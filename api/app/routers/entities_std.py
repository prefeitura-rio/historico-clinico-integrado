# -*- coding: utf-8 -*-
from typing import Annotated, Optional, List

from fastapi import APIRouter, Depends
from tortoise.contrib.pydantic import pydantic_model_creator

from app.dependencies import get_current_active_user
from app.pydantic_models import (
    StandardizedPatientRecordModel, StandardizedPatientConditionModel,
    BulkInsertOutputModel, StandardizedPatientRecordListModel, StandardizedPatientConditionListModel
)
from app.models import (
    User, StandardizedPatientCondition, StandardizedPatientRecord,
    RawPatientCondition, RawPatientRecord
)

StandardizedPatientRecordOutput = pydantic_model_creator(
    StandardizedPatientRecord, name="StandardizedPatientRecordOutput"
)
StandardizedPatientConditionOutput = pydantic_model_creator(
    StandardizedPatientCondition, name="StandardizedPatientConditionOutput"
)


router = APIRouter(prefix="/std", tags=["Entidades STD (Formato Standardized/Padronizado)"])


@router.get("/patientrecords", response_model=list[StandardizedPatientRecordOutput])
async def get_standardized_patientrecords(
    current_user: Annotated[User, Depends(get_current_active_user)],
    patient_cpf: Optional[str] = None,
) -> list[StandardizedPatientRecordOutput]:

    if patient_cpf is not None:
        queryset = StandardizedPatientRecord.filter(
            patient_cpf=patient_cpf
        )
    else:
        queryset = StandardizedPatientRecord.all()

    if not current_user.is_superuser:
        user_data_source = await current_user.data_source
        queryset.filter(raw_source__data_source=user_data_source)

    return await StandardizedPatientRecordOutput.from_queryset(queryset)


@router.post("/patientrecords", response_model=BulkInsertOutputModel,
             status_code=201)
async def create_standardized_patientrecords(
    _: Annotated[User, Depends(get_current_active_user)],
    records: list[StandardizedPatientRecordModel],
) -> BulkInsertOutputModel:
    records_to_create = []
    for record in records:
        record = record.dict(exclude_unset=True)

        raw_source = await RawPatientRecord.get(id=record['raw_source_id'])

        record['raw_source'] = raw_source

        records_to_create.append( StandardizedPatientRecord(**record) )

    new_records = await StandardizedPatientRecord.bulk_create(records_to_create)

    return {
        'count': len(new_records)
    }


@router.get("/patientconditions", response_model=list[StandardizedPatientConditionOutput])
async def get_standardized_patientconditions(
    current_user: Annotated[User, Depends(get_current_active_user)],
    patient_cpf: Optional[str] = None,
) -> list[StandardizedPatientConditionOutput]:

    if patient_cpf is not None:
        queryset = StandardizedPatientCondition.filter(
            patient_cpf=patient_cpf
        )
    else:
        queryset = StandardizedPatientCondition.all()

    if not current_user.is_superuser:
        user_data_source = await current_user.data_source
        queryset.filter(raw_source__data_source=user_data_source)

    return await StandardizedPatientConditionOutput.from_queryset(queryset)

@router.post("/patientconditions", response_model=BulkInsertOutputModel,
             status_code=201)
async def create_standardized_patientconditions(
    _: Annotated[User, Depends(get_current_active_user)],
    conditions: list[StandardizedPatientConditionModel],
) -> BulkInsertOutputModel:

    conditions_to_create = []
    for condition in conditions:
        condition = condition.dict(exclude_unset=True)

        raw_source = await RawPatientCondition.get(id=condition['raw_source_id'])

        condition['raw_source'] = raw_source

        conditions_to_create.append( StandardizedPatientCondition(**condition) )

    new_conditions = await StandardizedPatientCondition.bulk_create(conditions_to_create)

    return {
        'count': len(new_conditions)
    }