# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from tortoise.contrib.pydantic import pydantic_model_creator

from app.dependencies import get_current_active_user
from app.models import (
    User, DataSource
)

DataSourceInput = pydantic_model_creator(DataSource, name="DataSourceInput", exclude=("id",))
DataSourceOutput = pydantic_model_creator(DataSource, name="DataSourceOutput")


router = APIRouter(prefix="/mrg", tags=["Entidades MRG (Formato Merged/Fundido)"])


@router.get("/data_source", response_model=list[DataSourceOutput])
async def get_address_types(
    _: Annotated[User, Depends(get_current_active_user)],
) -> list[DataSourceOutput]:
    return await DataSourceOutput.from_queryset(DataSource.all())

@router.post("/data_source", response_model=DataSourceOutput, status_code=201)
async def create_address_type(
    _: Annotated[User, Depends(get_current_active_user)],
    datasource: DataSourceInput,
) -> DataSourceOutput:
    try:
        datasource_instance = await DataSource.create(**datasource.dict(exclude_unset=True))
        return await DataSourceOutput.from_tortoise_orm(datasource_instance)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="ENUM field Data not Compatible",
        )