import os
# pyrefly: ignore [missing-import]
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from tools.analyzer import analyzer_tool

# Initialize the Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

# Bind our tools to the LLM
tools = [analyzer_tool]
llm_with_tools = llm.bind_tools(tools)

def call_model(state):
    """
    Calls the LLM. It looks at the messages and decides whether
    to reply directly or use a tool.
    """
    messages = state["messages"]
    csv_path = state.get("csv_file_path", "No file uploaded")
    
    # Give the agent some context
    system_prompt = SystemMessage(
        content=f"You are an AI CSV Analyst. You help users analyze their data.\n"
                f"The current dataset is located at: {csv_path}\n"
                f"If the user asks a question about the data, use the analyzer_tool to read it."
    )
    
    response = llm_with_tools.invoke([system_prompt] + messages)
    
    return {"messages": [response]}
