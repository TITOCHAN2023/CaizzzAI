import datetime
import os
import requests
from typing import Tuple

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from middleware.mysql.models.audio_position import audioPositionSchema
from middleware.mysql.models.users import UserSchema
from middleware.mysql import session

from env import TTS_URL, SERVER_URL
from langchain_caizzz.tts import tts
from ...model.request import TTSRequest
from ...model.response import StandardResponse
from ...auth.jwt import jwt_auth
from middleware.redis import r
from logger import logger

audio_router = APIRouter(prefix="/audio", tags=["audio"])


@audio_router.post("", response_model=StandardResponse, dependencies=[Depends(jwt_auth)])
async def generate_audio(req:TTSRequest, info: Tuple[int, int] = Depends(jwt_auth)) -> StandardResponse:
    uid,_= info
    if req.content == "":
        logger.error("text is empty")
        raise HTTPException(status_code=400, detail="text is empty")
    
    
    
    if r.hexists(name=f"audio_{uid}",key=req.voicename+req.content):
        tts_url = r.hget(name=f"audio_{uid}",key=req.voicename+req.content)
        return StandardResponse(
            code=0,
            status="success",
            message="audio",
            data={"audio_url": tts_url},
        )
    with session() as conn:
        audio_position = conn.query(audioPositionSchema.audio_position).filter(audioPositionSchema.uid == uid,audioPositionSchema.audio_content==req.voicename+req.content).first()
        if audio_position:
            return StandardResponse(
                code=0,
                status="success",
                message="audio",
                data={"audio_url": audio_position},
            )
        
    tts_class = req.tts_class.upper()
    try:
        tts_url =tts(
                            uid=uid, 
                            content=req.content, 
                            voicename=req.voicename, 
                            tts_class=tts_class
                            )
        tts_url = f"{SERVER_URL }/v1/audio/audio/{uid}/"+tts_url
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    r.hset(name=f"audio_{uid}",key=req.voicename+req.content,value=tts_url)
    with session() as conn:
        new_audio_position = audioPositionSchema(
            audio_content=req.voicename+req.content,
            audio_position=tts_url,
            uid=uid
        )
        conn.add(new_audio_position)
        conn.commit()

    return StandardResponse(
        code=0,
        status="success",
        message="audio",
        data={"audio_url": tts_url},
    )


@audio_router.get("/audio/{uid}/{name}", response_class=FileResponse)
async def get_audio(uid:str,name: str) -> FileResponse:
    filename = f"audio_output/{uid}/{name}"
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"return audio {name} to {uid} . location :{filename}")

    if not os.path.exists(filename):
        logger.error(f"audio {filename} not found")
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(filename)

# @audio_router.get("/audio/{name}", response_class=FileResponse)
# async def get_audio( name: str) -> FileResponse:
#     uid=1
#     filename = f"audio_output/{uid}/{name}"
#     logger.info(f"Current working directory: {os.getcwd()}")
#     logger.info(f"return audio {name} to {uid} . location :{filename}")

#     if not os.path.exists(filename):
#         logger.error(f"audio {filename} not found")
#         raise HTTPException(status_code=404, detail="Audio file not found")

#     return FileResponse(filename)

