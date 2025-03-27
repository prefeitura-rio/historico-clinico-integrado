# -*- coding: utf-8 -*-
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    token_expire_minutes: int


class TokenData(BaseModel):
    username: Optional[str]
    name: Optional[str]
    email: Optional[str]
    cpf: Optional[str]
    access_level: Optional[str]
    job_title: Optional[str]
    cnes: Optional[str]
    ap: Optional[str]
