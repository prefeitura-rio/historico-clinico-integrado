from fastapi import HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

from app import config
from app.auth.enums import LoginStatusEnum
from app.types.pydantic_models import Token
from app.auth.types import AuthenticationErrorModel
from app.auth.routers import router
from app.auth.types import LoginForm, LoginFormWith2FA
from app.auth.utils import (
    authenticate_user,
    generate_user_token
)
from app.auth.utils.email import (
    generate_2fa_code,
    store_code,
    validate_code,
    send_2fa_email_to_user
)


@router.post(
    "/2fa/email/generate-code/",
    response_model=dict,
    responses={
        401: {"model": AuthenticationErrorModel}
    }
)
async def generate_2fa_code(
    login: LoginForm
):
    result = await authenticate_user(login.username, login.password)

    if result['status'] != LoginStatusEnum.SUCCESS:
        raise JSONResponse(
            status_code=401,
            content=AuthenticationErrorModel(
                message="Something went wrong",
                type=result['status']
            ),
        )
    
    code = generate_2fa_code()
    store_code(result['user'], code)

    try:
        success = await send_2fa_email_to_user(result['user'], code)
    except Exception as e:
        logger.error(f"Error during the email sending process. {e}")
        success = False

    if not success:
        raise JSONResponse(
            status_code=401,
            content=AuthenticationErrorModel(
                message="Error during the email queueing process. Try Again.",
                type=LoginStatusEnum.EMAIL_QUEUE_ERROR
            ),
        )

    return {
        "message": "Código enviado com sucesso."
    }


@router.post(
    "/2fa/email/login/",
    response_model=Token,
    responses={
        401: {"model": AuthenticationErrorModel}
    }
)
async def login_with_2fa(
    form_data: LoginFormWith2FA,
) -> Token:

    login_result = await authenticate_user(
        username=form_data.username,
        password=form_data.password,
        code=form_data.code,
        verificator=validate_code,
    )
    logger.info(f"login_result: {login_result['status']}")

    if login_result['status'] == LoginStatusEnum.SUCCESS:
        login_result['user'].is_2fa_activated = True
        await login_result['user'].save()

        return {
            "access_token": generate_user_token(login_result['user']),
            "token_type": "bearer",
            "token_expire_minutes": int(config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        }
    else:
        return JSONResponse(
            status_code=401,
            content={
                "message": "Something went wrong",
                "type": login_result['status'],
            },
        )