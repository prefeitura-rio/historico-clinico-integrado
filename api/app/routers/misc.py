# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, status


router = APIRouter(prefix="/misc", tags=["Outros"])


@router.post("/erro-interno")
async def trigger_intern_error():
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Erro interno",
    )
