from datetime import datetime
from typing import Any, AsyncGenerator, Callable, Dict, Tuple
from logger import logger
import json

from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, HTTPException, Request

from sqlalchemy import or_

from middleware.mysql.models.history import historySchema
from middleware.mysql.models.session import SessionSchema
from middleware.mysql.models.users import UserSchema
from middleware.mysql import session
from routes.model.request import CreateSessionRequest,ChatRequest
from routes.model.response import StandardResponse
from ...auth.oauth import jwt_auth
from middleware.redis import r

from langchain_caizzz.llm import init_llm
from langchain_caizzz.chain import caizzzchain


session_router = APIRouter(prefix="/vdb", tags=["vdb"])



