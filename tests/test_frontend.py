# -*- coding: utf-8 -*-
from httpx import AsyncClient  # noqa
import pytest  # noqa
import sys
sys.path.insert(0, "../")


@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_patientheader(
    client: AsyncClient,
    token_frontend: str,
    patient_cpf_with_data: str,
):
    response = await client.get(
        f"/frontend/patient/header/{patient_cpf_with_data}",
        headers={"Authorization": f"Bearer {token_frontend}"}
    )

    assert response.status_code == 200


@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_patientsummary(
    client: AsyncClient,
    token_frontend: str,
    patient_cpf_with_data: str,
):
    response = await client.get(
        f"/frontend/patient/summary/{patient_cpf_with_data}",
        headers={"Authorization": f"Bearer {token_frontend}"}
    )

    assert response.status_code == 200


@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_filtertags(
    client: AsyncClient,
    token_frontend: str,
):
    response = await client.get(
        "/frontend/patient/filter_tags",
        headers={"Authorization": f"Bearer {token_frontend}"}
    )

    assert response.status_code == 200


@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_patientencounters(
    client: AsyncClient,
    token_frontend: str,
    patient_cpf_with_data: str,
):
    response = await client.get(
        f"/frontend/patient/encounters/{patient_cpf_with_data}",
        headers={"Authorization": f"Bearer {token_frontend}"}
    )

    assert response.status_code == 200
