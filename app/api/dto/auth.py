from typing import Optional

from pydantic import BaseModel


class UserRegisterRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserLoginRequest(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None


class UserRegisterResponse(BaseModel):
    pass


class UserLoginResponse(BaseModel):
    id: int
    email: str
    username: str


class UserCheckAuthResponse(BaseModel):
    id: int
    email: str
    username: str


class UserLogoutResponse(BaseModel):
    pass
