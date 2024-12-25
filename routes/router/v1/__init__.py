from fastapi import APIRouter

from .key import key_router
from .session import session_router
from .vdb import vdb_router
from .podcastfy import podcast_router

v1_router = APIRouter(prefix="/v1", tags=["v1"])

v1_router.include_router(key_router)
v1_router.include_router(session_router)
v1_router.include_router(vdb_router)
v1_router.include_router(podcast_router)
