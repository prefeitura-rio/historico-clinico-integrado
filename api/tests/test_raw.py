# -*- coding: utf-8 -*-
from httpx import AsyncClient  # noqa
import pytest  # noqa
import datetime
import sys
sys.path.insert(0, "../")



@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_create_rawpatientrecord(
    client              : AsyncClient,
    token               : str,
    patient_cpf         : str,
):
    response = await client.post(
        "/raw/patientrecords",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "data_list": [
                {
                    "patient_code": f"{patient_cpf}.19970607",
                    "patient_cpf": patient_cpf,
                    "data": {"name":"Teste"}
                },
                {
                    "patient_code": f"{patient_cpf}.19970607",
                    "patient_cpf": patient_cpf,
                    "data": {"name":"Teste"}
                }
            ],
            "cnes": "1234567"
        }
    )

    assert response.status_code == 201
    assert response.json()['count'] == 2


@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_create_rawpatientrecord_invalid_cpf(
    client                      : AsyncClient,
    token                       : str,
    patient_invalid_cpf         : str
):
    response = await client.post(
        "/raw/patientrecords",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "data_list": [
                {
                    "patient_code": f"{patient_invalid_cpf}.19970607",
                    "patient_cpf": patient_invalid_cpf,
                    "data": {"name":"Teste"}
                }
            ],
            "cnes": "1234567"
        }
    )

    assert response.status_code == 400



@pytest.mark.anyio
@pytest.mark.run(order=2)
async def test_read_rawpatientrecords(
    client: AsyncClient,
    token: str
):

    response = await client.get(
        "/raw/patientrecords",
        headers={"Authorization": f"Bearer {token}"},
        params={
            'start_datetime':datetime.datetime.now() - datetime.timedelta(hours=24),
            'end_datetime':datetime.datetime.now() + datetime.timedelta(hours=24)
        }
    )

    assert response.status_code == 200

    json_response = response.json()
    assert len(json_response) > 0


@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_create_rawpatientcondition(
    client      : AsyncClient,
    token       : str,
    patient_cpf : str
):
    response = await client.post(
        "/raw/patientconditions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "data_list": [
                {
                    "patient_code": f"{patient_cpf}.19970607",
                    "patient_cpf": patient_cpf,
                    "data": {"name":"Teste"}
                },
                {
                    "patient_code": f"{patient_cpf}.19970607",
                    "patient_cpf": patient_cpf,
                    "data": {"name":"Teste"}
                }
            ],
            "cnes": "1234567"
        }
    )

    assert response.status_code == 201
    assert response.json()['count'] == 2


@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_create_rawpatientcondition_invalid_cpf(
    client                      : AsyncClient,
    token                       : str,
    patient_invalid_cpf         : str,
    patient_cpf                 : str
):
    response = await client.post(
        "/raw/patientconditions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "data_list": [
                {
                    "patient_code": f"{patient_invalid_cpf}.19970607",
                    "patient_cpf": patient_invalid_cpf,
                    "data": {"name":"Teste"}
                },
                {
                    "patient_code": f"{patient_cpf}.19970607",
                    "patient_cpf": patient_cpf,
                    "data": {"name":"Teste"}
                }
            ],
            "cnes": "1234567"
        }
    )

    assert response.status_code == 400


@pytest.mark.anyio
@pytest.mark.run(order=2)
async def test_read_rawpatientconditions(
    client  : AsyncClient,
    token   : str
):
    response = await client.get(
        "/raw/patientconditions",
        headers={"Authorization": f"Bearer {token}"},
        params={
            'start_datetime':datetime.datetime.now() - datetime.timedelta(hours=24),
            'end_datetime':datetime.datetime.now() + datetime.timedelta(hours=24)
        }
    )

    assert response.status_code == 200

    json_response = response.json()
    assert len(json_response) > 0
