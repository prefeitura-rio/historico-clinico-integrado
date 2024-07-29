# -*- coding: utf-8 -*-
from typing import Annotated, List

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import ValidationError

from app.dependencies import get_current_active_user
from app.pydantic_models import (
    MergedPatient as PydanticMergedPatient,
)
from app.models import User


router = APIRouter(prefix="/frontend", tags=["Endpoints para consumo da aplicação Frontend"])


@router.get("/user")
async def get_patient_header(
    user: Annotated[User, Depends(get_current_active_user)],
) -> dict:
    cpf = user.cpf

    return {
        "nome": user.name,
        "email": user.email,
        "CPF": f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}",
    }


@router.get("/patient/header/{cpf}")
async def get_patient_header(
    _: Annotated[User, Depends(get_current_active_user)],
    cpf: int,
) -> dict:
    return {
        "nome_registro": "José da Silva Xavier",
        "nome_social": None,
        "cpf": f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}",
        "cns": "123456789012345",
        "data_nascimento": "1972-08-01",
        "genero": "masculino",
        "raca": "parda",
        "telefone": "(21) 99999-9999",
        "clinica_familia": {"cnes": "1234567", "nome": "Clinica da Familia XXX"},
        "equipe_saude_familia": {"id_ine": "1234567", "nome": "Equipe Roxo"},
        "responsavel_medico": "Roberta dos Santos",
        "responsavel_enfermagem": "Pedro da Nobrega",
        "cadastro_validado_indicador": True,
    }


@router.get("/patient/summary/{cpf}")
async def get_patient_summary(
    _: Annotated[User, Depends(get_current_active_user)],
    cpf: int,
) -> list:
    return {
        "alergias": [
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
        "medicamentos_uso_continuo": [
            "Losartana potássica",
            "Enalapril maleato",
            "Besilato de anlodipino",
            "Captopril",
            "Clonazepam",
            "Enalapril",
        ],
    }


@router.get("/patient/encounters/{cpf}")
async def get_patient_encouters(
    _: Annotated[User, Depends(get_current_active_user)],
    cpf: int,
) -> list:
    return [
        {
            "datahora_entrada": "2023-09-01T10:00:00",
            "datahora_saida": "2023-09-01T12:00:00",
            "local": "UPA 24h Magalhães Bastos",
            "tipo": "Consulta",
            "subtipo": "Emergência",
            "cids_ativos": ["A10.2", "B02.5"],
            "responsavel": {"nome": "Dr. João da Silva", "funcao": "Médico(a)"},
            "descricao": "Lorem ipsum dolor sit amet consectetur. ",
            "tags_filtro": ["UPA"],
        },
        {
            "datahora_entrada": "2021-09-01T10:00:00",
            "datahora_saida": "2021-09-01T12:00:00",
            "local": "UPA 24h Magalhães Bastos",
            "tipo": "Consulta",
            "subtipo": "Emergência",
            "cids_ativos": ["A10.2"],
            "responsavel": {"nome": "Dr. João da Silva", "funcao": "Médico(a)"},
            "descricao": "Lorem ipsum dolor sit amet consectetur. Sed vel suscipit id pulvinar sed nam libero eu. Leo arcu sit lacus nisl nullam eget et dignissim sed. Fames pretium cursus viverra posuere arcu tortor sit lectus congue. Velit tempor ultricies pulvinar magna pulvinar ridiculus consequat nibh...",
            "tags_filtro": ["UPA", "Emergência"],
        },
    ]
