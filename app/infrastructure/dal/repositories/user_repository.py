import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.infrastructure import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
)
from app.infrastructure.dal.entities.models import User, UserSession
from app.infrastructure.dal.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    def _handle_email_constraint(self, ex: IntegrityError, email: str):
        if "users_email_key" in str(ex.orig).lower():
            raise EntityAlreadyExistsException(f"Пользователь с email {email} уже существует.")
        raise

    async def add_user_credentials(self, entity: User) -> int:
        try:
            self.db.add(entity)
            await self.db.flush()
            await self.db.refresh(entity)
            return entity.id
        except IntegrityError as ex:
            await self.db.rollback()
            self._handle_email_constraint(ex, entity.email)

    async def get_user_by_email(self, user_email: str) -> User:
        stmt = sa.select(User).where(User.email == user_email)
        result = await self.db.execute(stmt)
        entity = result.scalar_one_or_none()

        if not entity:
            raise EntityNotFoundException(f"Пользователь с email {user_email} не найден.")
        return entity

    async def get_user_by_session_id(self, session_id: str, cur_time) -> User:
        stmt = (
            sa.select(User)
            .join(UserSession, User.id == UserSession.user_id)
            .where(UserSession.id == session_id, UserSession.expiration_date >= cur_time)
        )
        result = await self.db.execute(stmt)
        user_entity = result.scalar_one_or_none()

        if not user_entity:
            raise EntityNotFoundException(
                f"Пользователь для сессии {session_id} не найден или сессия истекла."
            )
        return user_entity

    async def get_user_by_id(self, user_id: int) -> User:
        user_entity = await self.db.get(User, user_id)

        if not user_entity:
            raise EntityNotFoundException(f"Пользователь с ID {user_id} не найден.")
        return user_entity

    async def update_user_email(self, user_id: int, new_email: str) -> None:
        try:
            stmt = sa.update(User).where(User.id == user_id).values(email=new_email)
            result = await self.db.execute(stmt)

            if result.rowcount == 0:
                raise EntityNotFoundException(
                    f"Пользователь с ID {user_id} для обновления не найден."
                )

            await self.db.flush()
        except IntegrityError as ex:
            await self.db.rollback()
            self._handle_email_constraint(ex, new_email)

    async def update_user_password(self, user_id: int, new_hashed_password: str) -> None:
        stmt = sa.update(User).where(User.id == user_id).values(password_hashed=new_hashed_password)
        result = await self.db.execute(stmt)

        if result.rowcount == 0:
            raise EntityNotFoundException(f"Пользователь с ID {user_id} для обновления не найден.")
        await self.db.flush()

    async def update_user_username(self, user_id: int, new_username: str) -> None:
        stmt = sa.update(User).where(User.id == user_id).values(username=new_username)
        result = await self.db.execute(stmt)

        if result.rowcount == 0:
            raise EntityNotFoundException(f"Пользователь с ID {user_id} для обновления не найден.")
        await self.db.flush()

    async def delete_user(self, user_id: int) -> None:
        stmt = sa.delete(User).where(User.id == user_id)
        await self.db.execute(stmt)
        await self.db.flush()
