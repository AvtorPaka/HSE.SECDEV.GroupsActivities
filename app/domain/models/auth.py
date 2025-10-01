from dataclasses import dataclass
from datetime import datetime

from app.domain.models.user import UserModel


@dataclass
class UserLoginModel:
    email: str
    password: str


@dataclass
class UserRegisterModel:
    username: str
    email: str
    password: str


@dataclass
class SessionModel:
    id: str
    user_id: int
    expiration_date: datetime


@dataclass
class SetCookieModel:
    user: UserModel
    session: SessionModel
