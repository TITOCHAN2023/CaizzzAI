from swarm import Swarm, Agent
from openai import OpenAI

from logger import logger
from env import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL,DEEPSEEK_MODEL
client = Swarm(OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL))
 
def transfer_to_agent_b():
    return agent_b
 
 
agent_a = Agent(
    name="Agent A",
    model="deepseek-chat",
    instructions="你是一个乐于助人的智能体.",
    functions=[transfer_to_agent_b],
)
 
agent_b = Agent(
    name="Agent B",
    model="deepseek-chat",
    instructions="你是一个名字叫小b的人工智能.",
)
 

response = client.run(
    agent=agent_a,
    messages=[{"role": "user",
               "content": "我想与智能体B对话."}],
)
 

print(response.messages[-1]["content"])