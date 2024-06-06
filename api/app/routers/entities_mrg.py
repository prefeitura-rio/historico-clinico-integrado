# -*- coding: utf-8 -*-
import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import ValidationError, IntegrityError
from tortoise.transactions import in_transaction

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


router = APIRouter(prefix="/mrg", tags=["Entidades MRG (Formato Merged/Fundido)"])


PatientOutput = pydantic_model_creator(Patient, name="PatientOutput")
PatientConditionOutput = pydantic_model_creator(PatientCondition, name="PatientConditionOutput")


@router.put("/patient")
async def create_or_update_patient(
    _: Annotated[User, Depends(get_current_active_user)],
    patients: list[PatientModel],
) -> list[PatientOutput]:

    async def process_patient(patient_data):
        birth_city_task = City.get_or_none(
            code=patient_data["birth_city"],
            state__code=patient_data["birth_state"],
            state__country__code=patient_data["birth_country"],
        )
        race_task = Race.get_or_none(slug=patient_data["race"])
        gender_task = Gender.get_or_none(slug=patient_data["gender"])
        nationality_task = Nationality.get_or_none(slug=patient_data["nationality"])

        birth_city, race, gender, nationality = await asyncio.gather(
            birth_city_task, race_task, gender_task, nationality_task
        )

        new_data = {
            "patient_cpf": patient_data.get("patient_cpf"),
            "patient_code": patient_data.get("patient_code"),
            "active": patient_data.get("active"),
            "protected_person": patient_data.get("protected_person"),
            "deceased": patient_data.get("deceased"),
            "deceased_date": patient_data.get("deceased_date"),
            "name": patient_data.get("name"),
            "mother_name": patient_data.get("mother_name"),
            "father_name": patient_data.get("father_name"),
            "birth_date": patient_data.get("birth_date").isoformat(),
            "birth_city": birth_city,
            "race": race,
            "gender": gender,
            "nationality": nationality,
        }

        async with in_transaction():
            patient = await Patient.get_or_none(
                patient_cpf=patient_data["patient_cpf"]
            ).prefetch_related("address_patient_periods", "telecom_patient_periods", "patient_cns")

            if patient:
                await patient.update_from_dict(new_data).save()
            else:
                patient = await Patient.create(**new_data)

            # Reset and update Address
            await patient.address_patient_periods.all().delete()
            address_tasks = [
                City.get_or_none(
                    code=address["city"],
                    state__code=address["state"],
                    state__country__code=address["country"],
                )
                for address in patient_data.get("address_list", [])
            ]
            address_cities = await asyncio.gather(*address_tasks)

            for address, city in zip(patient_data.get("address_list", []), address_cities):
                address["patient"] = patient
                address["city"] = city
                address["period_start"] = address.get("start")
                address["period_end"] = address.get("end")
                await PatientAddress.create(**address)

            # Reset and update Telecom
            await patient.telecom_patient_periods.all().delete()
            telecoms = patient_data.get("telecom_list", [])
            for telecom in telecoms:
                telecom["patient"] = patient
                telecom["period_start"] = telecom.get("start")
                telecom["period_end"] = telecom.get("end")
                await PatientTelecom.create(**telecom)

            # Reset and update CNS
            await patient.patient_cns.all().delete()
            cns_list = patient_data.get("cns_list", [])
            for cns in cns_list:
                cns["patient"] = patient
                try:
                    await PatientCns.create(**cns)
                except IntegrityError:
                    existing_cns = await PatientCns.get_or_none(value=cns["value"])
                    if existing_cns:
                        await existing_cns.delete()

        return await PatientOutput.from_tortoise_orm(patient)

    patient_tasks = [process_patient(patient.dict()) for patient in patients]
    updated_patients = await asyncio.gather(*patient_tasks)
    return updated_patients


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
