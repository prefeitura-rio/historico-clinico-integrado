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
from app.utils import read_timestamp

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

    data = patient_record["dados"]

    cns_principal = None
    if len(patient_record["cns"]) > 0:
        cns_principal = patient_record["cns"][0]

    telefone_principal = None
    if len(patient_record["contato"]["telefone"]) > 0:
        telefone_principal = patient_record["contato"]["telefone"][0]["valor"]

    clinica_principal = {}
    if len(patient_record["clinica_familia"]) > 0:
        clinica_principal = patient_record["clinica_familia"][0]

    equipe_principal = {}
    medicos, enfermeiros = [], []
    if len(patient_record["equipe_saude_familia"]) > 0:
        equipe_principal = patient_record["equipe_saude_familia"][0]

        for equipe in patient_record["equipe_saude_familia"]:
            medicos.extend(equipe["medicos"])
            enfermeiros.extend(equipe["enfermeiros"])

    for medico in medicos:
        medico['registry'] = medico.pop('id_profissional_sus')
        medico['name'] = medico.pop('nome')

    for enfermeiro in enfermeiros:
        enfermeiro['registry'] = enfermeiro.pop('id_profissional_sus')
        enfermeiro['name'] = enfermeiro.pop('nome')

    data_nascimento = None
    if data.get("data_nascimento") is not None:
        data_nascimento = read_timestamp(data.get("data_nascimento"), format='date')

    return {
        "registration_name": data.get("nome"),
        "social_name": data.get("nome_social"),
        "cpf": f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}",
        "cns": cns_principal,
        "birth_date": data_nascimento,
        "gender": data.get("genero"),
        "race": data.get("raca"),
        "phone": telefone_principal,
        "family_clinic": {
            "cnes": clinica_principal.get("id_cnes"),
            "name": clinica_principal.get("nome"),
            "phone": clinica_principal.get("telefone"),
        },
        "family_health_team": {
            "ine_code": equipe_principal.get("id_ine"),
            "name": equipe_principal.get("nome"),
            "phone": equipe_principal.get("telefone"),
        },
        "medical_responsible": medicos,
        "nursing_responsible": enfermeiros,
        "validated": data.get("identidade_validada_indicador"),
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

    results_json = read_sql(
        f"""
        SELECT *
        FROM `{BIGQUERY_PROJECT}`.`saude_historico_clinico`.`episodio_assistencial`
        WHERE paciente.cpf = '{cpf}'
        """,
        from_file="/tmp/credentials.json",
    ).to_json(orient="records")

    encounters = []
    for result in json.loads(results_json):
        # Responsible professional
        professional = result.get('profissional_saude_responsavel')
        if professional:
            professional = {
                "name": professional.get('nome'),
                "role": professional.get('especialidade')
            }

        # CIDs
        cids = []
        for cid in result['condicoes']:
            if cid.get('descricao') is not None:
                cids.append(cid['descricao'])

        encounter = {
            "entry_datetime": read_timestamp(result['entrada_datahora'], format='datetime'),
            "exit_datetime": read_timestamp(result['saida_datahora'], format='datetime'),
            "location": result['estabelecimento']['nome'],
            "type": result['tipo'],
            "subtype": result['subtipo'],
            "active_cids": cids,
            "responsible": professional,
            "description": result['motivo_atendimento'],
            "motivation": result['motivo_atendimento'],
            "summary": result['desfecho_atendimento'],
            "filter_tags": [result['estabelecimento']['estabelecimento_tipo']],
        }
        encounters.append(encounter)

    return encounters
