from fastapi import APIRouter

from .key import key_router
from .session import session_router

v1_router = APIRouter(prefix="/v1", tags=["v1"])

v1_router.include_router(key_router)
v1_router.include_router(session_router)
