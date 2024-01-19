# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends
from tortoise.contrib.pydantic import pydantic_model_creator

from app.dependencies import get_current_active_user
from app.pydantic_models import UserRegisterInputModel, UserRegisterOutputModel
from app.utils import password_hash
from app.models import (
    User, DataSource
)

DataSourceInput = pydantic_model_creator(DataSource, name="DataSourceInput", exclude=("id",))
DataSourceOutput = pydantic_model_creator(DataSource, name="DataSourceOutput")


router = APIRouter(prefix="/outros", tags=["Outras Entidades"])


@router.post("/user", status_code=201)
async def create_user(
    _       : Annotated[User, Depends(get_current_active_user)],
    user    : UserRegisterInputModel,
) -> UserRegisterOutputModel:

    user_data = user.dict()
    datasource_data = user_data.pop('data_source')

    datasource_instance, _ = await DataSource.get_or_create(
        system = datasource_data['system'],
        cnes = datasource_data['cnes'],
        description = datasource_data['description']
    )

    user_data['password']       = password_hash(user_data['password'])
    user_data['data_source']    = datasource_instance

    user_instance = await User.create(**user_data)

    output = {
        **dict(user_instance),
        'data_source': dict(datasource_instance)
    }

    return output
