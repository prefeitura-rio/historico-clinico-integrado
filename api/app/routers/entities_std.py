# -*- coding: utf-8 -*-
from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import ValidationError, DoesNotExist

from app.dependencies import get_current_active_user
from app.pydantic_models import (
    StandardizedPatientRecordModel, StandardizedPatientConditionModel,
    BulkInsertOutputModel
)
from app.models import (
    User, StandardizedPatientCondition, StandardizedPatientRecord,
    RawPatientCondition, RawPatientRecord, City, ConditionCode
)


router = APIRouter(prefix="/std", tags=["Entidades STD (Formato Standardized/Padronizado)"])


StandardizedPatientRecordOutput = pydantic_model_creator(
    StandardizedPatientRecord, name="StandardizedPatientRecordOutput"
)
StandardizedPatientConditionOutput = pydantic_model_creator(
    StandardizedPatientCondition, name="StandardizedPatientConditionOutput"
)


@router.get("/patientrecords")
async def get_standardized_patientrecords(
    _           : Annotated[User, Depends(get_current_active_user)],
    patient_cpf : Optional[str] = None,
) -> list[StandardizedPatientRecordOutput]:

    queryset = StandardizedPatientRecord.filter(
        patient_cpf=patient_cpf
    )

    return await StandardizedPatientRecordOutput.from_queryset(queryset)


@router.post("/patientrecords", status_code=201)
async def create_standardized_patientrecords(
    _           : Annotated[User, Depends(get_current_active_user)],
    records     : list[StandardizedPatientRecordModel],
) -> BulkInsertOutputModel:

    records_to_create = []
    for record in records:
        record = record.dict(exclude_unset=True)

        try:
            raw_source = await RawPatientRecord.get(id=record['raw_source_id'])
        except DoesNotExist as e:
            return HTMLResponse(
                status_code=404, 
                content=f"Raw Source {record['raw_source_id']}: {e}"
            )
        
        if raw_source.patient_cpf != record['patient_cpf']:
            return HTMLResponse(
                status_code=400, 
                content=f"Raw Source: CPF mismatch {raw_source.patient_cpf} != {record['patient_cpf']}"
            )
        
        try:
            birth_city = await City.get(
                code=record['birth_city_cod']
            ).prefetch_related('state__country')
        except DoesNotExist as e:
            return HTMLResponse(status_code=404, content=f"Birth City: {e}")
        
        if birth_city.state.code != record['birth_state_cod']:
            return HTMLResponse(
                status_code=400, 
                content="Birth State is not compatible with Birth City"
            )
        
        if birth_city.state.country.code != record['birth_country_cod']:
            return HTMLResponse(
                status_code=400, 
                content="Birth Country is not compatible with Birth City"
            )

        record['raw_source']    = raw_source
        record['birth_city']    = birth_city
        record['birth_state']   = birth_city.state
        record['birth_country'] = birth_city.state.country

        try:
            records_to_create.append( StandardizedPatientRecord(**record) )
        except ValidationError as e:
            return HTMLResponse(status_code=400, content=str(e))

    new_records = await StandardizedPatientRecord.bulk_create(records_to_create)

    return {
        'count': len(new_records)
    }


@router.get("/patientconditions")
async def get_standardized_patientconditions(
    _           : Annotated[User, Depends(get_current_active_user)],
    patient_cpf : str,
) -> list[StandardizedPatientConditionOutput]:

    queryset = StandardizedPatientCondition.filter(
        patient_cpf=patient_cpf
    )

    return await StandardizedPatientConditionOutput.from_queryset(queryset)


@router.post("/patientconditions", status_code=201)
async def create_standardized_patientconditions(
    _           : Annotated[User, Depends(get_current_active_user)],
    conditions  : list[StandardizedPatientConditionModel],
) -> BulkInsertOutputModel:

    conditions_to_create = []
    for condition in conditions:
        condition = condition.dict(exclude_unset=True)

        try:
            raw_source = await RawPatientCondition.get(id=condition['raw_source_id'])
        except DoesNotExist as e:
            return HTMLResponse(
                status_code=404, 
                content=f"Raw Source {condition['raw_source_id']}: {e}"
            )
        
        if raw_source.patient_cpf != condition['patient_cpf']:
            return HTMLResponse(
                status_code=400, 
                content=f"Raw Source: CPF mismatch {raw_source.patient_cpf} != {condition['patient_cpf']}"
            )
        
        condition['raw_source'] = raw_source

        code = condition['cid'] if condition['cid'] else condition['ciap']
        if not await ConditionCode.exists(value=code):
            return HTMLResponse(
                status_code=404, 
                content=f"Condition Code {code} not found"
            )

        try:
            conditions_to_create.append( StandardizedPatientCondition(**condition) )
        except ValidationError as e:
            return HTMLResponse(status_code=400, content=str(e))

    new_conditions = await StandardizedPatientCondition.bulk_create(conditions_to_create)

    return {
        'count': len(new_conditions)
    }
