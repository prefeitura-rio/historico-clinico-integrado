# -*- coding: utf-8 -*-
import json
from functools import wraps
from typing import Any, Dict, Optional, Union

from fastapi import APIRouter, HTTPException, Request, status

from app.models import User, UserHistory


def router_request(
    *,
    method: str,
    router: APIRouter,
    path: str,
    response_model: Any = None,
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
):
    def decorator(f):
        router_method = getattr(router, method.lower())
        if not router_method:
            raise AttributeError(f"Method {method} is not valid.")

        @router_method(path=path, response_model=response_model, responses=responses)
        @wraps(f)
        async def wrapper(*args, **kwargs):
            user: User = None
            if "user" not in kwargs:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="The user dependency is missing. This is a bug. Please report it.",
                )
            user = kwargs["user"]
            request: Request = None
            if "request" not in kwargs:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="The request dependency is missing. This is a bug. Please report it.",
                )
            request = kwargs["request"]
            full_path = router.prefix + path
            # Format the path with jinja parameters
            for key, value in kwargs.items():
                full_path = full_path.replace(f"{{{key}}}", str(value))
            query_params = dict(request.query_params)
            if method == "GET":
                body = None
            else:
                body_bytes = await request.body()
                body_str = body_bytes.decode()
                if body_str:
                    body = json.loads(body_str)
                else:
                    body = None
            try:
                response = await f(*args, **kwargs)
                await UserHistory.create(
                    user=user,
                    method=request.method,
                    path=full_path,
                    query_params=query_params,
                    body=body,
                    status_code=200,
                )
                return response
            except HTTPException as exc:
                await UserHistory.create(
                    user=user,
                    method=request.method,
                    path=full_path,
                    query_params=query_params,
                    body=body,
                    status_code=exc.status_code,
                )
                raise exc

        return wrapper

    return decorator