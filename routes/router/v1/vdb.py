from datetime import datetime
from typing import Any, AsyncGenerator, Callable, Dict, Tuple
from logger import logger
import json
import os


from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form

from sqlalchemy import or_

from middleware.mysql.models.VectorDB import VectorDBSchema
from middleware.mysql.models.users import UserSchema
from middleware.mysql import session
from routes.model.request import EmbeddingRequest
from routes.model.response import StandardResponse
from ...auth.jwt import jwt_auth
from middleware.redis import r
from middleware.hash.hash import hash_string
from env import UPLOAD_FILES_MAX_SIZE,UPLOAD_FOLDER,FAISS_INDEX_PATH

from langchain_caizzz.llm import init_llm
from langchain_caizzz.embedding import init_embedding
from langchain_caizzz.faiss import update_vdb

vdb_router = APIRouter(prefix="/vdb", tags=["vdb"])


from env import allowed_extensions,public_vdb_list


'''upload file to vdb'''
@vdb_router.post("/{vdbname}/uploadfile", response_model=StandardResponse, dependencies=[Depends(jwt_auth)])
async def upload_file(vdbname: str,
    embedding_model: str = Form(...),
    base_url: str = Form(...),
    api_key: str = Form(...),file: UploadFile = File(...), info: Tuple[int, int] = Depends(jwt_auth)) -> StandardResponse:

    uid, _ = info

    _, ext = os.path.splitext(file.filename)
    ext = ext.lower()
    content = await file.read()

    is_admin = False
    with session() as conn:
        user = conn.query(UserSchema).filter(UserSchema.uid == uid).first()
        is_admin = user.is_admin

        if not conn.is_active:
            conn.rollback()
            conn.close()
        else:
            conn.commit()

        vdb = conn.query(VectorDBSchema).filter(VectorDBSchema.name == vdbname).first()
        if not vdb:
            raise HTTPException(status_code=404, detail="VectorDB not found")

        if not conn.is_active:
            conn.rollback()
            conn.close()
        else:
            conn.commit()

    if vdbname in public_vdb_list and not is_admin:
        raise HTTPException(status_code=400, detail="公共知识库不支持非管理员上传文件")

    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="不支持的文件类型")

    if len(content) > UPLOAD_FILES_MAX_SIZE:
        raise HTTPException(status_code=413, detail="文件太大")

    filename = hash_string(file.filename)
    hash_vdbname = hash_string(vdbname)
    os.makedirs(f"{FAISS_INDEX_PATH}/{UPLOAD_FOLDER}/{str(uid)}/{hash_vdbname}", exist_ok=True)
    folder_path = f"{FAISS_INDEX_PATH}/{UPLOAD_FOLDER}/{str(uid)}/{hash_vdbname}"
    file_location = f"{FAISS_INDEX_PATH}/{UPLOAD_FOLDER}/{str(uid)}/{hash_vdbname}/{filename}{ext}"

    with open(file_location, "wb") as f:
        f.write(content)


    os.makedirs(f"{FAISS_INDEX_PATH}/index/{str(uid)}", exist_ok=True)
    index_file_path = f"{FAISS_INDEX_PATH}/index/{str(uid)}/{hash_vdbname}.index"
    mapping_file_path = f"{FAISS_INDEX_PATH}/index/{str(uid)}/{hash_vdbname}_mapping.pkl"

    # logger.info(f"uid:{uid},vdbname:{vdbname},filename:{filename},ext:{ext},file_location:{file_location},index_file_path:{index_file_path},mapping_file_path:{mapping_file_path}")
    # logger.info(f"embeddings_name:{embedding_model},api_key:{api_key},base_url:{base_url}")

    embeddings = init_embedding(embeddings_name=embedding_model, api_key=api_key, base_url=base_url)
    update_vdb(index_file_path, mapping_file_path, directory_path=folder_path, embeddings=embeddings)

    return StandardResponse(code=0, status="success", data={"info": f"文件'{file.filename}'成功存入'{vdbname}'知识库中"})




'''get vdb list'''
@vdb_router.get("/getvdblist", response_model=StandardResponse, dependencies=[Depends(jwt_auth)])
async def get_vdb_list(info: Tuple[int, int] = Depends(jwt_auth)) -> StandardResponse:
    uid,_=info

    if r.exists(f"vdb_list:{uid}"):
        vdb_list=[json.loads(vdb) for vdb in r.lrange(f"vdb_list:{uid}",0,-1)]
        data={"vdb_list":vdb_list}
        return StandardResponse(code=0, status="success",data=data)

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
            conn.query(VectorDBSchema.vdbid,VectorDBSchema.name,VectorDBSchema.create_at,VectorDBSchema.update_at)
            .filter(or_(VectorDBSchema.uid == uid, VectorDBSchema.uid == 0))  #uid=0表示公共知识库
            .order_by(VectorDBSchema.update_at.desc())
        )
        res=query.all()

    vdb_list=[{
            "vdbid":vdbid,
            "name":str(name),
            "create_at":str(create_at),
            "update_at":str(update_at),
        }for vdbid,name,create_at,update_at in res]

    data={"vdb_list":vdb_list}

    for vdb in vdb_list:
        r.rpush(f"vdb_list:{uid}", json.dumps(vdb))

    return StandardResponse(code=0, status="success", data=data)




'''create vdb'''
@vdb_router.post("", response_model=StandardResponse, dependencies=[Depends(jwt_auth)])
async def create_vdb(request: Dict[str, Any],info: Tuple[int, int] = Depends(jwt_auth)) -> StandardResponse:
    uid,_=info
    name=request.get("name")
    logger.info(f"uid:{uid},name:{name}")

    with session() as conn:
        user = conn.query(UserSchema).filter(UserSchema.uid == uid).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not conn.is_active:
            conn.rollback()
            conn.close()
        else:
            conn.commit()


        vdb = conn.query(VectorDBSchema).filter(VectorDBSchema.name == name).first()
        if vdb:
            raise HTTPException(status_code=400, detail="此名字已经存在")
        
        if name in public_vdb_list:
            if not user.is_admin:
                raise HTTPException(status_code=400,detail="公共知识库名字不支持创建,请更换名字")

        _vdb = VectorDBSchema(uid=uid, name=name,index="faiss")
        conn.add(_vdb)
        conn.commit()

        data = {"name": _vdb.name, "create_at": _vdb.create_at}

        r.rpush(f"vdb_list:{uid}", json.dumps({
            "vdbid":_vdb.vdbid,
            "name":_vdb.name,
            "create_at":str(_vdb.create_at),
            "update_at":str(_vdb.update_at)
        }))
        
    return StandardResponse(code=0, status="success", data=data)
