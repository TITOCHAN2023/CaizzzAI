import os

allowed_extensions = [".txt", ".pdf", ".docx", ".xlsx",".htm","html"]
public_vdb_list=["SZTU公共知识库"]


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



OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_LLM_MODEL = os.environ.get("OPENAI_LLM_MODEL")
OPENAI_EMBEDDING_MODEL = os.environ.get("OPENAI_EMBEDDING_MODEL","text-embedding-3-small")

DEBUG_MODE= os.environ.get("DEBUG_MODE", "False").lower() == "true"

API_HOST = os.environ.get("API_HOST","localhost")
API_PORT = int(os.environ.get("API_PORT", "8000"))



REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")



JWT_TOKEN_SECRET = os.environ.get("JWT_TOKEN_SECRET")
JWT_TOKEN_EXPIRE_TIME = eval(os.environ.get("JWT_TOKEN_EXPIRE_TIME", "3600 * 24 * 30"))
JWT_TOKEN_ALGORITHM = os.environ.get("JWT_TOKEN_ALGORITHM", "HS256")
API_KEY_EXPIRE_TIME = eval(os.environ.get("API_KEY_EXPIRE_TIME", "3600 * 24 * 30"))

