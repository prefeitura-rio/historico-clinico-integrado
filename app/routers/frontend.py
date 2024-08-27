# -*- coding: utf-8 -*-
import json

from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from basedosdados import read_sql
from tortoise.exceptions import ValidationError

from app.dependencies import (
    get_current_frontend_user
)
from app.models import User
from app.types.frontend import (
    PatientHeader,
    PatientSummary,
    Encounter,
    UserInfo,
)
from app.validators import CPFValidator
from app.config import (
    BIGQUERY_PROJECT,
    BIGQUERY_PATIENT_HEADER_TABLE_ID,
    BIGQUERY_PATIENT_SUMMARY_TABLE_ID,
    BIGQUERY_PATIENT_ENCOUNTERS_TABLE_ID
)

router = APIRouter(prefix="/frontend", tags=["Frontend Application"])


@router.get("/user")
async def get_user_info(
    user: Annotated[User, Depends(get_current_frontend_user)],
) -> UserInfo:
    if user.cpf:
        cpf = user.cpf
        cpf = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    else:
        cpf = None

    return {
        "name": user.name,
        "role": user.role,
        "email": user.email,
        "username": user.username,
        "cpf": cpf,
    }


@router.get("/patient/header/{cpf}")
async def get_patient_header(
    _: Annotated[User, Depends(get_current_frontend_user)],
    cpf: str,
) -> PatientHeader:
    validator = CPFValidator()
    try:
        validator(cpf)
    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid CPF")

    results_json = read_sql(
        f"""
        SELECT *
        FROM `{BIGQUERY_PROJECT}`.{BIGQUERY_PATIENT_HEADER_TABLE_ID}
        WHERE cpf = '{cpf}'
        """,
        from_file="/tmp/credentials.json",
    ).to_json(orient="records")
    try:
        results = json.loads(results_json)
    except Exception:
        results = []

    if len(results) == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        return results[0]



@router.get("/patient/summary/{cpf}")
async def get_patient_summary(
    _: Annotated[User, Depends(get_current_frontend_user)],
    cpf: str,
) -> PatientSummary:

    results_json = read_sql(
        f"""
        SELECT *
        FROM `{BIGQUERY_PROJECT}`.{BIGQUERY_PATIENT_SUMMARY_TABLE_ID}
        WHERE cpf = '{cpf}'
        """,
        from_file="/tmp/credentials.json",
    ).to_json(orient="records")
    results = json.loads(results_json)
    if len(results) == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        return results[0]

@router.get("/patient/filter_tags")
async def get_filter_tags(
    _: Annotated[User, Depends(get_current_frontend_user)]
) -> List[str]:
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


@router.get("/patient/encounters/{cpf}")
async def get_patient_encounters(
    _: Annotated[User, Depends(get_current_frontend_user)],
    cpf: str,
) -> List[Encounter]:

    results_json = read_sql(
        f"""
        SELECT *
        FROM `{BIGQUERY_PROJECT}`.{BIGQUERY_PATIENT_ENCOUNTERS_TABLE_ID}
        WHERE cpf = '{cpf}'
        """,
        from_file="/tmp/credentials.json",
    ).to_json(orient="records")
    results = json.loads(results_json)
    return results
