import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.pydantic_v1 import BaseModel 
from .memory import  init_memory

from middleware.redis import  r



def caizzzchain(llm: ChatOpenAI, memory_key: str) :



    memory = init_memory(memory_key)
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name=memory_key),
            ("human", "{input}"),
        ])
        
    memory_variables = memory.load_memory_variables({})
    prompt_with_memory = prompt.partial(**memory_variables)
    chain = prompt_with_memory | llm

    return chain
    