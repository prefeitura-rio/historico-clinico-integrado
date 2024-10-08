# -*- coding: utf-8 -*-
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from tortoise import Tortoise

from app.utils import read_bq


router = APIRouter(prefix="/misc", tags=["Miscelanous"])


@router.get(path="/health")
async def health() -> dict:
    result = {}
    # HCI DB Test
    try:
        conn = Tortoise.get_connection("default")
        await conn.execute_query("select 1 as number")
    except Exception as e:
        result["database"] = {
            "success": False,
            "error": str(e),
        }
    else:
        result["database"] = {
            "success": True,
            "error": None,
        }

    # Big Query Test
    try:
        await read_bq(query="select 1 as number")
    except Exception as e:
        result["bigquery"] = {
            "success": False,
            "error": str(e),
        }
    else:
        result["bigquery"] = {
            "success": True,
            "error": None,
        }

    result["success"] = result["bigquery"]["success"] and result["database"]["success"]

    return JSONResponse(
        content=result,
        status_code=200 if result["success"] else 503,
    )
