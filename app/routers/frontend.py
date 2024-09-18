# -*- coding: utf-8 -*-
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Request
from tortoise.exceptions import ValidationError
from fastapi_simple_rate_limiter import rate_limiter
from app.decorators import router_request
from app.dependencies import get_current_active_user
from app.models import User
from app.types.frontend import (
    PatientHeader,
    PatientSummary,
    Encounter,
    UserInfo,
)
from app.utils import read_bq
from app.validators import CPFValidator
from app.config import (
    BIGQUERY_PROJECT,
    BIGQUERY_PATIENT_HEADER_TABLE_ID,
    BIGQUERY_PATIENT_SUMMARY_TABLE_ID,
    BIGQUERY_PATIENT_ENCOUNTERS_TABLE_ID,
)

router = APIRouter(prefix="/frontend", tags=["Frontend Application"])


@router.get("/user")
async def get_user_info(
    user: Annotated[User, Depends(get_current_active_user)],
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


@router_request(method="GET", router=router, path="/patient/header/{cpf}")
@rate_limiter(limit=5, seconds=60)
async def get_patient_header(
    user: Annotated[User, Depends(get_current_active_user)],
    cpf: str,
    request: Request,
) -> PatientHeader:
    validator = CPFValidator()
    try:
        validator(cpf)
    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid CPF")

    results = await read_bq(
        f"""
        SELECT *
        FROM `{BIGQUERY_PROJECT}`.{BIGQUERY_PATIENT_HEADER_TABLE_ID}
        WHERE cpf_particao = {cpf}
        """,
        from_file="/tmp/credentials.json",
    )

    if len(results) == 0:
        raise HTTPException(status_code=404, detail="Patient not found")

    dados = results[0]
    configuracao_exibicao = dados.get("exibicao", {})

    if configuracao_exibicao.get("indicador", False) is False:
        message = ",".join(configuracao_exibicao.get("motivos", []))
        raise HTTPException(status_code=403, detail=message)

    return dados


@router_request(method="GET", router=router, path="/patient/summary/{cpf}")
@rate_limiter(limit=5, seconds=60)
async def get_patient_summary(
    user: Annotated[User, Depends(get_current_active_user)],
    cpf: str,
    request: Request,
) -> PatientSummary:

    results = await read_bq(
        f"""
        SELECT *
        FROM `{BIGQUERY_PROJECT}`.{BIGQUERY_PATIENT_SUMMARY_TABLE_ID}
        WHERE cpf_particao = {cpf}
        """,
        from_file="/tmp/credentials.json",
    )
    if len(results) == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        return results[0]


@router.get("/patient/filter_tags")
async def get_filter_tags(_: Annotated[User, Depends(get_current_active_user)]) -> List[str]:
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


@router_request(method="GET", router=router, path="/patient/encounters/{cpf}")
@rate_limiter(limit=5, seconds=60)
async def get_patient_encounters(
    user: Annotated[User, Depends(get_current_active_user)],
    cpf: str,
    request: Request,
) -> List[Encounter]:

    results = await read_bq(
        f"""
        SELECT *
        FROM `{BIGQUERY_PROJECT}`.{BIGQUERY_PATIENT_ENCOUNTERS_TABLE_ID}
        WHERE cpf_particao = {cpf} and exibicao.indicador = true
        """,
        from_file="/tmp/credentials.json",
    )
    return results
