from datetime import datetime
from typing import Any, AsyncGenerator, Callable, Dict, Tuple
from env import FAISS_INDEX_PATH
from langchain_caizzz.embedding import init_embedding
from langchain_caizzz.faiss import load_faiss_index
from logger import logger
import json

from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, HTTPException, Request

from sqlalchemy import or_

from middleware.hash.hash import hash_string
from middleware.mysql.models.history import historySchema
from middleware.mysql.models.chat_session import ChatSessionSchema
from middleware.mysql.models.users import UserSchema
from middleware.mysql import session
from routes.model.request import CreateSessionRequest,ChatRequest
from routes.model.response import StandardResponse
from ...auth.jwt import jwt_auth
from middleware.redis import r

from langchain_caizzz.llm import init_llm
from langchain_caizzz.chain import caizzzchain


session_router = APIRouter(prefix="/session", tags=["session"])


'''get session list'''
@session_router.get("/sessionlist", response_model=StandardResponse, dependencies=[Depends(jwt_auth)])
async def get_session(page_id:int,page_size:int,info: Tuple[int, int] = Depends(jwt_auth)) -> StandardResponse:
    uid,_=info
    logger.info(f"uid:{uid},page_id:{page_id},page_size:{page_size}")

    if r.exists(f"{uid}_session_list"):
        session_list = r.lrange(f"{uid}_session_list", page_id*page_size, (page_id+1)*page_size-1)
        data = {
            "session_list": [
                {
                    "sid": i,
                    "sessionname": session_name,
                    "update_at": ""
                }
                for i, session_name in enumerate(session_list)
            ]
        }
        return StandardResponse(code=0, status="success", data=data)

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
            conn.query(ChatSessionSchema.sid,ChatSessionSchema.sessionname,ChatSessionSchema.update_at)
            .filter(ChatSessionSchema.uid==uid)
            .filter(ChatSessionSchema.delete_at==None)
            .order_by(ChatSessionSchema.update_at.desc())
            .offset(page_id*page_size)
        )
        res=query.limit(page_size).all()

    session_list=[{
            "sid":sid,
            "sessionname":str(sessionname),
            "update_at":str(update_at),
        }for sid,sessionname,update_at in res]

    data={"session_list":session_list}

    for session_ in session_list:
        r.rpush(f"{uid}_session_list", session_["sessionname"])

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

        if request.sessionname == "":
            raise HTTPException(status_code=400, detail="Session name cannot be empty")
        
        query=(
            conn.query(ChatSessionSchema)
            .filter(ChatSessionSchema.sessionname==request.sessionname)
            .filter(ChatSessionSchema.uid==uid)
            .filter(ChatSessionSchema.delete_at==None)
        )
        if query.first():
            raise HTTPException(status_code=400, detail="Session name already exists")
        
        _session = ChatSessionSchema(uid=uid, sessionname=request.sessionname)
        conn.add(_session)
        conn.commit()

        r.lpush(f"{uid}_session_list", request.sessionname)
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
            conn.query(ChatSessionSchema)
            .filter(ChatSessionSchema.sessionname==sessionname)
            .filter(ChatSessionSchema.uid==uid)
            .filter(ChatSessionSchema.delete_at==None)
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

    if r.exists(f"{uid}{sessionname}:usermessage"):
        usermessage = r.lrange(f"{uid}{sessionname}:usermessage", 0, -1)
        botmessage = r.lrange(f"{uid}{sessionname}:botmessage", 0, -1)
        llm_model = r.get(f"{uid}{sessionname}llm_model")
        user_api_key = r.get(f"{uid}{sessionname}user_api_key")
        user_base_url = r.get(f"{uid}{sessionname}user_base_url")
        
        
        data = {
            "sessionname": sessionname,
            "create_at": "",
            "update_at": "",
            "history": [
                {
                    "hid": i,
                    "create_at": "",
                    "usermessage": usermessage[i],
                    "botmessage": botmessage[i],
                    "llm_model": llm_model,
                    "user_api_key": user_api_key,
                    "user_base_url": user_base_url
                }
                for i in range(len(usermessage))
            ]
        }
        r.set(f"{uid}_api_key", str(user_api_key))
        r.set(f"{uid}_base_url", str(user_base_url))
        return StandardResponse(code=0, status="success", data=data)

    with session() as conn:
        if not conn.is_active:
            conn.rollback()
            conn.close()
        else:
            conn.commit()

        query = (
            conn.query(ChatSessionSchema.sid,ChatSessionSchema.sessionname, ChatSessionSchema.create_at, ChatSessionSchema.update_at)
            .filter(ChatSessionSchema.sessionname == sessionname)
            .filter(ChatSessionSchema.uid == uid)
            .filter(or_(ChatSessionSchema.delete_at.is_(None), datetime.now() < ChatSessionSchema.delete_at))
        )
        result = query.first()

        session_id = result.sid


        query = (
            conn.query(historySchema.hid,historySchema.create_at,historySchema.usermessage, historySchema.botmessage,historySchema.llm_model,historySchema.user_api_key,historySchema.user_base_url)
                .filter(historySchema.sid == session_id)
                .filter(or_(historySchema.is_deleted.is_(None), historySchema.is_deleted == False))
                .order_by(historySchema.create_at.asc())
                )
        
        results = query.all()
        if not results:
            data={"history":[]}
        else:
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

        for history in data["history"]:
            r.rpush(f"{uid}{sessionname}:usermessage", history["usermessage"])
            r.rpush(f"{uid}{sessionname}:botmessage", history["botmessage"])
            if history["llm_model"]: 
                r.set(f"{uid}{sessionname}llm_model", history["llm_model"])

            if history["user_api_key"]: 
                r.set(f"{uid}{sessionname}user_api_key", history["user_api_key"])

            if history["user_base_url"]: 
                r.set(f"{uid}{sessionname}user_base_url", history["user_base_url"])

    logger.info(f"llm_model:{r.get(f'{uid}{sessionname}llm_model')},user_api_key:{r.get(f'{uid}{sessionname}user_api_key')},user_base_url:{r.get(f'{uid}{sessionname}user_base_url')}")

    return StandardResponse(code=0, status="success", data=data)





