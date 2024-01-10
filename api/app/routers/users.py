# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from tortoise.contrib.pydantic import pydantic_model_creator

from app.dependencies import get_current_active_user
from app.models import User
from app.utils import password_hash

router = APIRouter(prefix="/users", tags=["users"])

UserCreateInput = pydantic_model_creator(
    User, name="UserCreateInput", exclude=["id", "is_active", "created_at", "updated_at"]
)

UserCreateOutput = pydantic_model_creator(User, name="UserOutput", exclude=["id", "password"])

UserUpdateInput = pydantic_model_creator(
    User, name="UserUpdateInput", exclude=["id", "created_at", "updated_at"]
)


@router.post("", response_model=UserCreateOutput, status_code=201)
async def create_user(
    current_user: Annotated[User, Depends(get_current_active_user)], user_input: UserCreateInput
) -> UserCreateOutput:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="You don't have permission to do this.")
    user_input_data = user_input.model_dump()
    user_input_data["password"] = password_hash(user_input_data["password"])
    user = await User.create(**user_input_data)
    return await UserCreateOutput.from_tortoise_orm(user)


@router.get("/me", response_model=UserCreateOutput)
async def read_my_user(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@router.get("/{user_id}", response_model=UserCreateOutput)
async def read_user(
    current_user: Annotated[User, Depends(get_current_active_user)], user_id: int
) -> UserCreateOutput:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="You don't have permission to do this.")
    user = await User.get(id=user_id)
    return await UserCreateOutput.from_tortoise_orm(user)


@router.patch("/{user_id}", response_model=UserCreateOutput)
async def update_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_id: int,
    user_input: UserUpdateInput,
) -> UserCreateOutput:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="You don't have permission to do this.")
    user = await User.get(id=user_id)
    user_input_data = user_input.model_dump()
    user_input_data["password"] = password_hash(user_input_data["password"])
    await user.update_from_dict(user_input_data).save()
    return await UserCreateOutput.from_tortoise_orm(user)


@router.delete("/{user_id}")
async def delete_user(
    current_user: Annotated[User, Depends(get_current_active_user)], user_id: int
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="You don't have permission to do this.")
    await User.filter(id=user_id).delete()
    return {"message": "User deleted successfully."}
