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
        data={"username": username, "password": password}
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
async def test_read_patient(client: AsyncClient, token: str, patient_cpf: str):
    response = await client.get(
        f"/mrg/patient/{patient_cpf}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    first_patient = response.json()[0]

    assert 'gender' in first_patient
    assert 'nationality' in first_patient
    assert 'race' in first_patient
    assert 'birth_city' in first_patient
    assert 'birth_state' in first_patient
    assert 'birth_country' in first_patient
    assert 'address_list' in first_patient
    assert 'telecom_list' in first_patient
    assert 'cns_list' in first_patient


@pytest.mark.anyio
@pytest.mark.run(order=10)
async def test_create_or_update_mrgpatient_all_fields(
    client: AsyncClient,
    token: str,
    patient_cpf: str
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
            "race": "parda"
        }]
    )

    assert response.json() > 0
    assert response.status_code == 200


@pytest.mark.anyio
@pytest.mark.run(order=10)
async def test_create_or_update_mrgpatient_invalid_cpf(
    client: AsyncClient,
    token: str,
    patient_invalid_cpf: str
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
            "race": "parda"
        }]
    )

    assert response.status_code == 400


@pytest.mark.anyio
@pytest.mark.run(order=11)
async def test_create_or_update_mrgaddress(
    client: AsyncClient,
    token: str,
    patient_code: str
):

    response = await client.put(
        "/mrg/patientaddress",
        headers={"Authorization": f"Bearer {token}"},
        json=[
            {
                "city": "00001",
                "line": "AVENIDA ABELARDO, 141",
                "postal_code": "21860390",
                "patient_code": patient_code
            }
        ]
    )

    assert response.status_code == 200

@pytest.mark.anyio
@pytest.mark.run(order=11)
async def test_create_or_update_mrgtelecom(
    client: AsyncClient,
    token: str,
    patient_code: str
):

    response = await client.put(
        "/mrg/patienttelecom",
        headers={"Authorization": f"Bearer {token}"},
        json=[
            {
                "value": "21977741695",
                "system": "phone",
                "patient_code": patient_code
            }
        ]
    )

    assert response.status_code == 200

@pytest.mark.anyio
@pytest.mark.run(order=11)
async def test_create_or_update_mrgcns(
    client: AsyncClient,
    token: str,
    patient_code: str
):

    response = await client.put(
        "/mrg/patientcns",
        headers={"Authorization": f"Bearer {token}"},
        json=[
            {
                "value": "898092209631527",
                "is_main": False,
                "patient_code": patient_code
            }
        ]
    )

    assert response.status_code == 200
