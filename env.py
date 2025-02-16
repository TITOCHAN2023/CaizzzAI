import os

allowed_extensions = [".txt", ".pdf", ".docx", ".xlsx",".htm","html"]
public_vdb_list=["SZTU公共知识库"]
TTS_URL=str(os.environ.get("TTS_URLS")).split(',')
PODCASTPOSITION=os.environ.get("PODCASTPOSITION")
TEXT_SPLITER_WAY=os.environ.get('TEXT_SPLITER_WAY')

SERVER=eval(os.environ.get("SERVER","0"))
SERVER_URL=os.environ.get("SERVER_URL")
API_HOST = os.environ.get("API_HOST","localhost")
API_PORT = int(os.environ.get("API_PORT", "8000"))
DEBUG_MODE= os.environ.get("DEBUG_MODE", "False").lower() == "true"
API_KEY_HOST = os.environ.get("API_KEY_HOST")
API_KEY_ROOT_AUTH=os.environ.get("API_KEY_ROOT_AUTH")
FREE_USAGE=os.environ.get("FREE_USAGE")
OTP_SECRET_2=os.environ.get("OTP_SECRET_2")
WX_APPID=os.environ.get("WX_APPID")
WX_APPSECRET=os.environ.get("WX_APPSECRET")

LOGGER_LEVEL = os.environ.get("LOGGER_LEVEL", "INFO")
LOGGER_ROOT = os.environ.get("LOGGER_ROOT", "./log")
ERROR_LOG  = os.environ.get("ERROR_LOG")
LOG_FORMAT = os.environ.get("LOG_FORMAT")
INFO_LOG = os.environ.get("INFO_LOG")
LOG_ROOT= os.environ.get("LOGGER_ROOT", "./log")
FAISS_INDEX_PATH= os.environ.get("FAISS_INDEX_PATH","vdb_path")
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "upload_files")
UPLOAD_FILES_MAX_SIZE = eval(os.environ.get("UPLOAD_FILES_MAX_SIZE", "10 * 1024 * 1024"))




MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")
MYSQL_HOST = os.environ.get("MYSQL_HOST")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
MYSQL_USER = os.environ.get("MYSQL_USER")



DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL")


OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_LLM_MODEL = os.environ.get("OPENAI_LLM_MODEL")
OPENAI_EMBEDDING_MODEL = os.environ.get("OPENAI_EMBEDDING_MODEL","text-embedding-3-small")





REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
REDIS_FLUSH=os.environ.get("REDIS_FLUSH",None)

OTP_SECRET = os.environ.get("OTP_SECRET")
JWT_TOKEN_SECRET = os.environ.get("JWT_TOKEN_SECRET")
JWT_TOKEN_EXPIRE_TIME = eval(os.environ.get("JWT_TOKEN_EXPIRE_TIME", "3600 * 24 * 30"))
JWT_TOKEN_ALGORITHM = os.environ.get("JWT_TOKEN_ALGORITHM", "HS256")
API_KEY_EXPIRE_TIME = eval(os.environ.get("API_KEY_EXPIRE_TIME", "3600 * 24 * 30"))

