import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.pydantic_v1 import BaseModel 
from .memory import  init_memory

from middleware.redis import  r



def caizzzchat(llm: ChatOpenAI, memory_key: str,uid:int,msg:str,vdbid:int | None = None) -> str:

    
    memory = init_memory(memory_key)


    prompt = ChatPromptTemplate.from_messages(
        messages=[
            MessagesPlaceholder(variable_name=memory_key),
            ("human", "{input}"),
        ],)
    
    memory_variables = memory.load_memory_variables({})
    prompt_with_memory = prompt.partial(**memory_variables)

    chain = prompt_with_memory | llm
    ai_response = ""
    for chunk in chain.stream({"input": msg}):
        content = chunk.content
        ai_response += content

    r.lpush(memory_key+":input",msg)
    r.lpush(memory_key+":output",ai_response)

    return ai_response
    