import os
from typing import Dict
from langchain_openai.chat_models import ChatOpenAI
from logger import logger
from env import OPENAI_BASE_URL,OPENAI_LLM_MODEL

def init_llm(llm_name: str, base_url: str, api_key: str, temperature: str, llm_class: str = "openai", **kwargs):
    """Init LLM."""

    kwargs.update({"verbose": True, "streaming": True})


    if llm_class == "openai":
        if base_url=="":
            base_url=OPENAI_BASE_URL
        if llm_name=="":
            llm_name=OPENAI_LLM_MODEL
        
        llm= ChatOpenAI(
            model=llm_name,
            openai_api_base=base_url,
            openai_api_key=api_key,
            temperature=temperature,
            **kwargs,
        )

        
        
    logger.debug(f"Init LLM: {llm.model_name}")
    return llm

