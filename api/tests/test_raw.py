# -*- coding: utf-8 -*-
from httpx import AsyncClient  # noqa
import pytest  # noqa

import sys
sys.path.insert(0, "../")



@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_post_rawpatientrecord(client: AsyncClient, token: str, patient_cpf: str):
    response = await client.post(
        "/raw/patientrecords",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "data_list": [
                {
                    "patient_cpf": patient_cpf,
                    "data": {"name":"Teste"}
                }
            ],
            "cnes": "1234567"
        }
    )

    assert response.status_code == 201
    assert response.json()['count'] == 1


@pytest.mark.anyio
@pytest.mark.run(order=2)
async def test_get_rawpatientrecords(client: AsyncClient, token: str):
    response = await client.get(
        "/raw/patientrecords",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    json_response = response.json()
    assert len(json_response) > 0


@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_post_rawpatientcondition(client: AsyncClient, token: str, patient_cpf: str):
    response = await client.post(
        "/raw/patientconditions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "data_list": [
                {
                    "patient_cpf": patient_cpf,
                    "data": {"name":"Teste"}
                }
            ],
            "cnes": "1234567"
        }
    )

    assert response.status_code == 201
    assert response.json()['count'] == 1

@pytest.mark.anyio
@pytest.mark.run(order=2)
async def test_get_rawpatientconditions(client: AsyncClient, token: str):
    response = await client.get(
        "/raw/patientconditions",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    json_response = response.json()
    assert len(json_response) > 0
