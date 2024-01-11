# -*- coding: utf-8 -*-
from datetime import date, datetime

from pydantic import BaseModel
from typing import Union
from typing import Any, List


class AddressModel(BaseModel):
    use: str | None = None
    type: str | None = None
    line: str
    city: str
    country: str
    state: str
    postal_code: str | None = None
    period_start: date
    period_end: date | None = None


class TelecomModel(BaseModel):
    system: str | None = None
    use: str | None = None
    value: str
    rank: int | None = None
    period_start: date
    period_end: date | None = None


class StandardizedAddressModel(BaseModel):
    use: str | None = None
    type: str | None = None
    line: str
    city: str
    country: str
    state: str
    postal_code: str | None = None
    start: str
    end:str | None = None


class StandardizedTelecomModel(BaseModel):
    system: str | None = None
    use: str | None = None
    value: str
    rank: int | None = None
    start: str
    end:str | None = None


class CnsModel(BaseModel):
    value: str
    is_main: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

class ConditionListModel(BaseModel):
    code: str
    clinical_status: str
    category: str
    date: datetime

class PatientConditionListModel(BaseModel):
    patient_cpf: str
    conditions: List[ConditionListModel]

class PatientModel(BaseModel):
    active: bool | None = True
    birth_city: str | None = None
    birth_state: str | None = None
    birth_country: str | None = None
    birth_date: date
    patient_cpf: str
    deceased: bool | None = None
    deceased_date: date | None = None
    father: str | None = None
    gender: str
    mother: str | None = None
    name: str
    nationality: str | None = None
    naturalization: str | None = None
    protected_person: bool | None = None
    race: str | None = None
    cns_list: list[CnsModel] | None = None
    telecom_list: list[TelecomModel] | None = None
    address_list: list[AddressModel] | None = None

class CompletePatientModel(BaseModel):
    active: bool | None = True
    birth_city: str | None = None
    birth_state: str | None = None
    birth_country: str | None = None
    birth_date: date
    patient_cpf: str
    deceased: bool | None = None
    deceased_date: date | None = None
    father_name: str | None = None
    mother_name: str | None = None
    gender: str
    name: str
    nationality: str | None = None
    naturalization: str | None = None
    protected_person: bool | None = None
    race: str | None = None
    cns_list: list[CnsModel] | None = None
    telecom_list: list[TelecomModel] | None = None
    address_list: list[AddressModel] | None = None
    condition_list: list[ConditionListModel] | None = None


class StandardizedPatientRecordModel(BaseModel):
    active: bool | None = True
    birth_city: str | None = None
    birth_state: str | None = None
    birth_country: str | None = None
    birth_date: date
    patient_cpf: str
    deceased: bool | None = False
    deceased_date: date | None = False
    father_name: str | None = None
    gender: str
    mother_name: str | None = None
    name: str
    nationality: str | None = None
    naturalization: str | None = None
    protected_person: bool | None = None
    race: str | None = None
    cns_list: List[CnsModel] | None = None
    address_list: List[StandardizedAddressModel] | None = None
    telecom_list: List[StandardizedTelecomModel] | None = None
    raw_source_id: str | None = None


class StandardizedPatientConditionModel(BaseModel):
    patient_cpf : str
    cid : str
    ciap: str | None = None
    clinical_status: str
    category: str
    date: datetime
    raw_source_id: str | None = None