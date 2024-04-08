# -*- coding: utf-8 -*-
import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import ValidationError, DoesNotExist

from app.dependencies import get_current_active_user
from app.pydantic_models import (
    PatientMergeableRecord, StandardizedPatientRecordModel, StandardizedPatientConditionModel,
    BulkInsertOutputModel, MergeableRecord
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

@router.get("/patientrecords/updated")
async def get_updated_patientrecords(
    _           : Annotated[User, Depends(get_current_active_user)],
    start_datetime: datetime.datetime = datetime.datetime.now() - datetime.timedelta(hours=1),
    end_datetime: datetime.datetime = datetime.datetime.now()
) -> list[ str ]:
    updated_patients = await StandardizedPatientRecord.raw(f"""
    select std.patient_code
    from std__patientrecord std
        left join patient on patient.patient_code = std.patient_code
    where
        std.created_at between '{start_datetime}' and '{end_datetime}'
        and ((patient.id is null) or (patient.updated_at < std.created_at))
    """)

    updated_patientcodes = [patient.patient_code for patient in updated_patients]
    return updated_patientcodes

@router.get("/patientrecords/{patient_code}")
async def get_standardized_patientrecords(
    _           : Annotated[User, Depends(get_current_active_user)],
    patient_code: str,
) -> PatientMergeableRecord[StandardizedPatientRecordModel]:

    # Get All STD Records for the Patient
    records = await StandardizedPatientRecord.filter(
        patient_code=patient_code,
    ).prefetch_related('raw_source__data_source')

    # Format Records to MergeableRecord
    mergeable_records = []
    for record in records:
        mergeable_records.append(
            MergeableRecord(
                standardized_record = record,
                source              = record.raw_source.data_source,
                event_moment        = record.raw_source.source_updated_at,
                ingestion_moment    = record.raw_source.updated_at,
            )
        )

    return PatientMergeableRecord(
        patient_code        = patient_code,
        mergeable_records   = mergeable_records
    )

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
        except KeyError:
            return HTMLResponse(
                status_code=400,
                content="raw_source_id Field Must be Informed"
            )

        record_cpf = record['patient_cpf']
        source_cpf = raw_source.patient_cpf
        if record_cpf != source_cpf:
            return HTMLResponse(
                status_code=400,
                content=f"Raw Source: CPF mismatch {source_cpf} != {record_cpf}"
            )

        if 'birth_city_cod' in record:
            try:
                birth_city = await City.get(
                    code=record['birth_city_cod']
                ).prefetch_related('state__country')
            except DoesNotExist as e:
                return HTMLResponse(status_code=404, content=f"Birth City: {e}")

            record['birth_city']    = birth_city
            record['birth_state']   = birth_city.state
            record['birth_country'] = birth_city.state.country

        record['raw_source'] = raw_source

        try:
            records_to_create.append( StandardizedPatientRecord(**record) )
        except ValidationError as e:
            return HTMLResponse(status_code=400, content=str(e))
        except ValueError as e:
            return HTMLResponse(status_code=400, content=str(e))

        await RawPatientRecord.filter(id=record['raw_source_id']).update(is_valid=True)

    new_records = await StandardizedPatientRecord.bulk_create(records_to_create)

    return {
        "cns_list": [],
        "address_list": [],
        "telecom_list": [],
        'count': len(new_records)
    }


@router.get("/patientconditions")
async def get_standardized_patientconditions(
    _           : Annotated[User, Depends(get_current_active_user)],
    patient_cpf : str,
) -> list[ MergeableRecord[StandardizedPatientConditionModel] ]:

    conditions = await StandardizedPatientCondition.filter(
        patient_cpf=patient_cpf
    ).prefetch_related('raw_source__data_source')

    results = []
    for condition in conditions:
        result = MergeableRecord(
            patient_code        = condition.patient_code,
            standardized_record = condition,
            source              = condition.raw_source.data_source,
            event_moment        = condition.raw_source.source_updated_at,
            ingestion_moment    = condition.raw_source.updated_at
        )
        results.append( result )

    return results


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
        except KeyError:
            return HTMLResponse(
                status_code=400,
                content="raw_source_id Field Must be Informed"
            )

        condition_cpf = condition['patient_cpf']
        source_cpf = raw_source.patient_cpf
        if condition_cpf != source_cpf:
            return HTMLResponse(
                status_code=400,
                content=f"Raw Source: CPF mismatch {source_cpf} != {condition_cpf}"
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
        except ValueError as e:
            return HTMLResponse(status_code=400, content=str(e))

        await RawPatientCondition.filter(id=condition['raw_source_id']).update(is_valid=True)

    new_conditions = await StandardizedPatientCondition.bulk_create(conditions_to_create)

    return {
        'count': len(new_conditions)
    }
