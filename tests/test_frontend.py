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
    cpf_with_header: str,
):
    response = await client.get(
        f"/frontend/patient/header?cpf={cpf_with_header}",
        headers={"Authorization": f"Bearer {token_frontend}"}
    )

    assert response.status_code == 200


@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_patientsummary(
    client: AsyncClient,
    token_frontend: str,
    cpf_with_summary: str,
):
    response = await client.get(
        f"/frontend/patient/summary?cpf={cpf_with_summary}",
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
        f"/frontend/patient/filter_tags",
        headers={"Authorization": f"Bearer {token_frontend}"}
    )

    assert response.status_code == 200


@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_patientencounters(
    client: AsyncClient,
    token_frontend: str,
    cpf_with_encounters: str,
):
    response = await client.get(
        f"/frontend/patient/encounters?cpf={cpf_with_encounters}",
        headers={"Authorization": f"Bearer {token_frontend}"}
    )

    assert response.status_code == 200
