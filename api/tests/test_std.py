# -*- coding: utf-8 -*-
import sys

sys.path.insert(0, "../")

import pytest  # noqa
from httpx import AsyncClient  # noqa


@pytest.mark.anyio
@pytest.mark.run(order=10)
async def test_post_stdpatientrecord(client: AsyncClient, token: str, patient_cpf : str, patientrecord_raw_source: str):
    response = await client.post(
        "/std/patientrecord",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "active": True,
            "birth_city": "Rio de Janeiro",
            "birth_state": "Rio de Janeiro",
            "birth_country": "Brasil",
            "birth_date": "2000-01-11",
            "patient_cpf": patient_cpf,
            "deceased": False,
            "deceased_date": "2024-01-11",
            "father_name": "João Cardoso Farias",
            "gender": "male",
            "mother_name": "Gabriela Marques da Cunha",
            "name": "Fernando Marques Farias",
            "nationality": "B",
            "naturalization": "n",
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
    )

    assert response.status_code == 201
    assert 'id' in response.json()

@pytest.mark.anyio
@pytest.mark.run(order=11)
async def test_get_stdpatientrecords(client: AsyncClient, token: str):
    response = await client.get(
        "/raw/patientrecords",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    json_response = response.json()
    assert len(json_response) > 0

@pytest.mark.anyio
@pytest.mark.run(order=10)
async def test_post_stdpatientcondition(client: AsyncClient, token: str, patient_cpf : str, patientcondition_raw_source: str):
    response = await client.post(
        "/std/patientcondition",
        headers={"Authorization": f"Bearer {token}"},
        json={
                "patient_cpf": patient_cpf,
                "cid": "A001",
                "ciap": None,
                "clinical_status": "resolved",
                "category": "encounter-diagnosis",
                "date": "2024-01-11T16:20:09.832Z",
                "raw_source_id": patientcondition_raw_source
            }
    )

    assert response.status_code == 201
    assert 'id' in response.json()

@pytest.mark.anyio
@pytest.mark.run(order=11)
async def test_get_stdpatientconditions(client: AsyncClient, token: str):
    response = await client.get(
        "/raw/patientconditions",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    json_response = response.json()
    assert len(json_response) > 0