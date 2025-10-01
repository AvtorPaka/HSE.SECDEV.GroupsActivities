from typing import Optional

from pydantic import BaseModel


class UserChangePasswordRequest(BaseModel):
    current_password: Optional[str] = None
    new_password: Optional[str] = None


class UserChangePasswordResponse(BaseModel):
    pass


class UserChangeEmailRequest(BaseModel):
    password: Optional[str] = None
    new_email: Optional[str] = None


class UserChangeEmailResponse(BaseModel):
    pass
