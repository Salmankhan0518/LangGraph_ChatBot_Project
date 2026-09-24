import sys
import uuid

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
import sqlite3


# uuid_utils monkeypatching
sys.modules['uuid_utils'] = uuid
sys.modules['uuid_utils.compat'] = uuid

# 1. State Definition
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# 2. LLM Model Initialization
# (Model name specific rakhein jaise 'qwen2.5:3b' ya 'llama3.2')
llm = ChatOllama(model="qwen2.5:3b")

# 3. Node Function Fix
def chat_node(state: ChatState):
    messages = state['messages']
    # FIX: Class ki bajaye 'llm' instance ko invoke karein
    response = llm.invoke(messages)
    return {'messages': [response]}

conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
# Checkpointer
checkpointer = SqliteSaver(conn=conn)

# 4. Graph Construction
graph = StateGraph(ChatState)

graph.add_node('chat_node', chat_node)
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)

# test
CONFIG = {"configurable": {"thread_id": 'thread-1'}}

response = chatbot.invoke(
                {"messages": [HumanMessage(content='what is my name')]},
                  config=CONFIG,
            )


print(response)