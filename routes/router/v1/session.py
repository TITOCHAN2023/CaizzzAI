from datetime import datetime
from typing import Any, AsyncGenerator, Callable, Dict, Tuple
from logger import logger

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
from langchain_caizzz.chain import caizzzchat
from langchain_caizzz.memory import init_memory
from langchain.memory import ConversationBufferWindowMemory
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







'''get session history'''
@session_router.get("/{sessionname}", response_model=StandardResponse, dependencies=[Depends(jwt_auth)])
async def get_session(sessionname: str, info: Tuple[int, int] = Depends(jwt_auth)):
    uid, _ = info


    with session() as conn:
        if not conn.is_active:
            conn.rollback()
            conn.close()
        else:
            conn.commit()

        query = (
            conn.query(SessionSchema.sid,SessionSchema.sessionname, SessionSchema.create_at, SessionSchema.update_at)
            .filter(SessionSchema.sessionname == sessionname)
            .filter(SessionSchema.uid == uid)
            .filter(or_(SessionSchema.delete_at.is_(None), datetime.now() < SessionSchema.delete_at))
        )
        result = query.first()

        session_id = result.sid


        query = (
            conn.query(historySchema.hid,historySchema.create_at,historySchema.usermessage, historySchema.botmessage,historySchema.llm_model,historySchema.user_api_key,historySchema.user_base_url)
                .filter(historySchema.sid == session_id)
                .filter(or_(historySchema.is_deleted.is_(None), historySchema.is_deleted == False))
                .order_by(historySchema.create_at.desc())
                )
        
        results = query.all()
        data = {
            "sessionname": result.sessionname,
            "create_at": str(result.create_at),
            "update_at": str(result.update_at),
            "history": [
                {
                    "hid": hid,
                    "create_at": str(create_at),
                    "usermessage": usermessage,
                    "botmessage": botmessage,
                    "llm_model": llm_model,
                    "user_api_key": user_api_key,
                    "user_base_url": user_base_url
                }
                for hid,create_at,usermessage,botmessage,llm_model,user_api_key,user_base_url in results
            ]
        }


        
        history_input = [usermessage for _, _, usermessage, _, _, _, _ in results]
        history_output = [botmessage for _, _, _, botmessage, _, _, _ in results]
        if history_input and history_output:
            for human_message, ai_response in zip(history_input, history_output):
                r.rpush(f"{uid}{sessionname}:input", human_message)
                r.rpush(f"{uid}{sessionname}:output", ai_response)
        


    return StandardResponse(code=0, status="success", data=data)







'''post user message'''
@session_router.post("/{sessionname}/chat", response_model=StandardResponse, dependencies=[Depends(jwt_auth)])
async def post_user_message(sessionname: str, req : ChatRequest, request:Request,info: Tuple[int, int] = Depends(jwt_auth)) -> StandardResponse:
    uid,_=info
    logger.info(f"uid:{uid},sessionname:{sessionname},message:{req}")

    llm=init_llm(req.llm_model,req.base_url,req.api_key,req.temperature)
    client_ip = request.client.host
    with session() as conn:
        if not conn.is_active:
            conn.rollback()
            conn.close()
        else:
            conn.commit()

        query=(
            conn.query(SessionSchema.sid,SessionSchema.sessionname, SessionSchema.create_at, SessionSchema.update_at)
            .filter(SessionSchema.sessionname == sessionname)
            .filter(SessionSchema.uid == uid)
            .filter(or_(SessionSchema.delete_at.is_(None), datetime.now() < SessionSchema.delete_at))
        )
        result = query.first()
        session_id = result.sid

        botmessage = caizzzchat(llm,str(uid)+sessionname,uid,req.message,req.vector_db_id)

        history = historySchema(
            sid=session_id,
            usermessage=req.message,
            botmessage=botmessage,
            ip=client_ip,
            llm_model=req.llm_model,
            user_api_key=req.api_key,
            user_base_url=req.base_url
        )
        conn.add(history)
        conn.commit()

    return StandardResponse(code=0, status="success", data={"botmessage": botmessage})



