# -*- coding: utf-8 -*-
import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from tortoise.contrib.pydantic import pydantic_model_creator

from app.dependencies import get_current_active_user
from app.models import (
    User, RawPatientRecord, RawPatientCondition, DataSource
)
from app.pydantic_models import ( RawDataListModel, BulkInsertOutputModel )

RawPatientConditionInput = pydantic_model_creator(
    RawPatientCondition, name="RawPatientConditionInput",
    exclude=("id","created_at","updated_at")
)
RawPatientConditionOutput = pydantic_model_creator(
    RawPatientCondition, name="RawPatientConditionOutput"
)

RawPatientRecordInput = pydantic_model_creator(
    RawPatientRecord, name="RawPatientRecordInput",
    exclude=("id","created_at","updated_at")
)
RawPatientRecordOutput = pydantic_model_creator(
    RawPatientRecord, name="RawPatientRecordOutput"
)


router = APIRouter(prefix="/raw", tags=["Entidades RAW (Formato Raw/Bruto)"])


@router.get("/patientrecords", response_model=list[RawPatientRecordOutput])
async def get_raw_patientrecords(
    current_user: Annotated[User, Depends(get_current_active_user)],
    start_date: datetime.date = datetime.date.today(),
    end_date: datetime.date = datetime.date.today() + datetime.timedelta(days=1),
    datasource_system: str = None,
) -> list[RawPatientRecordOutput]:

    filtered = RawPatientRecord.filter(
        created_at__gte=start_date,
        created_at__lt=end_date
    )

    if datasource_system is not None:
        filtered = filtered.filter(
            data_source__system=datasource_system
        )
    return await RawPatientRecordOutput.from_queryset(filtered)


@router.post("/patientrecords", response_model=BulkInsertOutputModel, status_code=201)
async def create_raw_patientrecords(
    current_user: Annotated[User, Depends(get_current_active_user)],
    raw_data: RawDataListModel,
) -> BulkInsertOutputModel:
    raw_data = raw_data.dict()
    cnes = raw_data.pop("cnes")
    records = raw_data.pop("data_list")

    data_source = await DataSource.get(cnes=cnes)

    records_to_create = []
    for record in records:
        records_to_create.append(
            RawPatientRecord(
                patient_cpf     = record.get('patient_cpf'),
                data            = record.get('data'),
                data_source     = data_source
            )
        )

    new_records = await RawPatientRecord.bulk_create(records_to_create)
    return {
        'count': len(new_records)
    }


@router.get("/patientconditions", response_model=list[RawPatientConditionOutput])
async def get_raw_patientconditions(
    current_user: Annotated[User, Depends(get_current_active_user)],
    start_date: datetime.date = datetime.date.today(),
    end_date: datetime.date = datetime.date.today() + datetime.timedelta(days=1),
    datasource_system: str = None,
) -> list[RawPatientConditionOutput]:

    filtered = RawPatientCondition.filter(
        created_at__gte=start_date,
        created_at__lt=end_date
    )

    if datasource_system is not None:
        filtered = filtered.filter(
            data_source__system=datasource_system
        )
    return await RawPatientConditionOutput.from_queryset(filtered)


@router.post("/patientconditions", response_model=BulkInsertOutputModel, status_code=201)
async def create_raw_patientonditions(
    current_user: Annotated[User, Depends(get_current_active_user)],
    raw_data: RawDataListModel,
) -> BulkInsertOutputModel:
    raw_data = raw_data.dict()
    cnes = raw_data.pop("cnes")
    conditions = raw_data.pop("data_list")

    data_source = await DataSource.get(cnes=cnes)

    conditions_to_create = []
    for condition in conditions:
        conditions_to_create.append(
            RawPatientCondition(
                patient_cpf     = condition.get('patient_cpf'),
                data            = condition.get('data'),
                data_source     = data_source
            )
        )

    new_conditions = await RawPatientCondition.bulk_create(conditions_to_create)
    return {
        'count': len(new_conditions)
    }
