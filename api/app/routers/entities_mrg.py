# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import ValidationError

from app.dependencies import get_current_active_user
from app.pydantic_models import PatientModel, PatientConditionListModel, CompletePatientModel
from app.models import (
    User, Patient, City, Race, Gender, Nationality, PatientAddress,
    PatientTelecom, PatientCondition, ConditionCode, PatientCns
)


router = APIRouter(prefix="/mrg", tags=["Entidades MRG (Formato Merged/Fundido)"])


PatientOutput = pydantic_model_creator(
    Patient, name="PatientOutput"
)
PatientConditionOutput = pydantic_model_creator(
    PatientCondition, name="PatientConditionOutput"
)


@router.put("/patient")
async def create_or_update_patient(
    _           : Annotated[User, Depends(get_current_active_user)],
    patient     : PatientModel,
) -> PatientOutput:

    patient_data = patient.dict()

    birth_city = await City.get_or_none(
        code                    = patient_data['birth_city'],
        state__code             = patient_data['birth_state'],
        state__country__code    = patient_data['birth_country']
    )
    new_data = {
        'patient_cpf'           : patient_data.get('patient_cpf'),
        'birth_date'            : patient_data.get('birth_date'),
        'active'                : patient_data.get('active'),
        'protected_person'      : patient_data.get('protected_person'),
        'deceased'              : patient_data.get('deceased'),
        'deceased_date'         : patient_data.get('deceased_date'),
        'name'                  : patient_data.get('name'),
        'mother_name'           : patient_data.get('mother_name'),
        'father_name'           : patient_data.get('father_name'),
        'birth_city'            : birth_city,
        'race'                  : await Race.get_or_none(slug = patient_data['race']),
        'gender'                : await Gender.get_or_none(slug = patient_data['gender']),
        'nationality'           : await Nationality.get_or_none(slug = patient_data['nationality']),
    }

    patient = await Patient.get_or_none(
        patient_cpf = patient_data.get('patient_cpf')
    ).prefetch_related('address_patient_periods','telecom_patient_periods', 'patient_cns')

    if patient is not None:
        await patient.update_from_dict(new_data).save()
    else:
        try:
            patient = await Patient.create(**new_data)
        except ValidationError as e:
            return HTMLResponse(status_code=400, content=str(e))

    # Reset de Address
    for instance in patient.address_patient_periods.related_objects:
        await instance.delete()
    for address in patient_data.get("address_list"):
        address_city = await City.get_or_none(
            code                    = address['city'],
            state__code             = address['state'],
            state__country__code    = address['country']
        )
        address['patient']  = patient
        address['city']     = address_city
        await PatientAddress.create(**address)

    # Reset de Telecom
    for instance in patient.telecom_patient_periods.related_objects:
        await instance.delete()
    for telecom in patient_data.get("telecom_list"):
        telecom['patient']  = patient
        await PatientTelecom.create(**telecom)

    # Reset de CNS
    for instance in patient.patient_cns.related_objects:
        await instance.delete()
    for cns in patient_data.get("cns_list"):
        cns['patient']  = patient
        await PatientCns.create(**cns)

    return await PatientOutput.from_tortoise_orm(patient)


@router.put("/patientcondition")
async def create_or_update_patientcondition(
    _                   : Annotated[User, Depends(get_current_active_user)],
    patientcondition    : PatientConditionListModel,
) -> list[PatientConditionOutput]:

    patient_data = patientcondition.dict()

    patient = await Patient.get_or_none(
        patient_cpf=patient_data.get('patient_cpf')
    ).prefetch_related('patientconditions')

    if patient is None:
        return HTMLResponse(status_code=400, content="Patient doesn't exist")

    # Reset Patient Conditions
    for instance in patient.patientconditions.related_objects:
        await instance.delete()

    conditions = []
    for condition in patient_data.get('conditions'):
        condition_code = await ConditionCode.get_or_none(
            value=condition.get('code')
        )
        if condition_code is None:
            return HTMLResponse(
                status_code=400,
                content=f"Condition Code {condition.get('code')} doesn't exist"
            )
        condition['patient'] = patient
        condition['condition_code'] = condition_code
        new_condition = await PatientCondition.create(**condition)
        conditions.append(new_condition)

    return conditions

@router.get("/patient/{patient_cpf}")
async def get_patient(
    _           : Annotated[User, Depends(get_current_active_user)],
    patient_cpf : int,
) -> CompletePatientModel:

    patient = await Patient.get_or_none(
        patient_cpf=patient_cpf
    ).prefetch_related(
        'race','nationality','gender','patient_cns',
        'birth_city__state__country',
        'telecom_patient_periods',
        'address_patient_periods__city__state__country',
        'patientconditions__condition_code',
    )

    address_list = []
    for address in patient.address_patient_periods.related_objects:
        address_data = dict(address)
        address_data['city']    = address.city.code
        address_data['state']   = address.city.state.code
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
    for cns in patient.patient_cns.related_objects:
        cns_data = dict(cns)
        cns_list.append(cns_data)

    patient_data = dict(patient)
    patient_data['gender']          = patient.gender.slug
    patient_data['race']            = patient.race.slug
    patient_data['address_list']    = address_list
    patient_data['telecom_list']    = telecom_list
    patient_data['condition_list']  = condition_list
    patient_data['cns_list']        = cns_list

    if patient.nationality is not None:
        patient_data['nationality']= patient.nationality.slug

    if patient.birth_city is not None:
        patient_data['birth_city']      = patient.birth_city.code
        patient_data['birth_state']     = patient.birth_city.state.code
        patient_data['birth_country']   = patient.birth_city.state.country.code

    return patient_data
