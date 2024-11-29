import datetime
from typing import Tuple

from fastapi import APIRouter, Depends
from sqlalchemy import or_

from ...model.response import StandardResponse
from ...auth.jwt import jwt_auth
from logger import logger

key_router = APIRouter(prefix="/key", tags=["key"])




@key_router.get("", response_model=StandardResponse, dependencies=[Depends(jwt_auth)])
def generate_api_key(info: Tuple[int, int] = Depends(jwt_auth)) -> StandardResponse:
    return StandardResponse(
        code=0,
        status="success",
        message="API key generated successfully",
    )
