# -*- coding: utf-8 -*-
from typing import Annotated, List

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import ValidationError

from app.dependencies import get_current_active_user
from app.pydantic_models import (
    CompletePatientModel,
    MergedPatient as PydanticMergedPatient,
    MergedPatientCns as PydanticMergedPatientCns,
    MergedPatientAddress as PydanticMergedPatientAddress,
    MergedPatientTelecom as PydanticMergedPatientTelecom,
)
from app.models import (
    User,
    City,
    Race,
    Gender,
    Nationality,
    MergedPatient,
    MergedPatientAddress,
    MergedPatientTelecom,
    MergedPatientCns,
)
from app.utils import get_instance


router = APIRouter(
    prefix="/mrg", tags=["Entidades MRG (Formato Merged/Fundido)"])

PatientOutput = pydantic_model_creator(MergedPatient, name="PatientOutput")


@router.put("/patient")
async def create_or_update_patient(
    _: Annotated[User, Depends(get_current_active_user)],
    patients: List[PydanticMergedPatient],
) -> int:

    patients = [patient.dict(exclude_none=True) for patient in patients]

    cities, races, genders, nationalities = {}, {}, {}, {}

    for patient in patients:
        patient['race'] = await get_instance(Model=Race, table=races, slug=patient.get('race'))
        patient['gender'] = await get_instance(Model=Gender, table=genders, slug=patient.get("gender"))
        patient['nationality'] = await get_instance(Model=Nationality, table=nationalities, slug=patient.get("nationality"))
        patient['birth_city'] = await get_instance(Model=City, table=cities, code=patient.get('birth_city'))
        patient['birth_date'] = patient['birth_date'].isoformat()

    try:
        inserts = [MergedPatient(**patient) for patient in patients]
    except ValidationError as e:
        return HTMLResponse(content=str(e), status_code=400)

    updatable_fields = [x for x in dict(inserts[0]).keys() if x not in [
        'patient_code', 'patient_cpf', 'created_at', 'updated_at', 'id']]
    bulk_insert_results = await MergedPatient.bulk_create(
        inserts,
        batch_size=500,
        on_conflict=["patient_code"],
        update_fields=updatable_fields
    )

    return len(bulk_insert_results)


@router.put("/patientaddress")
async def create_or_update_patientaddress(
    _: Annotated[User, Depends(get_current_active_user)],
    patientaddress_list: List[PydanticMergedPatientAddress],
) -> int:
    # Get list of patient codes
    patient_codes = [
        patientaddress.patient_code for patientaddress in patientaddress_list]

    # Delete all addresses for the patients
    await MergedPatientAddress.filter(patient_id__in=patient_codes).delete()

    # Prepare Inserts
    inserts = []
    for address in patientaddress_list:
        address = address.dict(exclude_none=True)
        address['city_id'] = address.pop('city')
        address['patient_id'] = address.pop('patient_code')

        inserts.append(MergedPatientAddress(**address))

    # Bulk Insert
    results = await MergedPatientAddress.bulk_create(
        inserts,
        batch_size=500
    )

    return len(results)


@router.put("/patienttelecom")
async def create_or_update_patienttelecom(
    _: Annotated[User, Depends(get_current_active_user)],
    patienttelecom_list: List[PydanticMergedPatientTelecom],
) -> int:
    # Get list of patient codes
    patient_codes = [
        patientaddress.patient_code for patientaddress in patienttelecom_list]

    # Delete all addresses for the patients
    await MergedPatientTelecom.filter(patient_id__in=patient_codes).delete()

    # Prepare Inserts
    inserts = []
    for telecom in patienttelecom_list:
        telecom = telecom.dict(exclude_none=True)
        telecom['patient_id'] = telecom.pop('patient_code')

        inserts.append(MergedPatientTelecom(**telecom))

    # Bulk Insert
    results = await MergedPatientTelecom.bulk_create(
        inserts,
        batch_size=500
    )

    return len(results)


@router.put("/patientcns")
async def create_or_update_patientcns(
    _: Annotated[User, Depends(get_current_active_user)],
    patientcns_list: List[PydanticMergedPatientCns],
) -> int:
    # Get list of patient codes
    patient_codes = [patientcns.patient_code for patientcns in patientcns_list]

    # Delete all CNS for the patients/
    await MergedPatientCns.filter(patient_id__in=patient_codes).delete()

    # Prepare Inserts
    inserts = []
    for cns in patientcns_list:
        cns = cns.dict(exclude_none=True)
        cns['patient_id'] = cns.pop('patient_code')

        inserts.append(MergedPatientCns(**cns))

    # Bulk Insert
    results = await MergedPatientCns.bulk_create(
        inserts,
        batch_size=500,
        ignore_conflicts=True
    )

    return len(results)


@router.get("/patient/{patient_cpf}")
async def get_patient(
    _: Annotated[User, Depends(get_current_active_user)],
    patient_cpf: int,
)-> list[CompletePatientModel]:

    patients = await MergedPatient.filter(patient_cpf=patient_cpf).prefetch_related(
        "race",
        "nationality",
        "gender",
        "patient_cns",
        "birth_city__state__country",
        "telecom_patient_periods",
        "address_patient_periods__city__state__country"
    )

    patient_list = []
    for patient in patients:
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

        cns_list = []
        for cns in patient.patient_cns.related_objects:
            cns_data = dict(cns)
            cns_list.append(cns_data)

        patient_data = dict(patient)
        patient_data["gender"] = patient.gender.slug
        patient_data["race"] = patient.race.slug
        patient_data["address_list"] = address_list
        patient_data["telecom_list"] = telecom_list
        patient_data["cns_list"] = cns_list

        if patient.nationality is not None:
            patient_data["nationality"] = patient.nationality.slug

        if patient.birth_city is not None:
            patient_data["birth_city"] = patient.birth_city.code
            patient_data["birth_state"] = patient.birth_city.state.code
            patient_data["birth_country"] = patient.birth_city.state.country.code

        patient_list.append(patient_data)

    return patient_list
