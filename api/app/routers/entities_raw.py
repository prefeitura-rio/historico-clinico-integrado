# -*- coding: utf-8 -*-
import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from tortoise.contrib.pydantic import pydantic_model_creator

from app.dependencies import get_current_active_user
from app.models import (
    User, RawPatientRecord, RawPatientCondition
)


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
) -> list[RawPatientRecordOutput]:
    if current_user.is_superuser:
        return await RawPatientRecordOutput.from_queryset(RawPatientRecord.filter(
            created_at__gte=start_date,
            created_at__lt=end_date
        ))

    user_data_source = await current_user.data_source
    return await RawPatientRecordOutput.from_queryset(RawPatientRecord.filter(
        data_source=user_data_source,
        created_at__gte=start_date,
        created_at__lt=end_date
    ))


@router.post("/patientrecord", response_model=RawPatientRecordOutput, status_code=201)
async def create_raw_patientrecord(
    current_user: Annotated[User, Depends(get_current_active_user)],
    record: RawPatientRecordInput,
) -> RawPatientRecordOutput:
    user_datasource = await current_user.data_source

    record_instance = await RawPatientRecord.create(
        patient_cpf     = record.patient_cpf,
        data            = record.data,
        data_source     = user_datasource
    )
    return await RawPatientRecordOutput.from_tortoise_orm(record_instance)


@router.get("/patientconditions", response_model=list[RawPatientConditionOutput])
async def get_raw_patientconditions(
    current_user: Annotated[User, Depends(get_current_active_user)],
    start_date: datetime.date = datetime.date.today(),
    end_date: datetime.date = datetime.date.today() + datetime.timedelta(days=1),
) -> list[RawPatientConditionOutput]:
    if current_user.is_superuser:
        return await RawPatientConditionOutput.from_queryset(RawPatientCondition.filter(
            created_at__gte=start_date,
            created_at__lt=end_date
        ))

    user_data_source = await current_user.data_source
    return await RawPatientConditionOutput.from_queryset(RawPatientCondition.filter(
        data_source=user_data_source,
        created_at__gte=start_date,
        created_at__lt=end_date
    ))


@router.post("/patientcondition", response_model=RawPatientConditionOutput, status_code=201)
async def create_raw_patientondition(
    current_user: Annotated[User, Depends(get_current_active_user)],
    condition: RawPatientConditionInput,
) -> RawPatientConditionOutput:
    user_datasource = await current_user.data_source

    condition_instance = await RawPatientCondition.create(
        patient_cpf     = condition.patient_cpf,
        data            = condition.data,
        data_source     = user_datasource
    )
    return await RawPatientConditionOutput.from_tortoise_orm(condition_instance)
