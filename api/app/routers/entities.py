# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from tortoise.contrib.pydantic import pydantic_model_creator

from app.dependencies import get_current_active_user
from app.pydantic_models import PatientModel
from app.models import (
    User, DataSource, Patient, City, Race, Gender, Nationality, Address, Telecom, PatientCondition, ConditionCode
)

PatientOutput = pydantic_model_creator(Patient, name="PatientOutput")


router = APIRouter(prefix="/mrg", tags=["Entidades MRG (Formato Merged/Fundido)"])


# Endpoint 1 - [PUT] Create Patient

@router.put("/patient", response_model=PatientOutput, status_code=200)
async def create_or_update_patient(
    _: Annotated[User, Depends(get_current_active_user)],
    patient: PatientModel,
) -> PatientOutput:
    input = patient.dict()

    birth_city = await City.get_or_none(
        code                    = input['birth_city'],
        state__code             = input['birth_state'],
        state__country__code    = input['birth_country']
    )
    new_data = {
        'patient_cpf'           : input.get('patient_cpf'),
        'birth_date'            : input.get('birth_date'),
        'active'                : input.get('active'),
        'protected_person'      : input.get('protected_person'),
        'deceased'              : input.get('deceased'),
        'deceased_date'         : input.get('deceased_date'),
        'name'                  : input.get('name'),
        'mother_name'           : input.get('mother'),
        'father_name'           : input.get('father'),
        'naturalization'        : input.get('naturalization'),
        'birth_city'            : birth_city,
        'race'                  : await Race.get_or_none(slug = input['race']),
        'gender'                : await Gender.get_or_none(slug = input['gender']),
        'nationality'           : await Nationality.get_or_none(slug = input['nationality']),
    }

    patient = await Patient.get_or_none(
        patient_cpf = input.get('patient_cpf')
    ).prefetch_related('address_patient_periods','telecom_patient_periods')

    if patient != None:
        await patient.update_from_dict(new_data).save()
    else:
        patient = await Patient.create(**new_data)

    # Reset de Address
    for instance in patient.address_patient_periods.related_objects:
        await instance.delete()
    for address in input.get("address_list"):
        address_city = await City.get_or_none(
            code                    = address['city'],
            state__code             = address['state'],
            state__country__code    = address['country']
        )
        address['patient']  = patient
        address['city']     = address_city
        await Address.create(**address)

    # Reset de Telecom
    for instance in patient.telecom_patient_periods.related_objects:
        await instance.delete()
    for telecom in input.get("telecom_list"):
        telecom['patient']  = patient
        await Telecom.create(**telecom)

    return await PatientOutput.from_tortoise_orm(patient)




# Endpoint 3 - [GET] Patient
# - Lista com todos os endereços, telecoms e Conditions