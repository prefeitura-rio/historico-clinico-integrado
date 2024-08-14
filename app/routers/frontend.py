# -*- coding: utf-8 -*-
import json
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from basedosdados import read_sql

from app.dependencies import get_current_active_user
from app.models import User
from app.types.frontend import (
    PatientHeader,
    PatientSummary,
    Encounter,
    UserInfo,
)
from app.config import BIGQUERY_PROJECT

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
        "email": user.email,
        "username": user.username,
        "cpf": cpf,
    }


@router.get("/patient/header/{cpf}")
async def get_patient_header(
    _: Annotated[User, Depends(get_current_active_user)],
    cpf: str,
) -> PatientHeader:
    results_json = read_sql(
        f"""
        SELECT *
        FROM `{BIGQUERY_PROJECT}`.`saude_dados_mestres`.`paciente`
        WHERE cpf = '{cpf}'
        """,
        from_file="/tmp/credentials.json",
    ).to_json(orient="records")

    results = json.loads(results_json)

    if len(results) > 0:
        patient_record = results[0]
    else:
        raise HTTPException(status_code=404, detail="Patient not found")

    data = patient_record["dados"][0]

    cns_principal = "?"
    if len(patient_record["cns"]) > 0:
        cns_principal = patient_record["cns"][0]["cns"]

    telefone_principal = "?"
    if len(patient_record["contato"]["telefone"]) > 0:
        telefone_principal = patient_record["contato"]["telefone"][0]["numero"]

    clinica_principal = {}
    if len(patient_record["clinica_familia"]) > 0:
        clinica_principal = patient_record["clinica_familia"][0]

    equipe_principal = {}
    if len(patient_record["equipe_saude_familia"]) > 0:
        equipe_principal = patient_record["equipe_saude_familia"][0]

    return {
        "registration_name": data.get("nome", "?"),
        "social_name": data.get("nome_social", "?"),
        "cpf": f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}",
        "cns": cns_principal,
        "birth_date": data.get("data_nascimento", "?"),
        "gender": data.get("genero", "?"),
        "race": data.get("raca", "?"),
        "phone": telefone_principal,
        "family_clinic": {
            "cnes": clinica_principal.get("id_cnes", "?"),
            "name": clinica_principal.get("nome", "?"),
            "phone": clinica_principal.get("telefone", "?"),
        },
        "family_health_team": {
            "ine_code": equipe_principal.get("id_ine", "?"),
            "name": equipe_principal.get("nome", "?"),
            "phone": equipe_principal.get("telefone", "?"),
        },
        "medical_responsible": [
            {"name": "Roberta dos Santos", "registry": "XXXXX"},
            {"name": "Lucas da Silva", "registry": "YYYYY"},
        ],
        "nursing_responsible": [{"name": "Pedro da Nobrega", "registry": "WWWWW"}],
        "validated": data.get("cadastro_validado_indicador"),
    }



@router.get("/patient/summary/{cpf}")
async def get_patient_summary(
    _: Annotated[User, Depends(get_current_active_user)],
    cpf: str,
) -> PatientSummary:

    if cpf == '19530236069':
        raise HTTPException(status_code=404, detail="Patient not found")
    elif cpf == '11111111111':
        raise HTTPException(status_code=400, detail="Invalid CPF")

    return {
        "allergies": [
            "Sulfonamidas",
            "Ácaros do pó",
            "Penicilina",
            "Medicamentos anticonvulsivantes",
            "Gatos",
            "Gramíneas",
            "Picadas de abelhas",
            "Picadas de vespas",
            "Preservativos",
            "Luvas de látex",
        ],
        "continuous_use_medications": [
            "Losartana potássica",
            "Enalapril maleato",
            "Besilato de anlodipino",
            "Captopril",
            "Clonazepam",
            "Enalapril",
        ],
    }


@router.get("/patient/encounters/{cpf}")
async def get_patient_encounters(
    _: Annotated[User, Depends(get_current_active_user)],
    cpf: str,
) -> List[Encounter]:

    if cpf == '19530236069':
        raise HTTPException(status_code=404, detail="Patient not found")
    elif cpf == '11111111111':
        raise HTTPException(status_code=400, detail="Invalid CPF")

    return [
        {
            "entry_datetime": "2023-09-05T10:00:00",
            "exit_datetime": "2023-09-05T12:00:00",
            "location": "UPA 24h Magalhães Bastos",
            "type": "Consulta",
            "subtype": "Marcada",
            "active_cids": ["A10.2", "B02.5"],
            "responsible": {"name": "Dr. João da Silva", "role": "Médico(a)"},
            "description": "Lorem ipsum dolor sit amet consectetur.",
            "filter_tags": ["UPA"],
        },
        {
            "entry_datetime": "2021-09-01T10:00:00",
            "exit_datetime": "2021-09-01T12:00:00",
            "location": "UPA 24h Magalhães Bastos",
            "type": "Consulta",
            "subtype": "Emergência",
            "active_cids": ["A10.2"],
            "responsible": {"name": "Dr. João da Silva", "role": "Médico(a)"},
            "description": (
                "Lorem ipsum dolor sit amet consectetur. Sed vel suscipit id pulvinar"
                "sed nam libero eu. Leo arcu sit lacus nisl nullam eget et dignissim sed."
                "Fames pretium cursus viverra posuere arcu tortor sit lectus congue. Velit"
                "tempor ultricies pulvinar magna pulvinar ridiculus consequat nibh..."
            ),
            "filter_tags": ["UPA"],
        },
        {
            "entry_datetime": "2021-08-21T22:00:00",
            "exit_datetime": "2021-08-22T02:50:00",
            "location": "CMS RAPHAEL DE PAULA SOUZA",
            "type": "Consulta",
            "subtype": "Pediatria",
            "active_cids": ["Z10.2"],
            "responsible": {"name": "Mariana Gomes", "role": "Enfermeiro(a)"},
            "description": (
                "Lorem ipsum dolor sit amet consectetur. Sed vel suscipit id pulvinar"
                "sed nam libero eu. Leo arcu sit lacus nisl nullam eget et dignissim sed."
            ),
            "filter_tags": ["CF/CMS"],
        },
        {
            "entry_datetime": "2021-05-11T12:00:00",
            "exit_datetime": "2021-05-12T20:50:00",
            "location": "Hospital Municipal Rocha Faria",
            "type": "Consulta",
            "subtype": "Cirurgia",
            "active_cids": ["E01.3"],
            "responsible": {"name": "Dra. Claudia Simas", "role": "Medico(a)"},
            "description": (
                "Lorem ipsum dolor sit amet consectetur. Sed vel suscipit id pulvinar."
            ),
            "filter_tags": ["Hospital"],
        }
    ]
