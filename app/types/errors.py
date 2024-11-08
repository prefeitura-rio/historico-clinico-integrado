# -*- coding: utf-8 -*-
from pydantic import BaseModel

from app.enums import (
    LoginStatusEnum,
    AccessErrorEnum,
    AcceptTermsEnum
)


class AuthenticationErrorModel(BaseModel):
    message: str
    type: LoginStatusEnum


class AccessErrorModel(BaseModel):
    message: str
    type: AccessErrorEnum


class TermAcceptanceErrorModel(BaseModel):
    message: str
    type: AcceptTermsEnum
