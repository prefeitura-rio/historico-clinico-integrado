# -*- coding: utf-8 -*-
import sys

sys.path.insert(0, "../")

import pytest  # noqa
from httpx import AsyncClient  # noqa


@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_auth(client: AsyncClient, username: str, password: str):
    response = await client.post(
        "/auth/token",
        headers={"content-type": "application/x-www-form-urlencoded"},
        data={"username": username, "password": password},
    )

    status_code = response.status_code
    assert status_code == 200

    result_body = response.json()
    assert "access_token" in result_body.keys()

    return result_body.get("access_token")

@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_auth_invalid(client: AsyncClient, username: str):
    response = await client.post(
        "/auth/token",
        headers={"content-type": "application/x-www-form-urlencoded"},
        data={"username": username, "password": "error"},
    )

    status_code = response.status_code
    assert status_code == 401


@pytest.mark.anyio
@pytest.mark.run(order=20)
async def test_read_patient(client: AsyncClient, token: str, patient_cpf : str):
    response = await client.get(
        f"/mrg/patient/{patient_cpf}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert 'gender' in response.json()
    assert 'nationality' in response.json()
    assert 'race' in response.json()
    assert 'birth_city' in response.json()
    assert 'birth_state' in response.json()
    assert 'birth_country' in response.json()
    assert 'address_list' in response.json()
    assert 'telecom_list' in response.json()
    assert 'condition_list' in response.json()
    assert 'cns_list' in response.json()


@pytest.mark.anyio
@pytest.mark.run(order=10)
async def test_create_or_update_mrgpatient_all_fields(
    client: AsyncClient,
    token: str,
    patient_cpf : str
):

    response = await client.put(
        "/mrg/patient",
        headers={"Authorization": f"Bearer {token}"},
        json=[{
            "active": True,
            "birth_city": "00001",
            "birth_state": "00001",
            "birth_country": "00001",
            "birth_date": "2000-01-11",
            "patient_cpf": patient_cpf,
            "patient_code": f"{patient_cpf}.20000111",
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
            "telecom_list": [
                {
                "system": "phone",
                "use": "home",
                "value": "32323232",
                "rank": 1,
                "period_start": "2010-10-02"
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
                    "period_start": "2010-10-02",
                    "period_end": "2013-07-11"
                }
            ]
        }]
    )

    assert response.status_code == 200
    assert len( response.json() ) > 0

@pytest.mark.anyio
@pytest.mark.run(order=10)
async def test_create_or_update_mrgpatient_mandatory_fields(
    client: AsyncClient,
    token: str,
    patient_cpf : str
):

    response = await client.put(
        "/mrg/patient",
        headers={"Authorization": f"Bearer {token}"},
        json=[{
            "birth_city": "00001",
            "birth_state": "00001",
            "birth_country": "00001",
            "birth_date": "2000-01-11",
            "patient_cpf": patient_cpf,
            "patient_code": f"{patient_cpf}.20000111",
            "gender": "male",
            "mother_name": "Gabriela Marques da Cunha",
            "name": "Fernando Marques Farias",
            "race": "parda",
            "cns_list": [],
            "telecom_list": [],
            "address_list": []
        }]
    )

    assert response.status_code == 200
    assert len( response.json() ) > 0


@pytest.mark.anyio
@pytest.mark.run(order=10)
async def test_create_or_update_mrgpatient_invalid_cpf(
    client              : AsyncClient,
    token               : str,
    patient_invalid_cpf : str
):

    response = await client.put(
        "/mrg/patient",
        headers={"Authorization": f"Bearer {token}"},
        json=[{
            "birth_city": "00001",
            "birth_state": "00001",
            "birth_country": "00001",
            "birth_date": "2000-01-11",
            "patient_cpf": patient_invalid_cpf,
            "patient_code": f"{patient_invalid_cpf}.20000111",
            "gender": "male",
            "mother_name": "Gabriela Marques da Cunha",
            "name": "Fernando Marques Farias",
            "race": "parda",
            "cns_list": [],
            "telecom_list": [],
            "address_list": []
        }]
    )

    assert response.status_code == 400


@pytest.mark.anyio
@pytest.mark.run(order=11)
async def test_create_or_update_mrgpatientcondition_all_fields(client: AsyncClient, token: str, patient_cpf : str):
    response = await client.put(
        "/mrg/patientcondition",
        headers={"Authorization": f"Bearer {token}"},
        json=[{
            "patient_cpf": patient_cpf,
            "patient_code": f"{patient_cpf}.20000111",
            "conditions": [
                {
                "code": "A001",
                "clinical_status": "resolved",
                "category": "encounter-diagnosis",
                "date": "2024-01-11T17:38:15.850Z"
                },
                {
                "code": "A001",
                "clinical_status": "not_resolved",
                "category": "encounter-diagnosis",
                "date": "2024-01-11T17:38:15.850Z"
                }
            ]
        }]
    )

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert 'id' in response.json()[0]


@pytest.mark.anyio
@pytest.mark.run(order=11)
async def test_create_or_update_mrgpatientcondition_mandatory_fields(client: AsyncClient, token: str, patient_cpf : str):
    response = await client.put(
        "/mrg/patientcondition",
        headers={"Authorization": f"Bearer {token}"},
        json=[{
            "patient_cpf": patient_cpf,
            "patient_code": f"{patient_cpf}.20000111",
            "conditions": [
                {
                "code": "A001",
                "date": "2024-01-11T17:38:15.850Z"
                }
            ]
        }]
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert 'id' in response.json()[0]


@pytest.mark.anyio
@pytest.mark.run(order=11)
async def test_create_or_update_mrgpatientcondition_invalid_cpf(
    client              : AsyncClient,
    token               : str,
    patient_invalid_cpf : str
):
    response = await client.put(
        "/mrg/patientcondition",
        headers={"Authorization": f"Bearer {token}"},
        json=[{
            "patient_cpf": patient_invalid_cpf,
            "patient_code": f"{patient_invalid_cpf}.20000111",
            "conditions": [
                {
                "code": "A001",
                "date": "2024-01-11T17:38:15.850Z"
                }
            ]
        }]
    )

    assert response.status_code == 400


@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_create_user(
    client  : AsyncClient,
    token   : str,
):
    response = await client.post(
        "/outros/user",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "testuser12",
            "password": "password_test",
            "email": "test12@email.com.br",
            "is_superuser": False,
            "data_source": {
                "system": "vitacare",
                "cnes": "11111111",
                "description": "Test Description 3"
            }
        }
    )
    print(response.json())

    status_code = response.status_code
    assert status_code == 201