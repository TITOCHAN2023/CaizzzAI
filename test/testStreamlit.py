import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory

# Setting up environment variables
os.environ["MODEL"] = "gpt-4o-mini"
os.environ["API_BASE"] = "https://api.openai-proxy.org/v1"
os.environ["OPENAI_API_KEY"] = "sk-SrkteYrb62PmPt0Lo5yyGCaAVSmWlb5zzgiqJ5skf965G4Mr"

# Initialize the ChatOpenAI model
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
        ],
    )
    
    return memory, prompt

def main():
    st.title("Chatbot Interface")
    st.write("This is a simple chatbot interface using Langchain and OpenAI.")

    # Initialize chat memory and prompt
    memory, prompt = chat("history")

    # User input
    user_input = st.text_input("You: ", "")
    if user_input:
        memory_variables = memory.load_memory_variables({})
        prompt_with_memory = prompt.partial(**memory_variables)

        ai_response = ""
        with st.spinner("AI is thinking..."):
            chain = prompt_with_memory | llm
            for chunk in chain.stream({"input": user_input}):
                ai_response += chunk.content

        # Display user and AI messages in a more formatted way
        st.markdown(f"**You:** {user_input}")
        st.markdown(f"**AI:** {ai_response}")

        memory.save_context({"input": user_input}, {"output": ai_response})

    if st.button("Clear Chat"):
        memory.clear()

if __name__ == "__main__":
    main()