'''post user message'''
@session_router.post("/{sessionname}/chat", response_model=StandardResponse, dependencies=[Depends(jwt_auth)])
async def post_user_message(sessionname: str, req : ChatRequest, request:Request,info: Tuple[int, int] = Depends(jwt_auth)) -> StreamingResponse:
    uid,_=info
    logger.info(f"uid:{uid},sessionname:{sessionname},message:{req}")

    user_api_key = r.get(f"{uid}{sessionname}user_api_key") if req.api_key == "" else req.api_key
    user_base_url = r.get(f"{uid}{sessionname}user_base_url") if req.base_url == "" else req.base_url

    client_ip  = request.client.host

    with session() as conn:
        if not conn.is_active:
            conn.rollback()
            conn.close()
        else:
            conn.commit()

        query=(
            conn.query(ChatSessionSchema.sid,ChatSessionSchema.sessionname, ChatSessionSchema.create_at, ChatSessionSchema.update_at)
            .filter(ChatSessionSchema.sessionname == sessionname)
            .filter(ChatSessionSchema.uid == uid)
            .filter(or_(ChatSessionSchema.delete_at.is_(None), datetime.now() < ChatSessionSchema.delete_at))
        )
        result = query.first()
        session_id = result.sid


    async def generate():
        botmessage = ""

        llm=init_llm(req.llm_model,user_base_url,user_api_key,req.temperature)
        chain=caizzzchain(llm,str(uid)+sessionname)

        input_message = req.message

        if req.vdb_name:
            
            hash_vdbname = hash_string(req.vdb_name)
            index_file_path = f"{FAISS_INDEX_PATH}/index/{str(uid)}/{hash_vdbname}.index"
            mapping_file_path = f"{FAISS_INDEX_PATH}/index/{str(uid)}/{hash_vdbname}_mapping.pkl"

            embeddings = init_embedding(embeddings_name="", api_key=user_api_key, base_url=user_base_url)

            vector_store = load_faiss_index(index_file_path, mapping_file_path, embeddings)

            results = vector_store.search(req.message, search_type="similarity", k=1)

            relevant_docs = [doc.page_content for doc in results]

            context = "\n\n".join(relevant_docs)

            input_message = f"根据以下文档回复:\n{context}\n\n\nUser:{req.message}\n"
        try:
            for chunk in chain.stream({"input": input_message}):
                content = chunk.content
                botmessage += content
                # 将每个chunk转换为JSON并发送
                yield f"data: {json.dumps({'content': content})}\n\n"

            # 在完成流式传输后保存历史记录
            with session() as conn:
                history = historySchema(
                    sid=session_id,
                    create_at=datetime.now(),
                    usermessage=req.message,
                    botmessage=botmessage,
                    ip=client_ip,
                    llm_model=req.llm_model,
                    user_api_key=req.api_key,
                    user_base_url=req.base_url
                )
                conn.add(history)
                conn.commit()
                r.rpush(f"{uid}{sessionname}:usermessage", req.message)
                r.rpush(f"{uid}{sessionname}:botmessage", botmessage)
            # 发送结束标记
            yield f"data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Error in stream: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )




