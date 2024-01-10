# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from tortoise.contrib.pydantic import pydantic_model_creator

from app.dependencies import get_current_active_user
from app.pydantic_models import StandardizedPatientRecordModel
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


@router.get("/patientrecord", response_model=list[StandardizedPatientRecordModel])
async def get_standardized_patientrecord(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> list[StandardizedPatientRecordModel]:
    if current_user.is_superuser:
        return await StandardizedPatientRecord.from_queryset(StandardizedPatientRecord.all())

    user_data_source = await current_user.data_source
    return await StandardizedPatientRecord.from_queryset(StandardizedPatientRecord.filter(
        data_source=user_data_source
    ))


@router.post("/patientrecord", response_model=StandardizedPatientRecordModel, status_code=201)
async def create_standardized_patientrecord(
    current_user: Annotated[User, Depends(get_current_active_user)],
    record: StandardizedPatientRecordModel,
) -> StandardizedPatientRecordModel:

    raw_source = await RawPatientRecord.get(id=record.raw_source_id)

    input_dict = record.dict(exclude_unset=True)
    input_dict['raw_source'] = raw_source

    record_instance = await StandardizedPatientRecord.create(**input_dict)
    return await StandardizedPatientRecordOutput.from_tortoise_orm(record_instance)
