# -*- coding: utf-8 -*-
from datetime import date, datetime
from typing import Generic, Optional, List, TypeVar, Any
from pydantic import BaseModel


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


class RawDataModel(BaseModel):
    id: Optional[int]
    patient_cpf: str
    patient_code: str
    source_updated_at: datetime
    source_id: Optional[str]
    data: dict


class RawDataListModel(BaseModel):
    data_list: List[RawDataModel]
    cnes: str


class UploadToDatalakeStatusModel(BaseModel):
    success: bool
    message: Optional[str]


class BulkInsertOutputModel(BaseModel):
    count: int
    datalake_status: Optional[UploadToDatalakeStatusModel]

