from typing import List, Literal

from pydantic import BaseModel

class CreateSessionRequest(BaseModel):
    sessionname: str
    

class ResetUserRequest(BaseModel):
    originUsername: str
    username: str
    originPassword:str = None
    password: str
    avatar: str = None
    otp: str = None


class RegisterRequest(BaseModel):
    otp: str
    username: str
    password: str
    avatar: str = None


class WXRegisterRequest(BaseModel):
    access_token: str
    signature: str
    openid: str
    sig_method: str
    
class LoginRequest(BaseModel):
    username: str
    password: str


class EmbeddingRequest(BaseModel):
    embedding_model: str = "text-embedding-3-small"
    base_url: str
    api_key: str


class ChatRequest(BaseModel):
    llm_model: str ="gpt-4o-mini"
    temperature: float = 0.5
    api_key: str
    base_url: str
    message: str
    vdb_name: str | None = None

class TTSRequest(BaseModel):
    voicename: str
    content: str
    tts_class: str = "F5-TTS"
