from datetime import datetime
from typing import Any, AsyncGenerator, Callable, Dict, Tuple
from logger import logger
import json
import os


from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form

from sqlalchemy import or_

from middleware.mysql.models.users import UserSchema
from middleware.mysql.models.podcastfy_session import PodcastfySessionSchema
from middleware.mysql.models.podcastfy_conversation import PodcastfyConversationSchema
from middleware.mysql import session
from middleware.redis import r

from routes.model.response import StandardResponse
from ...auth.jwt import jwt_auth
from middleware.redis import r
from middleware.hash.hash import hash_string

import requests
from typing import List

from env import UPLOAD_FILES_MAX_SIZE,PODCASTPOSITION,TTS_URL,allowed_extensions

podcast_router = APIRouter(prefix="/podcast", tags=["podcast"])


tts_url=TTS_URL
position=PODCASTPOSITION


async def upload_files(files: List[UploadFile], sessionname: str,uid:int) :

    urls=[]

    for file in files:
        _, ext = os.path.splitext(file.filename)
        ext = ext.lower()
        content = await file.read()

        if ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.filename}:{ext}")

        if len(content) > UPLOAD_FILES_MAX_SIZE:
            raise HTTPException(status_code=413, detail=f"文件太大: {file.filename}")

        os.makedirs(f"{position}/{uid}/{sessionname}/", exist_ok=True)
        file_location = f"{position}/{uid}/{sessionname}/{file.filename}"

        urls.append(file_location)

        with open(file_location, "wb") as f:
            f.write(content)


    from middleware.podcastfy.client import generate_podcast
    from env import OPENAI_API_KEY,OPENAI_BASE_URL
    api_key=OPENAI_API_KEY
    base_url=OPENAI_BASE_URL


    transcript_file = generate_podcast(
        urls=urls,
        tts_model="edge",
        llm_model_name="gpt-4o-mini",
        api_key_label=api_key,
        base_url=base_url,
        transcript_only=True,
        longform=False
        )
    
    logger.info(f"Generated transcript file path: {transcript_file}")
    
    try:
        with open(transcript_file, "r") as f:
            transcript = f.read()
    except Exception as e:
        logger.error(f"Error reading transcript file: {str(e)}")
        raise HTTPException(status_code=400, detail="Error reading transcript file")
    
    

    return transcript


async def divide(transcript:str):
    import re

    person1_lines = []
    person2_lines = []

    matches = re.findall(r'<(Person1|Person2)>(.*?)</\1>', transcript, re.DOTALL)

    for match in matches:
        if match[0] == "Person1":
            person1_lines.append(match[1].strip())
        elif match[0] == "Person2":
            person2_lines.append(match[1].strip())

    return person1_lines,person2_lines
    


@podcast_router.post("/{sessionname}/upload", response_model=StandardResponse, dependencies=[Depends(jwt_auth)])
async def upload_file_podcast(
    sessionname:str,
    file: UploadFile = File(...),info: Tuple[int, int] = Depends(jwt_auth)):


    uid, _ = info
    

    try:
        with session() as conn:
            
            sessionname = sessionname+file.filename


            ses = conn.query(PodcastfySessionSchema)\
            .filter(PodcastfySessionSchema.sessionname == sessionname)\
            .filter(PodcastfySessionSchema.uid== uid)\
            .first()

            if ses:
                logger.error(f"Session already exists: {sessionname}")
                import random
                random_number = str(random.random())
                sessionname = sessionname + random_number

            ses = PodcastfySessionSchema(
                uid=uid,
                sessionname=sessionname,
                create_at=datetime.now()
            )

            conn.add(ses)
            conn.commit()
            sid = ses.sid
            logger.info(f"Session created with ID: {sid}")

    except Exception as e:

        logger.error(f"Error creating session: {str(e)}")

    try:
        transcript =await upload_files([file], sessionname, uid)
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=400, detail="Error uploading file")

    logger.info(f"transcript: {transcript}")

    person1_lines,person2_lines=await divide(transcript)

    with session() as conn:
        for content_1,content_2 in zip(person1_lines,person2_lines):
            conversation = PodcastfyConversationSchema(
                sid=sid,
                content_1=content_1,
                content_2=content_2,
                create_at=datetime.now()
            )
            conn.add(conversation)
            conn.commit()

    data={
        "history":[
            {
                "content_1":content_1,
                "content_2":content_2,
            }
            for content_1,content_2 in zip(person1_lines,person2_lines)
        ]
    }

    r.rpush(f"{uid}_session_list_podcast", sessionname)
    r.set(f"{uid}{sessionname}:podcast_message", json.dumps(data))
    return StandardResponse(code=0, status="success", data=data)
    



