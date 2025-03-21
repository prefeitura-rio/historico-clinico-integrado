# -*- coding: utf-8 -*-

from fastapi import APIRouter
from app.auth.routers.govbr import router as auth_govbr

router = APIRouter(prefix="/auth", tags=["Autenticação"])

router.include_router(auth_govbr)
