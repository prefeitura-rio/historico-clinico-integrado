# -*- coding: utf-8 -*-
from httpx import AsyncClient  # noqa
import pytest  # noqa

import sys
sys.path.insert(0, "../")



@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_post_rawpatientrecord(client: AsyncClient, token: str, patient_cpf: str):
    response = await client.post(
        "/raw/patientrecord",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "patient_cpf": patient_cpf,
            "data": {
                "name" : "Teste",
                "address": "Rua 1, 3000, 22222222, Rio de Janeiro, RJ, Brasil"
            }
        }
    )

    assert response.status_code == 201
    assert 'id' in response.json()


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
        "/raw/patientcondition",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "patient_cpf": patient_cpf,
            "data": {
                "code" : "A001",
                "status": "resolved"
            }
        }
    )

    assert response.status_code == 201
    assert 'id' in response.json()

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