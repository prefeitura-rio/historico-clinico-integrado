# -*- coding: utf-8 -*-
from httpx import AsyncClient  # noqa
import pytest  # noqa
import sys
sys.path.insert(0, "../")


@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_create_rawpatientrecord(
    client: AsyncClient,
    token_pipeline: str,
    patient_cpf: str,
):
    response = await client.post(
        "/raw/patientrecords?upload_to_datalake=false",
        headers={"Authorization": f"Bearer {token_pipeline}"},
        json={
            "data_list": [
                {
                    "patient_code": f"{patient_cpf}.19970607",
                    "patient_cpf": patient_cpf,
                    "source_updated_at": "2012-04-23T18:25:43.000Z",
                    "data": {"name": "Teste"}
                },
                {
                    "patient_code": f"{patient_cpf}.19970607",
                    "patient_cpf": patient_cpf,
                    "source_updated_at": "2012-04-22T18:25:43.000Z",
                    "data": {"name": "Teste"}
                }
            ],
            "cnes": "1234567"
        }
    )
    print("SAIDA:", response.text)

    assert response.status_code == 201
    assert response.json()['count'] == 2


@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_create_rawpatientrecord_invalid_cpf(
    client: AsyncClient,
    token_pipeline: str,
    patient_invalid_cpf: str
):
    response = await client.post(
        "/raw/patientrecords?upload_to_datalake=false",
        headers={"Authorization": f"Bearer {token_pipeline}"},
        json={
            "data_list": [
                {
                    "patient_code": f"{patient_invalid_cpf}.19970607",
                    "patient_cpf": patient_invalid_cpf,
                    "source_updated_at": "2012-04-26T18:25:43.000Z",
                    "data": {"name": "Teste"}
                }
            ],
            "cnes": "1234567"
        }
    )

    assert response.status_code == 400


@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_create_rawpatientcondition(
    client: AsyncClient,
    token_pipeline: str,
    patient_cpf: str
):
    response = await client.post(
        "/raw/patientconditions?upload_to_datalake=false",
        headers={"Authorization": f"Bearer {token_pipeline}"},
        json={
            "data_list": [
                {
                    "patient_code": f"{patient_cpf}.19970607",
                    "patient_cpf": patient_cpf,
                    "source_updated_at": "2012-04-13T00:00:00.000Z",
                    "data": {"name": "Teste"}
                },
                {
                    "patient_code": f"{patient_cpf}.19970607",
                    "patient_cpf": patient_cpf,
                    "source_updated_at": "2012-04-03T00:00:00.000Z",
                    "data": {"name": "Teste"}
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
    client: AsyncClient,
    token_pipeline: str,
    patient_invalid_cpf: str,
    patient_cpf: str
):
    response = await client.post(
        "/raw/patientconditions?upload_to_datalake=false",
        headers={"Authorization": f"Bearer {token_pipeline}"},
        json={
            "data_list": [
                {
                    "patient_code": f"{patient_invalid_cpf}.19970607",
                    "patient_cpf": patient_invalid_cpf,
                    "source_updated_at": "2012-04-21T00:00:00.000Z",
                    "data": {"name": "Teste"}
                },
                {
                    "patient_code": f"{patient_cpf}.19970607",
                    "patient_cpf": patient_cpf,
                    "source_updated_at": "2012-04-28T00:00:00.000Z",
                    "data": {"name": "Teste"}
                }
            ],
            "cnes": "1234567"
        }
    )

    assert response.status_code == 400