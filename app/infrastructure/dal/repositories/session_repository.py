import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.infrastructure import EntityNotFoundException
from app.infrastructure.dal.entities.models import UserSession
from app.infrastructure.dal.repositories.base_repository import BaseRepository


class SessionRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_user_session(self, session_id: str) -> UserSession:
        stmt = sa.select(UserSession).where(UserSession.id == session_id)
        result = await self.db.execute(stmt)
        session_entity = result.scalar_one_or_none()

        if not session_entity:
            raise EntityNotFoundException(f"Сессия с ID {session_id} не найдена.")

        return session_entity

    async def create_user_session(self, entity: UserSession) -> None:
        try:
            self.db.add(entity)
            await self.db.flush()
            await self.db.refresh(entity)
        except IntegrityError as ex:
            await self.db.rollback()
            if "user_sessions_user_id_fkey" in str(ex.orig).lower():
                raise EntityNotFoundException(
                    f"Пользователь с ID {entity.user_id} для создания сессии не найден."
                )
            raise

    async def delete_user_session(self, session_id: str) -> None:
        stmt = sa.delete(UserSession).where(UserSession.id == session_id)
        await self.db.execute(stmt)

        await self.db.flush()

    async def delete_all_user_sessions(self, user_id: int) -> int:
        stmt = sa.delete(UserSession).where(UserSession.user_id == user_id)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount
