from dataclasses import dataclass


@dataclass
class UserModel:
    id: int
    email: str
    username: str
    password_hashed: str


@dataclass
class ChangeUserPasswordModel:
    user: UserModel
    new_password: str
    current_password: str


@dataclass
class ChangeUserEmailModel:
    user: UserModel
    provided_password: str
    new_email: str
