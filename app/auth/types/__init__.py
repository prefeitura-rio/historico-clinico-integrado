from pydantic import BaseModel

from app.enums import (
    LoginStatusEnum,
    AccessErrorEnum,
)


class AuthenticationErrorModel(BaseModel):
    message: str
    type: LoginStatusEnum


class AccessErrorModel(BaseModel):
    message: str
    type: AccessErrorEnum


class LoginForm(BaseModel):
    username: str
    password: str


class LoginFormWith2FA(BaseModel):
    username: str
    password: str
    code: str