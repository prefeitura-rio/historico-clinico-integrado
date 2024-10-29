# -*- coding: utf-8 -*-
from pydantic import BaseModel

from app.enums import (
    LoginErrorEnum,
    AccessErrorEnum,
    AcceptTermsEnum
)


class AuthenticationErrorModel(BaseModel):
    message: str
    type: LoginErrorEnum


class AccessErrorModel(BaseModel):
    message: str
    type: AccessErrorEnum


class TermAcceptanceErrorModel(BaseModel):
    message: str
    type: AcceptTermsEnum
