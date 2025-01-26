
# CaizzzAI (Developing)

CaizzzAI is an AI project utilizing Langchain, OpenAI, and FAISS to deliver high-touch services with AI-Chat and RAG, based on FAISS.

![CaizzzAI](static/img/image.png)

## Environment Setup

To set up the conda environment, run the following commands:

```bash
conda create -n caizzzai python=3.11
conda activate caizzzai
pip install -r requirement.txt
```

Alternatively, you can set up the environment using other methods, but ensure the Python version is 3.11.

## Creating .env File

Create a `.env` file with the following content:

```plaintext
# Server class
SERVER = 0 # 0: CPU, 1: GPU (better performance)

# TTS (create TTS server see here https://github.com/TITOCHAN2023/F5-TTS)
TTS_URL="xxxxx"

# API
API_HOST = "localhost"
API_PORT = "8000"
JWT_TOKEN_SECRET = "xxx"

# LLM
LLM_NAME = "llm"
OUTPUT_PARSER_NAME = "output_parser"
RETRIEVER_NAME = "retriever"
DOCUMENT_STUFFER_NAME = "document_stuffer"

# Log root path
INFO_LOG = "zzzzz-api-info.log"
ERROR_LOG = "zzzzz-api-error.log"
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | <cyan>[{function}]</cyan>: <level>{message}</level>"
FAISS_INDEX_PATH = "vdb_path"
UPLOAD_FOLDER = "upload_files"
UPLOAD_FILES_MAX_SIZE = "10 * 1024 * 1024"

# MySQL
MYSQL_HOST = "xxx"
MYSQL_USER = "xxx"
MYSQL_PASSWORD = "xxx"
MYSQL_DATABASE = "CaizzzRAG"
MYSQL_PORT = 3306

# OpenAI
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

# Redis
DEBUG_MODE = True
REDIS_HOST = "xxx"
REDIS_PORT = 6379
REDIS_PASSWORD = "xxx"
```

## Starting the Application

To start the application, use the following commands:

```bash
uvicorn main:app --reload --env-file .env 
streamlit run Caizzz_app.py --server.enableCORS false --server.port 8502 --server.enableXsrfProtection false --server.baseUrlPath "gpt"
```

## Additional Integrations

- **Podcastfy**: Added to the project (thanks to podcastfy.ai)
- **TTS**: Added to the project (thanks to F5-TTS, GPT-SoVITS)
- **Whisper**: To build your STT server (CUDA), use the following Docker command:

```bash
docker run --gpus=all --publish 8xxx:8000 --volume ~/.cache/huggingface:/root/.cache/huggingface --detach fedirz/faster-whisper-server:latest-cuda
```

## Project Structure

```plaintext
CaizzzAI/
├── env.py
├── loadDocuments.py
├── LICENSE
├── log/
│   ├── zzzzz-api-error.log
│   ├── zzzzz-api-info.log
├── logger/
│   └── logger.py
├── routes/
│   ├── router/
│   │   ├── v1/
│   │   │   ├── audio.py
│   │   │   ├── podcastfy.py
│   │   │   └── vdb.py
├── static/
│   └── img/
│       └── image.png
├── main.py
├── Caizzz_app.py
├── README.md
└── requirement.txt
```

## API Endpoints

### User

- **POST /root/register**: Register a new user.
- **POST /root/login**: Login a user.
- **POST /root/reset_user**: Reset user information (requires authorization).

### Audio

- **GET /audio/{uid}/{name}**: Retrieve audio file by user ID and file name.

### Podcastfy

- **POST /{sessionname}/upload**: Upload a podcast file.
- **GET /sessionlist**: Get the list of podcast sessions.
- **GET /{sessionname}**: Get the history of a podcast session.
- **POST /v1/session**: Create a new podcast session (requires authorization).
- **DELETE /v1/session/{sessionname}/delete**: Delete a podcast session (requires authorization).
- **GET /v1/session/{sessionname}**: Get the history of a podcast session (requires authorization).
- **POST /v1/session/{sessionname}/chat**: Post a user message to a session (requires authorization).

### Vector Database (VDB)

- **POST /{vdbname}/uploadfile**: Upload a file to the vector database (requires authorization).
- **GET /getvdblist**: Get the list of vector databases (requires authorization).
- **POST /v1/vdb**: Create a new vector database (requires authorization).
- **POST /v1/vdb/{vdbname}/uploadfile**: Upload a file to the vector database (requires authorization).

