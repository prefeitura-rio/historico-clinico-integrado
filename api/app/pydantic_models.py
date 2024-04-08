# -*- coding: utf-8 -*-
from datetime import date, datetime
from typing import Generic, Optional, List, TypeVar
from pydantic import BaseModel


class AddressModel(BaseModel):
    use: Optional[str]
    type: Optional[str]
    line: str
    city: str
    country: str
    state: str
    postal_code: Optional[str]
    start: Optional[date]
    end: Optional[date]


class TelecomModel(BaseModel):
    system: Optional[str]
    use: Optional[str]
    value: str
    rank: Optional[int]
    start: Optional[date]
    end: Optional[date]


class DataSourceModel(BaseModel):
    system: str
    cnes: str
    description: str


class UserRegisterInputModel(BaseModel):
    username: str
    password: str
    email: str
    is_superuser: bool
    data_source: DataSourceModel


class UserRegisterOutputModel(BaseModel):
    username: str
    is_superuser: bool
    data_source: DataSourceModel


class CnsModel(BaseModel):
    value: str
    is_main: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str]


class RawDataModelInput(BaseModel):
    patient_cpf: str
    patient_code: str
    source_updated_at: str
    data: dict


class RawDataListModelInput(BaseModel):
    data_list: List[RawDataModelInput]
    cnes: str


class BulkInsertOutputModel(BaseModel):
    count: int


class ConditionListModel(BaseModel):
    code: str
    clinical_status: Optional[str]
    category: Optional[str]
    date: datetime


class PatientConditionListModel(BaseModel):
    patient_cpf: str
    patient_code: str
    conditions: List[ConditionListModel]


class PatientModel(BaseModel):
    active: Optional[bool] = True
    birth_city: Optional[str]
    birth_state: Optional[str]
    birth_country: Optional[str]
    birth_date: date
    patient_cpf: str
    patient_code: str
    deceased: Optional[bool] = False
    deceased_date: Optional[date]
    father_name: Optional[str]
    gender: str
    mother_name: Optional[str]
    name: str
    nationality: Optional[str]
    protected_person: Optional[bool]
    race: Optional[str]
    cns_list: Optional[List[CnsModel]]
    telecom_list: Optional[List[TelecomModel]]
    address_list: Optional[List[AddressModel]]


class CompletePatientModel(BaseModel):
    birth_date: date
    patient_cpf: str
    patient_code: str
    gender: str
    name: str
    cns_list: List[CnsModel]
    telecom_list: List[TelecomModel]
    address_list: List[AddressModel]
    condition_list: List[ConditionListModel]
    active: Optional[bool] = True
    birth_city: Optional[str]
    birth_state: Optional[str]
    birth_country: Optional[str]
    deceased: Optional[bool] = False
    deceased_date: Optional[date]
    father_name: Optional[str]
    mother_name: Optional[str]
    nationality: Optional[str]
    protected_person: Optional[bool]
    race: Optional[str]


class StandardizedAddressModel(BaseModel):
    use: Optional[str]
    type: Optional[str]
    line: str
    city: str
    country: str
    state: str
    postal_code: Optional[str]
    start: Optional[str]
    end: Optional[str]


class StandardizedTelecomModel(BaseModel):
    system: Optional[str]
    use: Optional[str]
    value: str
    rank: Optional[int]
    start: Optional[str]
    end: Optional[str]


class StandardizedPatientRecordModel(BaseModel):
    active: Optional[bool] = True
    birth_city_cod: Optional[str]
    birth_state_cod: Optional[str]
    birth_country_cod: Optional[str]
    birth_date: date
    patient_cpf: str
    patient_code: str
    deceased: Optional[bool] = False
    deceased_date: Optional[date]
    father_name: Optional[str]
    gender: str
    mother_name: Optional[str]
    name: str
    nationality: Optional[str]
    protected_person: Optional[bool]
    race: Optional[str]
    cns_list: Optional[List[CnsModel]]
    address_list: Optional[List[StandardizedAddressModel]]
    telecom_list: Optional[List[StandardizedTelecomModel]]
    raw_source_id: str
    is_valid: Optional[bool]


class StandardizedPatientConditionModel(BaseModel):
    patient_cpf : str
    patient_code: str
    cid : str
    ciap: Optional[str]
    clinical_status: Optional[str]
    category: Optional[str]
    date: datetime
    raw_source_id: str
    is_valid: Optional[bool]


PatientData = TypeVar('PatientData', StandardizedPatientRecordModel, StandardizedPatientConditionModel)

class MergeableRecord(Generic[PatientData], BaseModel):
    standardized_record: PatientData
    source: DataSourceModel
    event_moment: datetime
    ingestion_moment: datetime


class PatientMergeableRecord(Generic[PatientData], BaseModel):
    patient_code: str
    mergeable_records: List[MergeableRecord[PatientData]]


class RecordListModel(Generic[PatientData], BaseModel):
    records: List[PatientData]

class StandardizedPatientRecordListModel(BaseModel):
    records: List[StandardizedPatientRecordModel]


class StandardizedPatientConditionListModel(BaseModel):
    conditions: List[StandardizedPatientConditionModel]