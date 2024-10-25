# -*- coding: utf-8 -*-
from pydantic import BaseModel

from app.enums import (
    LoginErrorEnum,
    AccessErrorEnum
)


class AuthenticationErrorModel(BaseModel):
    message: str
    type: LoginErrorEnum


class AccessErrorModel(BaseModel):
    message: str
    type: AccessErrorEnum