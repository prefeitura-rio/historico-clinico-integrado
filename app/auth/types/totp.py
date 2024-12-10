# -*- coding: utf-8 -*-
from pydantic import BaseModel


class User2FA(BaseModel):
    id: int
    username: str
    is_2fa_required: bool
    is_2fa_activated: bool


class Enable2FA(BaseModel):
    secret_key: str
