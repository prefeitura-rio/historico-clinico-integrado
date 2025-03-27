import httpx
import json
from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from typing import Annotated
from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime
from loguru import logger

from app.dependencies import get_current_user
from app.config import base as config
from app.models import User


router = APIRouter(prefix="/raw", tags=["Raw"])

class RawDataModel(BaseModel):
    id: Optional[int]
    patient_cpf: str
    patient_code: str
    source_updated_at: datetime
    source_id: Optional[str]
    data: dict

class RawDataListModel(BaseModel):
    data_list: List[RawDataModel]
    cnes: str


@router.post("/{entity_name}")
async def load_data(
    _: Annotated[User, Depends(get_current_user)],
    entity_name: Literal["patientrecords", "encounter"],
    raw_data: RawDataListModel
):
    if entity_name == "patientrecords":
        entity_name = "paciente"
    elif entity_name == "encounter":
        entity_name = "atendimento"

    async with httpx.AsyncClient() as client:
        logger.info(f"Getting token from datalake hub...")
        response = await client.post(
            url=f"{config.DATALAKE_HUB_URL}auth/token",
            headers={
                "accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "password",
                "username": config.DATALAKE_HUB_USERNAME,
                "password": config.DATALAKE_HUB_PASSWORD,
            },
            timeout=90
        )

        if response.status_code != 200:
            raise JSONResponse(
                status_code=response.status_code,
                content={
                    "message": "Failed to get token from datalake hub",
                    "content": response.json()
                }
            )

        token = response.json().get("access_token")

        logger.info(f"Sending data to datalake hub...")
        response = await client.post(
            url=f"{config.DATALAKE_HUB_URL}vitacare/{entity_name}",
            headers={
                "Authorization": f"Bearer {token}"
            },
            json=json.loads(raw_data.json()),
            timeout=90
        )

    return JSONResponse(
        status_code=response.status_code,
        content=response.json()
    )