# -*- coding: utf-8 -*-
import sys

sys.path.insert(0, "../")

import pytest  # noqa
from httpx import AsyncClient  # noqa

from .utils import generate_cns, generate_cpf  # noqa


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
@pytest.mark.run(order=2)
async def test_patient_creation__minimal(client: AsyncClient, username: str, password: str):
    response = await client.post(
        "/auth/token",
        headers={"content-type": "application/x-www-form-urlencoded"},
        data={"username": username, "password": password},
    )
    result_body = response.json()
    token = result_body.get("access_token")
    random_cpf = generate_cpf()

    response = await client.post(
        "/patients/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "active": True,
            "birth_date": "1999-12-20",
            "gender": "male",
            "cpf": random_cpf,
            "name": "MANUEL GOMES",
            "telecom": [{"value": "5521123456789"}],
        },
    )
    assert response.status_code == 201
    assert response.json() is not None
    assert "cpf" in response.json()
    assert response.json()["cpf"] == random_cpf


@pytest.mark.anyio
@pytest.mark.run(order=2)
async def test_patient_creation__complete(client: AsyncClient, username: str, password: str):
    response = await client.post(
        "/auth/token",
        headers={"content-type": "application/x-www-form-urlencoded"},
        data={"username": username, "password": password},
    )
    result_body = response.json()
    token = result_body.get("access_token")
    random_cpf = generate_cpf()
    random_cns = generate_cns()

    response = await client.post(
        "/patients/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "active": True,
            "address": [
                {
                    "use": "home",
                    "type": "physical",
                    "line": "AV SQN BLOCO M 604 APARTAMENTO ASA NORTE",
                    "city": "Rio de Janeiro",
                    "state": "Rio de Janeiro",
                    "country": "Brasil",
                    "postal_code": "70752130",
                    "period": {"start": "2020-10-01 00:00:00", "end": "2020-10-02 00:00:00"},
                }
            ],
            "birth_city": "Rio de Janeiro",
            "birth_country": "Brasil",
            "birth_state": "Rio de Janeiro",
            "birth_date": "1999-12-20 00:00:00",
            "deceased": False,
            "gender": "male",
            "cpf": random_cpf,
            "cns": random_cns,
            "name": "GABRIELA INACIO ALVES",
            "nationality": "B",
            "naturalization": "",
            "mother": "MARILIA FARES DA ROCHA ALVES",
            "father": "JURACY ALVES",
            "protected_person": False,
            "race": "Parda",
            "ethnicity": "PATAXO",
            "telecom": [
                {
                    "system": "phone",
                    "use": "home",
                    "value": "5521123456789",
                    "rank": "1",
                    "period": {"start": "2020-10-01 00:00:00", "end": "2020-10-02 00:00:00"},
                }
            ],
        },
    )
    assert response.status_code == 201
    assert response.json() is not None
    assert "cpf" in response.json()
    assert response.json()["cpf"] == random_cpf
