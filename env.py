import os

SUPPORT_URL_TYPE= os.environ.get("SUPPORT_URL_TYPE", "text,html,markdown").split(",")
SUPPORT_UPLOAD_FILE= os.environ.get("SUPPORT_UPLOAD_FILE", "True").lower() == "true"
TMP_ROOT= os.environ.get("TMP_ROOT", "/tmp")

LLM_NAME = os.environ.get("LLM_NAME")

LOGGER_LEVEL = os.environ.get("LOGGER_LEVEL", "INFO")
LOGGER_ROOT = os.environ.get("LOGGER_ROOT", "./log")
ERROR_LOG  = os.environ.get("ERROR_LOG")
LOG_FORMAT = os.environ.get("LOG_FORMAT")
INFO_LOG = os.environ.get("INFO_LOG")
LOG_ROOT= os.environ.get("LOGGER_ROOT", "./log")

NEO4J_HOST = os.environ.get("NEO4J_HOST")
NEO4J_PORT = int(os.environ.get("NEO4J_PORT", "7687"))
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")

DOCUMENT_STUFFER__NAME= os.environ.get("DOCUMENT_STUFFER__NAME")
OUTPUT_PARSER_NAME= os.environ.get("OUTPUT_PARSER_NAME")

MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")
MYSQL_HOST = os.environ.get("MYSQL_HOST")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
MYSQL_USER = os.environ.get("MYSQL_USER")


OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai-proxy.org/v1")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_SYS_PROMPT = os.environ.get("OPENAI_SYS_PROMPT", "")
OPENAI_INIT_HISTORY = os.environ.get("OPENAI_INIT_HISTORY", "")

OPENAI_LLM_TYPE = os.environ.get("OPENAI_LLM_TYPE")
OPENAI_LLM_MODEL = os.environ.get("OPENAI_LLM_MODEL")
OPENAI_LLM_PATH = os.environ.get("OPENAI_LLM_PATH")
OPENAI_MAX_TOKENS = int(os.environ.get("OPENAI_MAX_TOKENS", "100"))

OPENAI_EMBEDDING_TYPE = os.environ.get("OPENAI_EMBEDDING_TYPE")
OPENAI_EMBEDDING_MODEL = os.environ.get("OPENAI_EMBEDDING_MODEL")
OPENAI_EMBEDDING_PATH = os.environ.get("OPENAI_EMBEDDING_PATH")
OPENAI_CHUNK_SIZE = int(os.environ.get("OPENAI_CHUNK_SIZE", "100"))


DEBUG_MODE= os.environ.get("DEBUG_MODE", "False").lower() == "true"

API_HOST = os.environ.get("API_HOST")
API_PORT = int(os.environ.get("API_PORT", "8000"))

OAUTH2_GITHUB_CLIENT_ID = os.environ.get("OAUTH2_GITHUB_CLIENT_ID")
OAUTH2_GITHUB_CLIENT_SECRET = os.environ.get("OAUTH2_GITHUB_CLIENT_SECRET")



REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")


JWT_TOKEN_SECRET = os.environ.get("JWT_TOKEN_SECRET")
JWT_TOKEN_EXPIRE_TIME = eval(os.environ.get("JWT_TOKEN_EXPIRE_TIME", "3600"))
JWT_TOKEN_ALGORITHM = os.environ.get("JWT_TOKEN_ALGORITHM", "HS256")

API_KEY_EXPIRE_TIME = eval(os.environ.get("API_KEY_EXPIRE_TIME", "3600 * 24 * 30"))


OAUTH2_GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
OAUTH2_GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
OAUTH2_GITHUB_USER_API = "https://api.github.com/user"

OAUTH2_GITHUB_REDIRECT_URL = f"http://{API_HOST}:{API_PORT}/v1/oauth2/github/callback"
