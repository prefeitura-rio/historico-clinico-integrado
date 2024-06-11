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


router = APIRouter(prefix="/mrg", tags=["Entidades MRG (Formato Merged/Fundido)"])


PatientOutput = pydantic_model_creator(Patient, name="PatientOutput")
PatientConditionOutput = pydantic_model_creator(PatientCondition, name="PatientConditionOutput")


@router.put("/patient")
async def create_or_update_patient(
    _: Annotated[User, Depends(get_current_active_user)],
    patients: List[PatientModel],
) -> list[PatientOutput]:

    races = {x.slug: x for x in await Race.all()}
    cities = {x.code: x for x in await City.all()}
    genders = {x.slug: x for x in await Gender.all()}
    nationalities = {x.slug: x for x in await Nationality.all()}

    patients = [patient.dict() for patient in patients]

    addresses, cnss, telecoms = [], [], []
    for patient in patients:
        # Entity Splitting
        addresses.append(patient.pop('address_list'))
        cnss.append(patient.pop('cns_list'))
        telecoms.append(patient.pop('telecom_list'))

        # Object Convertions
        patient['race'] = races.get(patient['race'])
        patient['birth_city'] = cities.get(patient.get('birth_city'))
        patient['gender'] = genders.get(patient.get('gender'))
        patient['nationality'] = nationalities.get(patient.get('nationality'))
        patient['birth_date'] = patient['birth_date'].isoformat()

    existing_patients = [
        Patient.get_or_none(
            patient_code=x['patient_code']
        ).prefetch_related("address_patient_periods", "telecom_patient_periods", "patient_cns")
        for x in patients
    ]
    existing_patients = await asyncio.gather(*existing_patients)

    awaitables = []
    for i, patient in enumerate(patients):
        if existing_patients[i]:
            awaitables.append(update_and_return(existing_patients[i], patient))
        else:
            awaitables.append(Patient.create(**patient))
    modified_patients = await asyncio.gather(*awaitables)

    async def update_addresses():
        addresses_to_insert = []
        for i, address_list in enumerate(addresses):
            for address in address_list:
                address["patient"] = modified_patients[i]
                address["city"] = cities.get(address.pop("city"))
                address["period_start"] = address.pop("start")
                address["period_end"] = address.pop("end")
                addresses_to_insert.append(PatientAddress(**address))
        await PatientAddress.filter(patient_id__in=[x.id for x in modified_patients]).delete()
        await PatientAddress.bulk_create(addresses_to_insert)

    async def update_telecoms():
        telecoms_to_insert = []
        for i, telecom_list in enumerate(telecoms):
            for telecom in telecom_list:
                telecom["patient"] = modified_patients[i]
                telecom["period_start"] = telecom.get("start")
                telecom["period_end"] = telecom.get("end")
                telecoms_to_insert.append(PatientTelecom(**telecom))
        await PatientTelecom.filter(patient_id__in=[x.id for x in modified_patients]).delete()
        await PatientTelecom.bulk_create(telecoms_to_insert)

    async def update_cnss():
        async def create_cns(cns_params):
            try:
                await PatientCns.create(**cns_params)
            except IntegrityError:
                await PatientCns.get(value=cns_params["value"]).delete()

        cns_creation_tasks = []
        for i, cns_list in enumerate(cnss):
            for cns in cns_list:
                cns["patient"] = modified_patients[i]
                cns_creation_tasks.append(create_cns(cns))
        await PatientCns.filter(patient_id__in=[x.id for x in modified_patients]).delete()
        await asyncio.gather(*cns_creation_tasks)

    await asyncio.gather(*[update_cnss(), update_addresses(), update_telecoms()])

    return modified_patients


@router.put("/patientcondition")
async def create_or_update_patientcondition(
    _: Annotated[User, Depends(get_current_active_user)],
    patientcondition_list: list[PatientConditionListModel],
) -> list[PatientConditionOutput]:

    inserted_conditions = []
    for patientcondition in patientcondition_list:
        patient_data = patientcondition.dict()

        try:
            patient = await Patient.get_or_none(
                patient_cpf=patient_data.get("patient_cpf")
            ).prefetch_related("patientconditions")
        except ValidationError as e:
            return HTMLResponse(status_code=400, content=str(e))

        if patient is None:
            return HTMLResponse(status_code=400, content="Patient doesn't exist")

        # Reset Patient Conditions
        for instance in patient.patientconditions.related_objects:
            await instance.delete()

        for condition in patient_data.get("conditions"):
            condition_code = await ConditionCode.get_or_none(value=condition.get("code"))
            if condition_code is None:
                return HTMLResponse(
                    status_code=400, content=f"Condition Code {condition.get('code')} doesn't exist"
                )
            condition["patient"] = patient
            condition["condition_code"] = condition_code
            new_condition = await PatientCondition.create(**condition)
            inserted_conditions.append(new_condition)

    return inserted_conditions


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