'''get podcast session list'''
@podcast_router.get("/sessionlist", response_model=StandardResponse, dependencies=[Depends(jwt_auth)])
async def get_session(page_id:int,page_size:int,info: Tuple[int, int] = Depends(jwt_auth)) -> StandardResponse:
    uid,_=info
    logger.info(f"uid:{uid},page_id:{page_id},page_size:{page_size}")

    if r.exists(f"{uid}_session_list_podcast"):
        session_list = r.lrange(f"{uid}_session_list_podcast", page_id*page_size, (page_id+1)*page_size-1)
        data = {
            "session_list": [
                {
                    "sid": i,
                    "sessionname": session_name,
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
            conn.query(PodcastfySessionSchema.sid,PodcastfySessionSchema.sessionname)
            .filter(PodcastfySessionSchema.uid==uid)
            .order_by(PodcastfySessionSchema.sid.desc())
            .offset(page_id*page_size)
        )
        res=query.limit(page_size).all()

    session_list=[{
            "sid":sid,
            "sessionname":str(sessionname),
        }for sid,sessionname in res]

    data={"session_list":session_list}

    for session_ in session_list:
        r.rpush(f"{uid}_session_list_podcast", session_["sessionname"])

    return StandardResponse(code=0, status="success", data=data)
        




'''get podcast session history'''
@podcast_router.get("/{sessionname}", response_model=StandardResponse, dependencies=[Depends(jwt_auth)])
async def get_session(sessionname: str, info: Tuple[int, int] = Depends(jwt_auth)):
    uid, _ = info

    if r.exists(f"{uid}{sessionname}:podcast_message"):
        data = json.loads(r.get(f"{uid}{sessionname}:podcast_message"))
        return StandardResponse(code=0, status="success", data=data)

    with session() as conn:
        if not conn.is_active:
            conn.rollback()
            conn.close()
        else:
            conn.commit()

        query = (
            conn.query(PodcastfySessionSchema.sid,PodcastfySessionSchema.sessionname, PodcastfySessionSchema.create_at)
            .filter(PodcastfySessionSchema.sessionname == sessionname)
            .filter(PodcastfySessionSchema.uid == uid)
        )
        result = query.first()

        if not result:
            return StandardResponse(code=404, status="error", data={"history": []})
        
        session_id = result.sid


        query = (
            conn.query(PodcastfyConversationSchema.cid,PodcastfyConversationSchema.create_at,PodcastfyConversationSchema.content_1, PodcastfyConversationSchema.content_2)
                .filter(PodcastfyConversationSchema.sid == session_id)
                .order_by(PodcastfyConversationSchema.create_at.asc())
                )
        
        results = query.all()
        if not results:
            data={"history":[]}
        else:
            data = {
                "history": [
                    {
                        "cid": cid,
                        "create_at": str(create_at),
                        "content_1": content_1,
                        "content_2": content_2,
                    }
                    for cid, create_at, content_1, content_2 in results
                ]
            }

        r.set(f"{uid}{sessionname}:podcast_message", json.dumps(data))


    return StandardResponse(code=0, status="success", data=data)