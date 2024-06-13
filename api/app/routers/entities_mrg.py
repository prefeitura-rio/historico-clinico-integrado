# -*- coding: utf-8 -*-
import asyncio
from typing import Annotated, List

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import ValidationError, IntegrityError

from app.dependencies import get_current_active_user
from app.pydantic_models import PatientModel, PatientConditionListModel, CompletePatientModel
from app.models import (
    User,
    Patient,
    City,
    Race,
    Gender,
    Nationality,
    PatientAddress,
    PatientTelecom,
    PatientCondition,
    ConditionCode,
    PatientCns,
)
from app.utils import update_and_return


router = APIRouter(
    prefix="/mrg", tags=["Entidades MRG (Formato Merged/Fundido)"])


PatientOutput = pydantic_model_creator(Patient, name="PatientOutput")
PatientConditionOutput = pydantic_model_creator(
    PatientCondition, name="PatientConditionOutput")


@router.put("/patient")
async def create_or_update_patient(
    _: Annotated[User, Depends(get_current_active_user)],
    patients: List[PatientModel],
) -> int:

    patients = [patient.dict(exclude_none=True) for patient in patients]
    
    cities, races, genders, nationalities = {}, {}, {}, {}
    async def get_instance(Model, table, slug=None, code=None):
        if slug is None:
            return None
        if slug not in table:
            if code:
                table[slug] = await Model.get_or_none(code=code)
            elif slug:
                table[slug] = await Model.get_or_none(slug=slug)
        return table[slug]

    for patient in patients:
        patient['race'] = await get_instance(Model=Race, table=races, slug=patient.get('race'))
        patient['gender'] = await get_instance(Model=Gender, table=genders, slug=patient.get("gender"))
        patient['nationality'] = await get_instance(Model=Nationality, table=nationalities, slug=patient.get("nationality"))
        patient['birth_city'] = await get_instance(Model=City, table=cities, code=patient.get('birth_city'))
        patient['birth_date'] = patient['birth_date'].isoformat()

    inserts = [Patient(**patient) for patient in patients]
    updatable_fields = [ x for x in dict(inserts[0]).keys() if x not in ['patient_code', 'patient_cpf', 'created_at', 'updated_at', 'id'] ]
    bulk_insert_results = await Patient.bulk_create(
        inserts,
        batch_size=500,
        on_conflict=["patient_cpf"],
        update_fields=updatable_fields
    )

    return len(bulk_insert_results)


@router.get("/patient/{patient_cpf}")
async def get_patient(
    _: Annotated[User, Depends(get_current_active_user)],
    patient_cpf: int,
) -> CompletePatientModel:

    patient = await Patient.get_or_none(patient_cpf=patient_cpf).prefetch_related(
        "race",
        "nationality",
        "gender",
        "patient_cns",
        "birth_city__state__country",
        "telecom_patient_periods",
        "address_patient_periods__city__state__country",
        "patientconditions__condition_code",
    )

    address_list = []
    for address in patient.address_patient_periods.related_objects:
        address_data = dict(address)
        address_data["city"] = address.city.code
        address_data["state"] = address.city.state.code
        address_data["country"] = address.city.state.country.code
        address_list.append(address_data)

    telecom_list = []
    for telecom in patient.telecom_patient_periods.related_objects:
        telecom_data = dict(telecom)
        telecom_list.append(telecom_data)

    condition_list = []
    for condition in patient.patientconditions.related_objects:
        condition_data = dict(condition)
        condition_data["code"] = condition.condition_code.value
        condition_list.append(condition_data)

    cns_list = []
    for cns in patient.patient_cns.related_objects:
        cns_data = dict(cns)
        cns_list.append(cns_data)

    patient_data = dict(patient)
    patient_data["gender"] = patient.gender.slug
    patient_data["race"] = patient.race.slug
    patient_data["address_list"] = address_list
    patient_data["telecom_list"] = telecom_list
    patient_data["condition_list"] = condition_list
    patient_data["cns_list"] = cns_list

    if patient.nationality is not None:
        patient_data["nationality"] = patient.nationality.slug

    if patient.birth_city is not None:
        patient_data["birth_city"] = patient.birth_city.code
        patient_data["birth_state"] = patient.birth_city.state.code
        patient_data["birth_country"] = patient.birth_city.state.country.code

    return patient_data
