# -*- coding: utf-8 -*-
from typing import Annotated, List

from fastapi import APIRouter, Depends

from app.dependencies import get_current_active_user
from app.models import User
from app.types.frontend import (
    PatientHeader,
    PatientSummary,
    Encounter,
    UserInfo,
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
        "email": user.email,
        "username": user.username,
        "cpf": cpf,
    }


@router.get("/patient/header/{cpf}")
async def get_patient_header(
    _: Annotated[User, Depends(get_current_active_user)],
    cpf: str,
) -> PatientHeader:
    return {
        "registration_name": "José da Silva Xavier",
        "social_name": None,
        "cpf": f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}",
        "cns": "123456789012345",
        "birth_date": "1972-08-01",
        "gender": "masculino",
        "race": "parda",
        "phone": "(21) 99999-9999",
        "family_clinic": {"cnes": "1234567", "name": "Clinica da Familia XXX"},
        "family_health_team": {"ine_code": "1234567", "name": "Equipe Roxo"},
        "medical_responsible": "Roberta dos Santos",
        "nursing_responsible": "Pedro da Nobrega",
        "validated": True,
    }


@router.get("/patient/summary/{cpf}")
async def get_patient_summary(
    _: Annotated[User, Depends(get_current_active_user)],
    cpf: str,
) -> PatientSummary:
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
    return [
        {
            "entry_datetime": "2023-09-01T10:00:00",
            "exit_datetime": "2023-09-01T12:00:00",
            "location": "UPA 24h Magalhães Bastos",
            "type": "Consulta",
            "subtype": "Emergência",
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
                "Lorem ipsum dolor sit amet consectetur. Sed vel suscipit id pulvinar sed nam libero eu."
                "Leo arcu sit lacus nisl nullam eget et dignissim sed. Fames pretium cursus viverra "
                "posuere arcu tortor sit lectus congue. Velit tempor ultricies pulvinar magna pulvinar "
                "ridiculus consequat nibh..."
            ),
            "filter_tags": ["UPA", "Emergência"],
        },
    ]
