# -*- coding: utf-8 -*-

from fastapi import APIRouter
from app.auth.routers.govbr import router as auth_govbr
from app.auth.routers.default import router as auth_default

router = APIRouter(prefix="/auth", tags=["Autenticação"])

router.include_router(auth_govbr)
router.include_router(auth_default)
