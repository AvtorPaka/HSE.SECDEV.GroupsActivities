from app.domain.exceptions.domain import (
    InvalidUserCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.domain.exceptions.infrastructure import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
)
from app.domain.hasher.hasher import PasswordHasher
from app.domain.models.user import ChangeUserEmailModel, ChangeUserPasswordModel
from app.domain.validators.user import ChangeUserEmailValidator, ChangeUserPasswordValidator
from app.infrastructure.dal.repositories.session_repository import SessionRepository
from app.infrastructure.dal.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository, session_repository: SessionRepository):
        self._user_repository = user_repository
        self._session_repository = session_repository

    async def change_user_password(self, model: ChangeUserPasswordModel):
        try:
            await self._change_user_password_unsafe(model)
        except EntityNotFoundException as ex:
            raise UserNotFoundException(
                message=f"Не удалось найти пользователя с id: {model.user.id}.",
                invalid_email=model.user.email,
                inner_exception=ex,
            )

    async def _change_user_password_unsafe(self, model: ChangeUserPasswordModel):
        validator = ChangeUserPasswordValidator()
        validator.validate(model)

        if not PasswordHasher.verify_password(
            password=model.current_password, hashed_password=model.user.password_hashed
        ):
            raise InvalidUserCredentialsException(
                message="Invalid credentials provided",
                email=model.user.email,
                invalid_password=model.current_password,
            )

        new_hashed_password = PasswordHasher.hash_password(model.new_password)

        async with self._user_repository.transaction():
            await self._user_repository.update_user_password(
                user_id=model.user.id, new_hashed_password=new_hashed_password
            )
            await self._session_repository.delete_all_user_sessions(user_id=model.user.id)

    async def change_user_email(self, model: ChangeUserEmailModel):
        try:
            await self._change_user_email_unsafe(model=model)
        except EntityNotFoundException as ex:
            raise UserNotFoundException(
                message=f"Не удалось найти пользователя с id: {model.user.id}.",
                invalid_email=model.user.email,
                inner_exception=ex,
            )
        except EntityAlreadyExistsException as ex:
            raise UserAlreadyExistsException(
                message="Check mail, if address is already in use",
                email=model.new_email,
                inner_exception=ex,
            )

    async def _change_user_email_unsafe(self, model: ChangeUserEmailModel):
        validator = ChangeUserEmailValidator()
        validator.validate(model)

        if not PasswordHasher.verify_password(
            password=model.provided_password, hashed_password=model.user.password_hashed
        ):
            raise InvalidUserCredentialsException(
                message="Invalid credentials provided",
                email=model.user.email,
                invalid_password=model.provided_password,
            )

        async with self._user_repository.transaction():
            await self._user_repository.update_user_email(
                user_id=model.user.id, new_email=model.new_email
            )
            await self._session_repository.delete_all_user_sessions(user_id=model.user.id)
