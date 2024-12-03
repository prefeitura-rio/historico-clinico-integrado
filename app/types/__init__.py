# -*- coding: utf-8 -*-
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    token_expire_minutes: int


class TokenData(BaseModel):
    username: Optional[str]