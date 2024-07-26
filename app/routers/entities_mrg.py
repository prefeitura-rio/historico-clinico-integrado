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
    ProfessionalModel,
    TeamModel
)
from app.models import (
    Occupation,
    OccupationFamily,
    User,
    City,
    Race,
    Gender,
    Nationality,
    MergedPatient,
    MergedPatientAddress,
    MergedPatientTelecom,
    MergedPatientCns,
    HealthCareProfessional,
    ProfessionalRegistry,
    HealthCareProfessionalOccupation,
    HealthCareTeam,
    HealthCareTeamType,
    HealthCareProfessionalTeam
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
        'patient_code', 'patient_cpf', 'created_at', 'id']]
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


@router.put("/professionals")
async def create_or_update_professionals(
    _: Annotated[User, Depends(get_current_active_user)],
    professionals: List[ProfessionalModel],
) -> int:

    # Index by ID_SUS
    professionals_indexed = {
        p.id_profissional_sus: p.dict(exclude_none=True)
        for p in professionals
    }

    # Insert Professionals
    professionals_inserts = []
    for id_sus, professional in professionals_indexed.items():
        professional['id_sus'] = professional.pop('id_profissional_sus')
        professional['name'] = professional.pop('nome')
        professionals_inserts.append(HealthCareProfessional(**professional))
    await HealthCareProfessional.bulk_create(
        professionals_inserts,
        batch_size=500,
        on_conflict=["id_sus"],
        update_fields=["name", "cpf","cns"]
    )

    # Retrieve all Ocupations and Families
    occupation_ids = [x.cbo for x in await Occupation.all()]
    occupation_family_ids = [x.code for x in await OccupationFamily.all()]

    # Retrieve Inserted Professionals
    professionals = await HealthCareProfessional.filter(
        id_sus__in=list(professionals_indexed.keys())
    )

    new_occupations = []
    new_occupation_families = []
    new_professional_occupation = []

    # Insert Health Care Professionals Occupations
    for id_sus, professional in zip(list(professionals_indexed.keys()), professionals):
        for cbo in professionals_indexed[id_sus]['cbo']:

            # If CBO Family does not exist in our base, prepare to insert it
            if cbo.get("id_cbo_familia") not in occupation_family_ids:
                new_occupation_families.append(
                    OccupationFamily(
                        code=cbo.get("id_cbo_familia"),
                        name=cbo.get("cbo_familia")
                    )
                )

            # If CBO does not exist in our base, prepare to insert it
            if cbo.get("id_cbo") not in occupation_ids:
                new_occupations.append(
                    Occupation(
                        cbo=cbo.get("id_cbo"),
                        description=cbo.get("cbo"),
                        family_id=cbo.get("id_cbo_familia")
                    )
                )

            new_professional_occupation.append(
                HealthCareProfessionalOccupation(
                    professional_id=professional.id_sus,
                    role_id=cbo.get("id_cbo")
                )
            )
    await OccupationFamily.bulk_create(
        new_occupation_families,
        batch_size=500,
        ignore_conflicts=True
    )
    await Occupation.bulk_create(
        new_occupations,
        batch_size=500,
        ignore_conflicts=True
    )
    await HealthCareProfessionalOccupation.bulk_create(
        new_professional_occupation,
        batch_size=500,
        ignore_conflicts=True
    )

    # Insert Health Care Professional Registry
    registry_inserts = []
    for id_sus, professional in zip(list(professionals_indexed.keys()), professionals):
        registry_list = professionals_indexed[id_sus].get('conselho', [])
        for registry in registry_list:
            registry_inserts.append(
                ProfessionalRegistry(
                    professional_id=professional.id_sus,
                    code=registry.get('id_registro_conselho'),
                    type=registry.get('id_tipo_conselho')
                )
            )
    await ProfessionalRegistry.bulk_create(
        registry_inserts,
        batch_size=500,
        ignore_conflicts=True
    )

    return len(professionals)

@router.put("/teams")
async def create_or_update_teams(
    _: Annotated[User, Depends(get_current_active_user)],
    teams: List[TeamModel],
) -> int:

    # Insert/Update Team Types
    types = {t.id_equipe_tipo: t.equipe_tipo_descricao for t in teams}
    types_to_insert = [
        HealthCareTeamType(code=tipo, name=nome)
        for tipo, nome in types.items()
    ]
    await HealthCareTeamType.bulk_create(
        types_to_insert,
        batch_size=500,
        ignore_conflicts=True
    )

    # Insert/Update Teams
    teams_indexed = {
        t.id_ine: t.dict(exclude_none=True)
        for t in teams
    }
    teams_to_insert = [
        HealthCareTeam(
            ine_code=ine,
            name=team.pop('nome_referencia'),
            team_type_id=team.pop('id_equipe_tipo'),
            healthcare_unit_id=team.pop('id_cnes'),
            phone=team.pop('telefone', None),
        )
        for ine, team in teams_indexed.items()
    ]
    created_teams = await HealthCareTeam.bulk_create(
        teams_to_insert,
        batch_size=500,
        on_conflict=["ine_code"],
        update_fields=["name", "team_type_id", "phone", "healthcare_unit_id"]
    )

    # Insert/Update Professional Teams
    professional_teams_to_insert = []
    for team in teams:
        for column in [
            'medicos',
            'enfermeiros',
            'auxiliares_tecnicos_enfermagem',
            'agentes_comunitarios',
            'auxiliares_tecnico_saude_bucal',
            'dentista',
            'outros_profissionais'
        ]:
            for prof_id_sus in team.dict().get(column, []):
                professional_teams_to_insert.append(
                    HealthCareProfessionalTeam(
                        professional_id=prof_id_sus,
                        team_id=team.id_ine
                    )
                )
    await HealthCareProfessionalTeam.bulk_create(
        professional_teams_to_insert,
        batch_size=500,
        ignore_conflicts=True
    )

    return len(created_teams)