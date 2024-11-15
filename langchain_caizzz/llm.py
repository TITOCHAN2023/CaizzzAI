import os
from typing import Dict
from langchain_openai.chat_models import ChatOpenAI
from logger import logger


def init_llm(llm_name: str, base_url: str, api_key: str, temperature:str,**kwargs) -> ChatOpenAI:
    """Init LLM."""

    kwargs.update({"verbose": True, "streaming": True})

    llm= ChatOpenAI(
        model=llm_name,
        openai_api_base=base_url,
        openai_api_key=api_key,
        temperature=temperature,
        **kwargs,
    )
    
    logger.debug(f"Init LLM: {llm.model_name}")
    return llm


def ping_llm(llm: ChatOpenAI) -> bool:
    # test the connection to the LLM
    try :
        llm_response = llm.invoke("ping! rely with 'pong'")
        logger.debug(f"LLM response: {llm_response}")
    except Exception as e:
        logger.error(f"LLM ping failed: {e}")
        return False
    logger.debug("LLM ping successful")
    return True