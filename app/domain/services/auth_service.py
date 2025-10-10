from datetime import datetime, timedelta, timezone
from typing import Optional

from app.domain.exceptions.domain import (
    AuthUserNotFoundException,
    BadRequestException,
    InvalidUserCredentialsException,
    UserAlreadyExistsException,
    UserUnauthenticatedException,
)
from app.domain.exceptions.infrastructure import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
)
from app.domain.hasher.hasher import PasswordHasher
from app.domain.keygen.keygen import KeyGenerator
from app.domain.models.auth import SessionModel, SetCookieModel, UserLoginModel, UserRegisterModel
from app.domain.models.user import UserModel
from app.domain.validators.auth import UserLoginModelValidator, UserRegisterModelValidator
from app.infrastructure.dal.entities.models import User, UserSession
from app.infrastructure.dal.repositories.session_repository import SessionRepository
from app.infrastructure.dal.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository, sessions_repository: SessionRepository):
        self._user_repository = user_repository
        self._sessions_repository = sessions_repository

    async def register_new_user(self, model: UserRegisterModel):
        try:
            await self._register_new_user_unsafe(model)
        except BadRequestException:
            raise
        except EntityNotFoundException as ex:
            raise AuthUserNotFoundException(
                message="Invalid user credentials",
                invalid_email=model.email,
                inner_exception=ex,
            )
        except EntityAlreadyExistsException as ex:
            raise UserAlreadyExistsException(
                message="Check mail, if address is already in use",
                email=model.email,
                inner_exception=ex,
            )

    async def _register_new_user_unsafe(self, model: UserRegisterModel):
        validator = UserRegisterModelValidator()
        validator.validate(model)

        hashed_password = PasswordHasher.hash_password(model.password)

        user_entity = User(
            username=model.username,
            email=model.email,
            password_hashed=hashed_password,
        )

        async with self._user_repository.transaction():
            await self._user_repository.add_user_credentials(entity=user_entity)

    async def login_user(self, model: UserLoginModel) -> SetCookieModel:
        try:
            return await self._login_user_unsafe(model)
        except BadRequestException:
            raise
        except EntityNotFoundException as ex:
            raise AuthUserNotFoundException(
                message="Invalid credentials provided",
                invalid_email=model.email,
                inner_exception=ex,
            )

    async def _login_user_unsafe(self, login_model: UserLoginModel) -> SetCookieModel:
        validator = UserLoginModelValidator()
        validator.validate(login_model)

        async with self._sessions_repository.transaction():
            user_entity = await self._user_repository.get_user_by_email(
                user_email=login_model.email
            )

            if not PasswordHasher.verify_password(
                password=login_model.password, hashed_password=user_entity.password_hashed
            ):
                raise InvalidUserCredentialsException(
                    message="Invalid credentials provided",
                    email=login_model.email,
                    invalid_password=login_model.password,
                )

            session_id = KeyGenerator.generate_composite_key()
            expiration_date = datetime.now(timezone.utc) + timedelta(hours=3)

            session_entity = UserSession(
                id=session_id, user_id=user_entity.id, expiration_date=expiration_date
            )
            await self._sessions_repository.create_user_session(entity=session_entity)

            user_model = UserModel(
                id=user_entity.id,
                email=user_entity.email,
                username=user_entity.username,
                password_hashed=user_entity.password_hashed,
            )

            session_model = SessionModel(
                id=session_id, user_id=user_entity.id, expiration_date=expiration_date
            )

            return SetCookieModel(user=user_model, session=session_model)

    async def logout_user(self, session_id: str):
        async with self._sessions_repository.transaction():
            await self._sessions_repository.delete_user_session(session_id=session_id)

    async def user_check_auth(self, session_id: Optional[str]) -> UserModel:
        try:
            return await self._check_user_auth_unsafe(session_id)
        except EntityNotFoundException as ex:
            raise UserUnauthenticatedException(
                message="Invalid credentials.", reason="Invalid credentials.", inner_exception=ex
            )

    async def _check_user_auth_unsafe(self, session_id: Optional[str]) -> UserModel:
        if session_id is None:
            raise UserUnauthenticatedException(
                message="Invalid credentials.",
                reason="Authentication credentials were not provided.",
            )

        async with self._user_repository.transaction():
            user_entity = await self._user_repository.get_user_by_session_id(
                session_id=session_id, cur_time=datetime.now()
            )

            return user_entity
