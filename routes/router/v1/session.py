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
from middleware.mysql.models.session import SessionSchema
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
                for hid,create_at,usermessage,botmessage,llm_model,user_api_key,user_base_url in results[::-1]
            ]
        }

        r.set(f"{uid}{sessionname}llm_model", results[0].llm_model)
        r.set(f"{uid}{sessionname}user_api_key", results[0].user_api_key)
        r.set(f"{uid}{sessionname}user_base_url", results[0].user_base_url)

        if not r.exists(f"{uid}{sessionname}:input"):
            history_input = [usermessage for _, _, usermessage, _, _, _, _ in results[0:20]]
            history_output = [botmessage for _, _, _, botmessage, _, _, _ in results[0:20]]
            #logger.info(f"history_input:{history_input},history_output:{history_output}")
            if history_input and history_output:
                for human_message, ai_response in zip(history_input, history_output):
                    r.rpush(f"{uid}{sessionname}:input", human_message)
                    r.rpush(f"{uid}{sessionname}:output", ai_response)
            


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
            conn.query(SessionSchema.sid,SessionSchema.sessionname, SessionSchema.create_at, SessionSchema.update_at)
            .filter(SessionSchema.sessionname == sessionname)
            .filter(SessionSchema.uid == uid)
            .filter(or_(SessionSchema.delete_at.is_(None), datetime.now() < SessionSchema.delete_at))
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

            input_message = f"根据以下文档回答问题：\n{context}\n\n问题：{req.message}\n回答："
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
                r.lpush(f"{uid}{sessionname}:input", req.message)
                r.lpush(f"{uid}{sessionname}:output", botmessage)
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




