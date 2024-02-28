# -*- coding: utf-8 -*-
import sys

sys.path.insert(0, "../")

import pytest  # noqa
from httpx import AsyncClient  # noqa


@pytest.mark.anyio
@pytest.mark.run(order=10)
async def test_create_stdpatientrecords_all_fields(
    client                      : AsyncClient,
    token                       : str,
    patient_cpf                 : str,
    patientrecord_raw_source    : str
):

    response = await client.post(
        "/std/patientrecords",
        headers={"Authorization": f"Bearer {token}"},
        json=[
                {
                    "active": True,
                    "birth_city_cod": "00001",
                    "birth_state_cod": "00001",
                    "birth_country_cod": "00001",
                    "birth_date": "2000-01-11",
                    "patient_cpf": patient_cpf,
                    "patient_code": f"{patient_cpf}.19970607",
                    "deceased": False,
                    "deceased_date": "2024-01-11",
                    "father_name": "João Cardoso Farias",
                    "gender": "male",
                    "mother_name": "Gabriela Marques da Cunha",
                    "name": "Fernando Marques Farias",
                    "nationality": "B",
                    "protected_person": False,
                    "race": "parda",
                    "cns_list": [
                        {
                            "value": "1171777717",
                            "is_main": True
                        }
                    ],
                    "address_list": [
                        {
                            "use": "string",
                            "type": "work",
                            "line": "Rua dos Bobos, 0",
                            "city": "00001",
                            "country": "00001",
                            "state": "00001",
                            "postal_code": "22222222",
                            "start": "2010-10-02",
                            "end": "2013-07-11"
                        }
                    ],
                    "telecom_list": [
                        {
                        "system": "phone",
                        "use": "home",
                        "value": "32323232",
                        "rank": 1,
                        "start": "2010-10-02"
                        }
                    ],
                    "raw_source_id": patientrecord_raw_source
                }
            ]
    )

    assert response.status_code == 201
    assert response.json()['count'] == 1

@pytest.mark.anyio
@pytest.mark.run(order=10)
async def test_create_stdpatientrecords_mandatory_fields(
    client                      : AsyncClient,
    token                       : str,
    patient_cpf                 : str,
    patientrecord_raw_source    : str
):

    response = await client.post(
        "/std/patientrecords",
        headers={"Authorization": f"Bearer {token}"},
        json=[
                {
                    "active": True,
                    "birth_date": "2000-01-11",
                    "patient_code": f"{patient_cpf}.20000111",
                    "patient_cpf": patient_cpf,
                    "gender": "male",
                    "race":"parda",
                    "name": "Fernando Marques Farias",
                    "raw_source_id": patientrecord_raw_source
                }
            ]
    )

    assert response.status_code == 201
    assert response.json()['count'] == 1


@pytest.mark.anyio
@pytest.mark.run(order=10)
async def test_create_stdpatientrecords_invalid_raw_source(
    client                      : AsyncClient,
    token                       : str,
    patient_cpf                 : str
):

    response = await client.post(
        "/std/patientrecords",
        headers={"Authorization": f"Bearer {token}"},
        json=[
                {
                    "active": True,
                    "birth_city_cod": "00001",
                    "birth_state_cod": "00001",
                    "birth_country_cod": "00001",
                    "birth_date": "2000-01-11",
                    "patient_cpf": patient_cpf,
                    "patient_code": f"{patient_cpf}.20000111",
                    "gender": "male",
                    "mother_name": "Gabriela Marques da Cunha",
                    "name": "Fernando Marques Farias",
                    "nationality": "B",
                    "race": "parda",
                    "cns_list": [],
                    "address_list": [],
                    "telecom_list": [],
                    "raw_source_id": "407a48a7-fc53-4ab1-8e18-dbd5c9ebfdbe"
                }
            ]
    )

    assert response.status_code == 404

@pytest.mark.anyio
@pytest.mark.run(order=10)
async def test_create_stdpatientrecords_cpf_mismatch(
    client                          : AsyncClient,
    token                           : str,
    patient_cpf                     : str,
    other_patientrecord_raw_source  : str
):

    response = await client.post(
        "/std/patientrecords",
        headers={"Authorization": f"Bearer {token}"},
        json=[
                {
                    "active": True,
                    "birth_city_cod": "00001",
                    "birth_state_cod": "00001",
                    "birth_country_cod": "00001",
                    "birth_date": "2000-01-11",
                    "patient_cpf": patient_cpf,
                    "patient_code": f"{patient_cpf}.20000111",
                    "gender": "male",
                    "mother_name": "Gabriela Marques da Cunha",
                    "name": "Fernando Marques Farias",
                    "nationality": "B",
                    "race": "parda",
                    "cns_list": [],
                    "address_list": [],
                    "telecom_list": [],
                    "raw_source_id": other_patientrecord_raw_source
                }
            ]
    )

    assert response.status_code == 400


@pytest.mark.anyio
@pytest.mark.run(order=10)
async def test_create_stdpatientrecords_invalid_cpf(
    client                      : AsyncClient,
    token                       : str,
    patient_invalid_cpf         : str,
    patientrecord_raw_source    : str
):

    response = await client.post(
        "/std/patientrecords",
        headers={"Authorization": f"Bearer {token}"},
        json=[
                {
                    "active": True,
                    "birth_city_cod": "00001",
                    "birth_state_cod": "00001",
                    "birth_country_cod": "00001",
                    "birth_date": "2000-01-11",
                    "patient_cpf": patient_invalid_cpf,
                    "patient_code": f"{patient_invalid_cpf}.20000111",
                    "deceased": False,
                    "deceased_date": "2024-01-11",
                    "father_name": "João Cardoso Farias",
                    "gender": "male",
                    "mother_name": "Gabriela Marques da Cunha",
                    "name": "Fernando Marques Farias",
                    "nationality": "B",
                    "protected_person": False,
                    "race": "parda",
                    "cns_list": [],
                    "address_list": [],
                    "telecom_list": [],
                    "raw_source_id": patientrecord_raw_source
                }
            ]
    )

    assert response.status_code == 400


@pytest.mark.anyio
@pytest.mark.run(order=11)
async def test_read_stdpatientrecords(
    client      : AsyncClient,
    token       : str,
    patient_cpf : str
):
    response = await client.get(
        f"/std/patientrecords?patient_cpf={patient_cpf}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    json_response = response.json()
    assert len(json_response) > 0


@pytest.mark.anyio
@pytest.mark.run(order=10)
async def test_create_stdpatientcondition_all_fields(
    client                      : AsyncClient,
    token                       : str,
    patient_cpf                 : str,
    patientcondition_raw_source : str
):
    response = await client.post(
        "/std/patientconditions",
        headers={"Authorization": f"Bearer {token}"},
        json = [
                {
                    "patient_cpf": patient_cpf,
                    "patient_code": f"{patient_cpf}.20000111",
                    "cid": "A001",
                    "clinical_status": "resolved",
                    "category": "encounter-diagnosis",
                    "date": "2024-01-11T16:20:09.832Z",
                    "raw_source_id": patientcondition_raw_source
                },
                {
                    "patient_cpf": patient_cpf,
                    "patient_code": f"{patient_cpf}.20000111",
                    "cid": "A001",
                    "clinical_status": "not_resolved",
                    "category": "encounter-diagnosis",
                    "date": "2024-01-11T16:20:09.832Z",
                    "raw_source_id": patientcondition_raw_source
                }
            ]
    )

    assert response.status_code == 201
    assert response.json()['count'] == 2


@pytest.mark.anyio
@pytest.mark.run(order=10)
async def test_create_stdpatientcondition_mandatory_fields(
    client                      : AsyncClient,
    token                       : str,
    patient_cpf                 : str,
    patientcondition_raw_source : str
):
    response = await client.post(
        "/std/patientconditions",
        headers={"Authorization": f"Bearer {token}"},
        json = [
                {
                    "patient_cpf": patient_cpf,
                    "patient_code": f"{patient_cpf}.20000111",
                    "cid": "A001",
                    "date": "2024-01-11T16:20:09.832Z",
                    "raw_source_id": patientcondition_raw_source
                }
            ]
    )

    assert response.status_code == 201


@pytest.mark.anyio
@pytest.mark.run(order=10)
async def test_create_stdpatientcondition_invalid_raw_source(
    client                      : AsyncClient,
    token                       : str,
    patient_cpf                 : str
):
    response = await client.post(
        "/std/patientconditions",
        headers={"Authorization": f"Bearer {token}"},
        json = [
                {
                    "patient_cpf": patient_cpf,
                    "patient_code": f"{patient_cpf}.20000111",
                    "cid": "A001",
                    "date": "2024-01-11T16:20:09.832Z",
                    "raw_source_id": "407a48a7-fc53-4ab1-8e18-dbd5c9ebfdbe"
                }
            ]
    )

    assert response.status_code == 404

@pytest.mark.anyio
@pytest.mark.run(order=10)
async def test_create_stdpatientcondition_cpfmismatch(
    client                              : AsyncClient,
    token                               : str,
    patient_cpf                         : str,
    other_patientcondition_raw_source   : str
):
    response = await client.post(
        "/std/patientconditions",
        headers={"Authorization": f"Bearer {token}"},
        json = [
                {
                    "patient_cpf": patient_cpf,
                    "patient_code": f"{patient_cpf}.20000111",
                    "cid": "A001",
                    "date": "2024-01-11T16:20:09.832Z",
                    "raw_source_id": other_patientcondition_raw_source
                }
            ]
    )

    assert response.status_code == 400


@pytest.mark.anyio
@pytest.mark.run(order=10)
async def test_create_stdpatientcondition_invalid_conditioncode(
    client                      : AsyncClient,
    token                       : str,
    patient_cpf                 : str,
    patientcondition_raw_source : str
):
    response = await client.post(
        "/std/patientconditions",
        headers={"Authorization": f"Bearer {token}"},
        json = [
                {
                    "patient_cpf": patient_cpf,
                    "patient_code": f"{patient_cpf}.20000111",
                    "cid": "ERROR",
                    "date": "2024-01-11T16:20:09.832Z",
                    "raw_source_id": patientcondition_raw_source
                }
            ]
    )

    assert response.status_code == 404

@pytest.mark.anyio
@pytest.mark.run(order=11)
async def test_read_stdpatientconditions(
    client      : AsyncClient,
    token       : str,
    patient_cpf : str
):
    response = await client.get(
        f"/std/patientconditions?patient_cpf={patient_cpf}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    json_response = response.json()
    assert len(json_response) > 0