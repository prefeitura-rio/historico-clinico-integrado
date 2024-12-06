# -*- coding: utf-8 -*-

from fastapi import APIRouter
from app.auth.routers.basic import router as auth_basic
from app.auth.routers.email import router as auth_email
from app.auth.routers.totp import router as auth_totp


router = APIRouter(prefix="/auth", tags=["Autenticação"])

router.include_router(auth_basic)
router.include_router(auth_email)
router.include_router(auth_totp)
