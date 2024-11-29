

# CaizzzAI (developing)


conda environment config：

```conda env create -f rag.yaml```

create .env:

With following the env.py, fill ".env" like:

```
# openai
OPENAI_BASE_URL="xxxx"
OPENAI_API_KEY="xxxx"

OPENAI_LLM_TYPE="openai"
OPENAI_LLM_MODEL="xxx"
OPENAI_LLM_PATH="openaillm"
OPENAI_MAX_TOKENS=100

OPENAI_EMBEDDING_TYPE="openai"
OPENAI_EMBEDDING_MODEL="xxx"
OPENAI_EMBEDDING_PATH="openaiembedding"
OPENAI_CHUNK_SIZE=100


DEBUG_MODE=True
REDIS_HOST = "xxx"
REDIS_PORT = 6379
REDIS_PASSWORD = "xxx"
```



