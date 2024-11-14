import datetime
from typing import Any, AsyncGenerator, Callable, Dict, Tuple
from logger import logger

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_

from middleware.mysql.models.session import SessionSchema
from middleware.mysql.models.users import UserSchema
from middleware.mysql import session
from routes.model.request import CreateSessionRequest
from routes.model.response import StandardResponse
from ...auth.oauth import jwt_auth
from middleware.redis import r

session_router = APIRouter(prefix="/session", tags=["session"])


'''get session list'''
@session_router.get("/sessionlist", response_model=StandardResponse, dependencies=[Depends(jwt_auth)])
async def get_session(page_id:int,page_size:int,info: Tuple[int, int] = Depends(jwt_auth)) -> StandardResponse:
    uid,_=info
    logger.info(f"uid:{uid},page_id:{page_id},page_size:{page_size}")
    with session() as conn:
        user = conn.query(UserSchema).filter(UserSchema.uid == uid).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not conn.is_active:
            conn.rollback()
            conn.close()
        else:
            conn.commit()

        query=(
            conn.query(SessionSchema.sid,SessionSchema.sessionname,SessionSchema.update_at)
            .filter(SessionSchema.uid==uid)
            .filter(SessionSchema.delete_at==None)
            .order_by(SessionSchema.update_at.desc())
            .offset(page_id*page_size)
        )
        res=query.limit(page_size).all()

    session_list=[{
            "sid":sid,
            "sessionname":str(sessionname),
            "update_at":str(update_at),
        }for sid,sessionname,update_at in res]

    data={"session_list":session_list}
    return StandardResponse(code=0, status="success", data=data)
        


        
    

    
'''create session'''
@session_router.post("", response_model=StandardResponse, dependencies=[Depends(jwt_auth)])
async def create_session(request: CreateSessionRequest,info: Tuple[int, int] = Depends(jwt_auth)) -> StandardResponse:
    uid,_=info
    logger.info(f"uid:{uid},sessionname:{request.sessionname}")
    with session() as conn:
        user = conn.query(UserSchema).filter(UserSchema.uid == uid).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not conn.is_active:
            conn.rollback()
            conn.close()
        else:
            conn.commit()

        _session = SessionSchema(uid=uid, sessionname=request.sessionname)
        conn.add(_session)
        conn.commit()

        data = {"sessionname": _session.sessionname, "create_at": _session.create_at}
    return StandardResponse(code=0, status="success", data=data)







'''delete session'''
@session_router.delete("/{sessionname}/delete", response_model=StandardResponse, dependencies=[Depends(jwt_auth)])
async def delete_session(sessionname:str,info: Tuple[int, int] = Depends(jwt_auth)) -> StandardResponse:
    uid,_=info
    logger.info(f"uid:{uid},sessionname:{sessionname}")
    with session() as conn:
        user = conn.query(UserSchema).filter(UserSchema.uid == uid).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not conn.is_active:
            conn.rollback()
            conn.close()
        else:
            conn.commit()

        query=(
            conn.query(SessionSchema)
            .filter(SessionSchema.sessionname==sessionname)
            .filter(SessionSchema.uid==uid)
            .filter(SessionSchema.delete_at==None)
        )
        res=query.first()
        if not res:
            raise HTTPException(status_code=404, detail="Session not found")
        res.delete_at=datetime.datetime.now()
        conn.commit()

    return StandardResponse(code=0, status="success", message="Session deleted successfully")







