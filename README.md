

# CaizzzAI (developing)

An AI project with Langchain,Openai,and FAISS,

delivers the high-touch service with AI-Chat and RAG,

based on FAISS,

named by Isshiki Iroha's Chinese name--"Caiyu" .



<img src="static/img/image.png" alt="image" style="width:40%;" />

conda environment config：

```conda create -n caizzzai python=3.11```

```conda activate caizzzai```

```pip install -r requirement.txt```

Or other way to build up th environment,

the Python version must be 3.11.

docker coming soon.

create .env:

With following the env.py, fill ".env" like:

```


# API
API_HOST = "localhost"
API_PORT = "8000"
JWT_TOKEN_SECRET = "xxx"

# llm
LLM_NAME = "llm"
OUTPUT_PARSER_NAME = "output_parser"
RETRIEVER_NAME = "retriever"
DOCUMENT_STUFFER__NAME = "document_stuffer"

# log root path
INFO_LOG = "zzzzz-api-info.log"
ERROR_LOG = "zzzzz-api-error.log"
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | <cyan>[{function}]</cyan>: <level>{message}</level>"
FAISS_INDEX_PATH = "vdb_path"
UPLOAD_FOLDER = "upload_files"
UPLOAD_FILES_MAX_SIZE = "10 * 1024 * 1024"

# mysql
MYSQL_HOST = "xxx"
MYSQL_USER = "xxx"
MYSQL_PASSWORD = "xxx"
MYSQL_DATABASE = "CaizzzRAG"
MYSQL_PORT = 3306

# openai
OPENAI_BASE_URL = "xxxx"
OPENAI_API_KEY = "xxx"

OPENAI_LLM_TYPE = "openai"
OPENAI_LLM_MODEL = "gpt-4o-mini"
OPENAI_LLM_PATH = "openaillm"
OPENAI_MAX_TOKENS = 100

OPENAI_EMBEDDING_TYPE = "openai"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
OPENAI_EMBEDDING_PATH = "openaiembedding"
OPENAI_CHUNK_SIZE = 100

# redis
DEBUG_MODE = True
REDIS_HOST = "xxx"
REDIS_PORT = 6379
REDIS_PASSWORD = "xxx"

```

then, u could start with this code

```

nohup uvicorn main:app --reload --env-file .env > uvicorn.log 2>&1 &

nohup streamlit run streamlit_app.py --server.enableCORS false --server.port 8502 --server.enableXsrfProtection false --server.baseUrlPath "gpt" > streamlit.log 2>&1 &

```

