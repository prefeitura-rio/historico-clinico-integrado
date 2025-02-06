# -*- coding: utf-8 -*-
import httpx
import jwt
from fastapi import HTTPException
from fastapi import APIRouter

from app import config
from app.models import User
from app.types import Token
from app.utils import employee_verify
from app.auth.types import LoginFormGovbr
from app.auth.types import AuthenticationErrorModel
from app.auth.utils import generate_user_token


router = APIRouter(prefix="/govbr")


@router.post(
    "/login/",
    response_model=Token,
    responses={
        401: {"model": AuthenticationErrorModel}
    },
)
async def login_with_govbr(
    form_data: LoginFormGovbr,
) -> Token:
    
    # -----------------------------
    # GET THE ACCESS TOKEN
    # -----------------------------
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{config.GOVBR_PROVIDER_URL}/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {config.GOVBR_CLIENT_ID}:{config.GOVBR_CLIENT_SECRET}",
            },
            data={
                "grant_type": "authorization_code",
                "code": form_data.code,
                "redirect_uri": config.GOVBR_REDIRECT_URL,
                "code_verifier": form_data.code_verifier,
            },
        )
        response.raise_for_status()

    # -----------------------------
    # VALIDATE THE ID_TOKEN
    # -----------------------------

    # Get keys from the jwk endpoint
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{config.GOVBR_PROVIDER_URL}/jwk",
        )
        response.raise_for_status()
    keys = response.json()['keys']

    # Validate the id_token
    payload = jwt.decode(form_data.id_token, keys, algorithms=["RS256"])

    # -----------------------------
    # LOGIN
    # -----------------------------
    name, cpf = payload['name'], payload['sub']
    user = await User.objects.get_or_none(cpf=cpf)

    if not user:
        # TODO: Create a new user
        raise HTTPException(status_code=401, detail=f"User {name} not found with this CPF {cpf}")

    is_employee = await employee_verify(user)
    if not is_employee:
        raise HTTPException(status_code=401, detail=f"User {name} is not an employee")

    return {
        "access_token": generate_user_token(user),
        "token_type": "bearer",
        "token_expire_minutes": int(config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }


