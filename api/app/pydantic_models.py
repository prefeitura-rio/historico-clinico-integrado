# -*- coding: utf-8 -*-
from datetime import date, datetime

from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator


class PeriodModel(BaseModel):
    start: datetime
    end: datetime | None = None


class AddressModel(BaseModel):
    use: str | None = None
    type: str | None = None
    line: str
    city: str
    state: str
    postal_code: str | None = None
    period: PeriodModel | None = None


class TelecomModel(BaseModel):
    system: str | None = None
    use: str | None = None
    value: str
    rank: int | None = None
    period: PeriodModel | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class PatientModel(BaseModel):
    active: bool | None = True
    address: list[AddressModel] | None = None
    birth_city: str | None = None
    birth_state: str | None = None
    birth_country: str | None = None
    birth_date: date
    cpf: str
    cns: str | None = None
    data_source_name: str | None = None
    deceased: bool | None = False
    ethnicity: str | None = None
    father: str | None = None
    gender: str
    mother: str | None = None
    name: str
    nationality: str | None = None
    naturalization: str | None = None
    protected_person: bool | None = None
    race: str | None = None
    telecom: list[TelecomModel] | None = None
