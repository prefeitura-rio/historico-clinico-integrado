# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from tortoise.contrib.pydantic import pydantic_model_creator

from app.dependencies import get_current_active_user
from app.models import (
    User, DataSource, RawPatientRecord, RawPatientCondition
)

DataSourceInput = pydantic_model_creator(DataSource, name="DataSourceInput", exclude=("id",))
DataSourceOutput = pydantic_model_creator(DataSource, name="DataSourceOutput")

RawPatientConditionInput = pydantic_model_creator(RawPatientCondition, name="RawPatientConditionInput", exclude=("id","created_at","updated_at"))
RawPatientConditionOutput = pydantic_model_creator(RawPatientCondition, name="RawPatientConditionOutput")

RawPatientRecordInput = pydantic_model_creator(RawPatientRecord, name="RawPatientRecordInput", exclude=("id","created_at","updated_at"))
RawPatientRecordOutput = pydantic_model_creator(RawPatientRecord, name="RawPatientRecordOutput")

router = APIRouter(prefix="/entities", tags=["entities"])


@router.get("/data_source", response_model=list[DataSourceOutput])
async def get_address_types(
    _: Annotated[User, Depends(get_current_active_user)],
) -> list[DataSourceOutput]:
    return await DataSourceOutput.from_queryset(DataSource.all())

@router.post("/data_source", response_model=DataSourceOutput, status_code=201)
async def create_address_type(
    _: Annotated[User, Depends(get_current_active_user)],
    datasource: DataSourceInput,
) -> DataSourceOutput:
    try:
        datasource_instance = await DataSource.create(**datasource.dict(exclude_unset=True))
        return await DataSourceOutput.from_tortoise_orm(datasource_instance)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="ENUM field Data not Compatible",
        )


@router.get("/raw_patientrecord", response_model=list[RawPatientRecordOutput])
async def get_raw_patientrecord(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> list[RawPatientRecordOutput]:
    if not current_user.is_active:
        raise HTTPException(
            status_code=400,
            detail="User is no longer Active",
        )

    if current_user.is_superuser:
        return await RawPatientRecordOutput.from_queryset(RawPatientRecord.all())

    user_data_source = await current_user.data_source
    return await RawPatientRecordOutput.from_queryset(RawPatientRecord.filter(
        data_source=user_data_source
    ))


@router.post("/raw_patientrecord", response_model=RawPatientRecordOutput, status_code=201)
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