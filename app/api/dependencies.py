from typing import Annotated

from fastapi import Depends, Request

from app.domain.models.user import UserModel
from app.domain.services.auth_service import AuthService
from app.domain.services.user_service import UserService
from app.infrastructure.dal.database import AsyncSession, get_async_db
from app.infrastructure.dal.repositories.session_repository import SessionRepository
from app.infrastructure.dal.repositories.user_repository import UserRepository

SESSION_COOKIE_KEY = "devsec-session-id"

DBSessionDep = Annotated[AsyncSession, Depends(get_async_db)]


def get_user_repository(db: DBSessionDep) -> UserRepository:
    return UserRepository(db)


def get_session_repository(db: DBSessionDep) -> SessionRepository:
    return SessionRepository(db)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    session_repo: SessionRepository = Depends(get_session_repository),
) -> AuthService:
    return AuthService(user_repo, session_repo)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    session_repo: SessionRepository = Depends(get_session_repository),
) -> UserService:
    return UserService(user_repo, session_repo)


async def get_current_user(
    request: Request, auth_service: AuthService = Depends(get_auth_service)
) -> UserModel:
    session_id = request.cookies.get(SESSION_COOKIE_KEY)
    return await auth_service.user_check_auth(session_id)
