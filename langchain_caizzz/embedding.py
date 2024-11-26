
from langchain_openai import OpenAIEmbeddings


from uuid import uuid4
from env import OPENAI_BASE_URL,OPENAI_EMBEDDING_MODEL
from logger import logger


def init_embedding(embeddings_name: str, base_url: str, api_key: str,**kwargs) -> OpenAIEmbeddings:
    """Init EMBEDDING"""

    if base_url=="":
        base_url=OPENAI_BASE_URL
    if embeddings_name=="":
        embeddings_name=OPENAI_EMBEDDING_MODEL
    
    embeddings = OpenAIEmbeddings(
        model=embeddings_name,
        openai_api_base=base_url,
        openai_api_key=api_key,
        **kwargs
    )
    
    logger.debug(f"Init LLM: {embeddings.model}")
    return embeddings
