# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from tortoise.contrib.pydantic import pydantic_model_creator

from app.dependencies import get_current_active_user
from app.pydantic_models import PatientModel, PatientConditionListModel, CompletePatientModel
from app.models import (
    User, DataSource, Patient, City, Race, Gender, Nationality, Address, Telecom, PatientCondition, ConditionCode
)

PatientOutput = pydantic_model_creator(Patient, name="PatientOutput")
PatientConditionOutput = pydantic_model_creator(PatientCondition, name="PatientConditionOutput")


router = APIRouter(prefix="/mrg", tags=["Entidades MRG (Formato Merged/Fundido)"])


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


@router.put("/patientcondition", response_model=list[PatientConditionOutput], status_code=200)
async def create_or_update_patientcondition(
    _: Annotated[User, Depends(get_current_active_user)],
    patientcondition: PatientConditionListModel,
) -> list[PatientConditionOutput]:
    input = patientcondition.dict()

    patient = await Patient.get_or_none(
        patient_cpf=input.get('patient_cpf')
    ).prefetch_related('patientconditions')

    if patient == None:
        raise HTTPException(status_code=400, detail="Patient don't exist")

    # Reset Patient Conditions
    for instance in patient.patientconditions.related_objects:
        await instance.delete()

    conditions = []
    for condition in input.get('conditions'):
        condition_code = await ConditionCode.get_or_none(
            value=condition.get('code')
        )
        if condition_code == None:
            raise HTTPException(
                status_code=400,
                detail=f"Condition Code {condition.get('code')} don't exist"
            )
        condition['patient'] = patient
        condition['condition_code'] = condition_code
        new_condition = await PatientCondition.create(**condition)
        conditions.append(new_condition)

    return conditions

@router.get("/patient/{patient_cpf}", response_model=CompletePatientModel)
async def get_patient(
    patient_cpf : int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> list[CompletePatientModel]:

    patient = await Patient.get_or_none(patient_cpf=patient_cpf).prefetch_related(
        'race','nationality','gender','cnss',
        'birth_city__state__country',
        'telecom_patient_periods',
        'address_patient_periods__city__state__country',
        'patientconditions__condition_code',
    )

    address_list = []
    for address in patient.address_patient_periods.related_objects:
        address_data = dict(address)
        address_data['city'] = address.city.code
        address_data['state'] = address.city.state.code
        address_data['country'] = address.city.state.country.code
        address_list.append(address_data)

    telecom_list = []
    for telecom in patient.telecom_patient_periods.related_objects:
        telecom_data = dict(telecom)
        telecom_list.append(telecom_data)

    condition_list = []
    for condition in patient.patientconditions.related_objects:
        condition_data = dict(condition)
        condition_data['code'] = condition.condition_code.value
        condition_list.append(condition_data)

    cns_list = []
    for cns in patient.cnss.related_objects:
        cns_data = dict(cns)
        cns_list.append(cns_data)

    patient_data = dict(patient)
    patient_data['gender'] = patient.gender.slug
    patient_data['nationality'] = patient.nationality.slug
    patient_data['race'] = patient.race.slug
    patient_data['birth_city'] = patient.birth_city.code
    patient_data['birth_state'] = patient.birth_city.state.code
    patient_data['birth_country'] = patient.birth_city.state.country.code
    patient_data['address_list'] = address_list
    patient_data['telecom_list'] = telecom_list
    patient_data['condition_list'] = condition_list
    patient_data['cns_list'] = cns_list

    return patient_data