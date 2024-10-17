# -*- coding: utf-8 -*-
import asyncio
from typing import Annotated, List
from fastapi import APIRouter, Depends, Request
from fastapi_limiter.depends import RateLimiter

from app.decorators import router_request
from app.dependencies import assert_user_is_active, assert_cpf_is_valid
from app.models import User
from app.types.frontend import (
    PatientHeader,
    PatientSummary,
    Encounter,
    UserInfo,
)
from app.utils import read_bq, validate_user_access_to_patient_data
from app.config import (
    BIGQUERY_PROJECT,
    BIGQUERY_PATIENT_HEADER_TABLE_ID,
    BIGQUERY_PATIENT_SUMMARY_TABLE_ID,
    BIGQUERY_PATIENT_ENCOUNTERS_TABLE_ID,
    REQUEST_LIMIT_MAX,
    REQUEST_LIMIT_WINDOW_SIZE,
)
from app.types.errors import (
    AccessErrorModel
)

router = APIRouter(prefix="/frontend", tags=["Frontend Application"])


@router.get("/user")
async def get_user_info(
    user: Annotated[User, Depends(assert_user_is_active)],
) -> UserInfo:

    if user.cpf:
        cpf = user.cpf
        cpf = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    else:
        cpf = None

    return {
        "name": user.name,
        "role": user.role.job_title if user.role else None,
        "email": user.email,
        "username": user.username,
        "cpf": cpf,
    }


@router_request(
    method="GET",
    router=router,
    path="/patient/header/{cpf}",
    response_model=PatientHeader,
    responses={
        404: {"model": AccessErrorModel},
        403: {"model": AccessErrorModel}
    },
    dependencies=[Depends(RateLimiter(times=REQUEST_LIMIT_MAX, seconds=REQUEST_LIMIT_WINDOW_SIZE))]
)
async def get_patient_header(
    user: Annotated[User, Depends(assert_user_is_active)],
    cpf: Annotated[str, Depends(assert_cpf_is_valid)],
    request: Request,
) -> PatientHeader:

    validation_job = validate_user_access_to_patient_data(user, cpf)
    results_job = read_bq(
        f"""
        SELECT *
        FROM `{BIGQUERY_PROJECT}`.{BIGQUERY_PATIENT_HEADER_TABLE_ID}
        WHERE
            cpf_particao = {cpf}
        """,
        from_file="/tmp/credentials.json",
    )

    validation, results = await asyncio.gather(validation_job, results_job)

    has_access, response = validation
    if has_access:
        return results[0]
    else:
        return response


@router_request(
    method="GET",
    router=router,
    path="/patient/summary/{cpf}",
    response_model=PatientSummary,
    dependencies=[Depends(RateLimiter(times=REQUEST_LIMIT_MAX, seconds=REQUEST_LIMIT_WINDOW_SIZE))]
)
async def get_patient_summary(
    user: Annotated[User, Depends(assert_user_is_active)],
    cpf: Annotated[str, Depends(assert_cpf_is_valid)],
    request: Request,
) -> PatientSummary:

    validation_job = validate_user_access_to_patient_data(user, cpf)

    results_job = read_bq(
        f"""
        SELECT *
        FROM `{BIGQUERY_PROJECT}`.{BIGQUERY_PATIENT_SUMMARY_TABLE_ID}
        WHERE cpf_particao = {cpf}
        """,
        from_file="/tmp/credentials.json",
    )
    validation, results = await asyncio.gather(validation_job, results_job)

    has_access, _ = validation
    if has_access:
        return results[0]
    else:
        return PatientSummary(allergies=[], continuous_use_medications=[])


@router_request(
    method="GET",
    router=router,
    path="/patient/encounters/{cpf}",
    response_model=List[Encounter],
    dependencies=[Depends(RateLimiter(times=REQUEST_LIMIT_MAX, seconds=REQUEST_LIMIT_WINDOW_SIZE))]
)
async def get_patient_encounters(
    user: Annotated[User, Depends(assert_user_is_active)],
    cpf: Annotated[str, Depends(assert_cpf_is_valid)],
    request: Request,
) -> List[Encounter]:

    validation_job = validate_user_access_to_patient_data(user, cpf)

    results_job = read_bq(
        f"""
        SELECT *
        FROM `{BIGQUERY_PROJECT}`.{BIGQUERY_PATIENT_ENCOUNTERS_TABLE_ID}
        WHERE cpf_particao = {cpf} and exibicao.indicador = true
        """,
        from_file="/tmp/credentials.json",
    )
    validation, results = await asyncio.gather(validation_job, results_job)

    has_access, _ = validation
    if has_access:
        return results
    else:
        return []


@router.get("/patient/filter_tags")
async def get_filter_tags(_: Annotated[User, Depends(assert_user_is_active)]) -> List[str]:
    return [
        "CF/CMS",
        "HOSPITAL",
        "CENTRO SAUDE ESCOLA",
        "UPA",
        "CCO",
        "MATERNIDADE",
        "CER",
        "POLICLINICA",
    ]


@router.get("/metadata")
async def get_metadata(_: Annotated[User, Depends(assert_user_is_active)]) -> dict:
    return {
        "filter_tags": [
            {"tag": "CF/CMS", "description": "CF e CMS"},
            {"tag": "HOSPITAL", "description": "Hospital"},
            {"tag": "CENTRO SAUDE ESCOLA", "description": "Centro Saúde Escola"},
            {"tag": "UPA", "description": "UPA"},
            {"tag": "CCO", "description": "CCO"},
            {"tag": "MATERNIDADE", "description": "Maternidade"},
            {"tag": "CER", "description": "CER"},
            {"tag": "POLICLINICA", "description": "Policlínica"},
        ]
    }
