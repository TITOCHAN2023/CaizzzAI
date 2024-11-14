import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.pydantic_v1 import BaseModel 

os.environ["MODEL"] = "gpt-4o-mini"
os.environ["API_BASE"] = "https://api.openai-proxy.org/v1"
os.environ["OPENAI_API_KEY"] = "sk-SrkteYrb62PmPt0Lo5yyGCaAVSmWlb5zzgiqJ5skf965G4Mr"

llm = ChatOpenAI(
    openai_api_base=os.environ["API_BASE"],
    model=os.environ["MODEL"],
    openai_api_key=os.environ["OPENAI_API_KEY"],
)

def chat(memory_key):
    memory = ConversationBufferWindowMemory(memory_key=memory_key, return_messages=True, k=10)
    prompt = ChatPromptTemplate.from_messages(
        messages=[
            MessagesPlaceholder(variable_name=memory_key),
            ("human", "{input}"),
        ],)
    
    while True:
        memory_variables = memory.load_memory_variables({})
        prompt_with_memory = prompt.partial(**memory_variables)
        human_message = input("user: ")
        if human_message == "exit":break
        print("AI:", end="", flush=True)
        chain = prompt_with_memory | llm
        ai_response = ""
        for chunk in chain.stream({"input": human_message}):
            content = chunk.content
            print(content, end="", flush=True)
            ai_response += content
        print()
        memory.save_context({"input": human_message}, {"output": ai_response})
    memory.clear()

chat("history")