# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from tortoise.contrib.pydantic import pydantic_model_creator

from app.dependencies import get_current_active_user
from app.pydantic_models import StandardizedPatientRecordModel, StandardizedPatientConditionModel
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


@router.post("/patientrecord", response_model=StandardizedPatientRecordOutput,
             status_code=201)
async def create_standardized_patientrecord(
    _: Annotated[User, Depends(get_current_active_user)],
    record: StandardizedPatientRecordModel,
) -> StandardizedPatientRecordOutput:

    raw_source = await RawPatientRecord.get(id=record.raw_source_id)

    input_dict = record.dict(exclude_unset=True)
    input_dict['raw_source'] = raw_source

    record_instance = await StandardizedPatientRecord.create(**input_dict)
    return await StandardizedPatientRecordOutput.from_tortoise_orm(record_instance)


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

@router.post("/patientcondition", response_model=StandardizedPatientConditionOutput,
             status_code=201)
async def create_standardized_patientcondition(
    _: Annotated[User, Depends(get_current_active_user)],
    condition: StandardizedPatientConditionModel,
) -> StandardizedPatientConditionOutput:

    raw_source = await RawPatientCondition.get(id=condition.raw_source_id)

    input_dict = condition.dict(exclude_unset=True)
    input_dict['raw_source'] = raw_source

    condition_instance = await StandardizedPatientCondition.create(**input_dict)
    return await StandardizedPatientConditionOutput.from_tortoise_orm(condition_instance)