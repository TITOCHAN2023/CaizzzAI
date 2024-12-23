import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.pydantic_v1 import BaseModel 

from logger import logger
from middleware.redis import  r

def init_memory(memory_key: str) -> ConversationBufferWindowMemory:
    memory = ConversationBufferWindowMemory(memory_key=memory_key, return_messages=True, k=20)
    
    # 从 Redis 列表加载历史记录
    input_messages = r.lrange(f"{memory_key}:usermessage",0,-1)
    output_messages = r.lrange(f"{memory_key}:botmessage",0,-1)
    #logger.info(input_message)
    if input_messages and output_messages:
        for input_message, output_message in zip(input_messages, output_messages):
            memory.save_context({"input": input_message}, {"output": output_message})

    return memory