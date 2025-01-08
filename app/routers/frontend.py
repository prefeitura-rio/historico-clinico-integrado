# -*- coding: utf-8 -*-
import asyncio
import unicodedata
import datetime
from typing import Annotated, List
from fastapi import APIRouter, Depends, Request
from fastapi_limiter.depends import RateLimiter
from fastapi.responses import JSONResponse

from app.decorators import router_request
from app.dependencies import assert_user_is_active, assert_cpf_is_valid
from app.models import User
from app.types.frontend import (
    PatientHeader,
    PatientSummary,
    Encounter,
    UserInfo,
)
from app.types.errors import AcceptTermsEnum
from app.utils import read_bq, validate_user_access_to_patient_data
from app.config import (
    BIGQUERY_PROJECT,
    BIGQUERY_PATIENT_HEADER_TABLE_ID,
    BIGQUERY_PATIENT_SEARCH_TABLE_ID,
    BIGQUERY_PATIENT_SUMMARY_TABLE_ID,
    BIGQUERY_PATIENT_ENCOUNTERS_TABLE_ID,
    REQUEST_LIMIT_MAX,
    REQUEST_LIMIT_WINDOW_SIZE,
)
from app.types.errors import (
    TermAcceptanceErrorModel
)
from app.auth.types import AccessErrorModel
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
        "is_use_terms_accepted": user.is_use_terms_accepted,
        "cpf": cpf,
    }


@router_request(
    method="POST",
    router=router,
    path="/user/accept-terms/",
    response_model=TermAcceptanceErrorModel,
    responses={
        500: {"model": TermAcceptanceErrorModel},
    },
)
async def accept_use_terms(
    user: Annotated[User, Depends(assert_user_is_active)],
    request: Request,
) -> TermAcceptanceErrorModel:

    try:
        user.is_use_terms_accepted = True
        user.use_terms_accepted_at = datetime.datetime.now()
        await user.save()
        return JSONResponse(
            status_code=200,
            content={
                "message": "Success",
                "type": AcceptTermsEnum.SUCCESS,
            },
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "message": "Patient not found",
                "type": AcceptTermsEnum.FAILURE,
            },
        )


@router.get("/patient/search",
    response_model=List[dict],
    responses={
        404: {"model": AccessErrorModel},
        403: {"model": AccessErrorModel}
    },
)
async def search_patient(
    request: Request,
    user: Annotated[User, Depends(assert_user_is_active)],
    cpf: str = None,
    cns: str = None,
    name: str = None,
) -> List[dict]:
    
    filled_param_count = sum([bool(cpf), bool(cns), bool(name)])
    if filled_param_count == 0:
        return JSONResponse(
            status_code=400,
            content={"message": "One of the parameters is required"},
        )
    elif filled_param_count > 1:
        return JSONResponse(
            status_code=400,
            content={"message": "Only one of the parameters is allowed"},
        )

    clause = ""
    if cns:
        clause = f"cns_particao = {cns}"
    elif cpf:
        clause = f"cpf = '{cpf}'"
    elif name:
        name_cleaned = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c)
        clause = f"search(nome,'{name_cleaned}')"

    results = await read_bq(
        f"""
        SELECT *
        FROM `{BIGQUERY_PROJECT}`.{BIGQUERY_PATIENT_SEARCH_TABLE_ID}
        WHERE {clause}
        ORDER BY nome ASC
        """,
        from_file="/tmp/credentials.json",
    )

    return results

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
            {"tag": "CCO", "description": "Centro Carioca do Olho"},
            {"tag": "MATERNIDADE", "description": "Maternidade"},
            {"tag": "CER", "description": "CER"},
            {"tag": "POLICLINICA", "description": "Policlínica"},
        ]
    }
