import os
from typing import Dict
from langchain_ollama  import ChatOllama
from langchain_openai.chat_models import ChatOpenAI
from logger import logger
from env import OPENAI_BASE_URL,OPENAI_LLM_MODEL,DEEPSEEK_BASE_URL,DEEPSEEK_API_KEY,DEEPSEEK_MODEL,API_KEY_HOST

def init_llm(llm_name: str, base_url: str, api_key: str, temperature: str, **kwargs):
    """Init LLM."""
    if llm_name == "":
        llm_name = DEEPSEEK_MODEL
    if "https://api.titochan.top" in base_url:
        base_url.replace("https://api.titochan.top", API_KEY_HOST)
    '''openai'''
    if llm_name.startswith("gpt"):

        kwargs.update({"verbose": True, "streaming": True})
        if llm_name=="":
            llm_name=OPENAI_LLM_MODEL
        
        logger.info(f"Init OpenAI LLM: {llm_name},base_url:{base_url},api_key:{api_key},temperature:{temperature}")

        llm= ChatOpenAI(
            model=llm_name,
            openai_api_base=base_url,
            openai_api_key=api_key,
            temperature=temperature,
            **kwargs,
        )

    '''deepseek'''
    if llm_name.startswith("deepseek"):

        kwargs.update({"verbose": True, "streaming": True})
        base_url=DEEPSEEK_BASE_URL
        llm_name=DEEPSEEK_MODEL
        api_key=DEEPSEEK_API_KEY
        
        logger.info(f"Init deepseek LLM: {llm_name},base_url:{base_url},api_key:{api_key},temperature:{temperature}")

        llm= ChatOpenAI(
            model=llm_name,
            openai_api_base=base_url,
            openai_api_key=api_key,
            temperature=temperature,
            **kwargs,
        )

    '''ollama'''
    if llm_name.startswith("ollama"):

        if base_url=="":
            base_url="127.0.0.1:11434"
        if llm_name=="":
            llm_name="c14q4"
            
        llm = ChatOllama(
            model=llm_name,
            base_url=base_url,
            temperature=temperature,
            stream=True,
            **kwargs,
        )

        
    return llm

