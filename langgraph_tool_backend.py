import sqlite3
import sys
import uuid
import requests
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchResults

# uuid_utils monkeypatching
sys.modules['uuid_utils'] = uuid
sys.modules['uuid_utils.compat'] = uuid

# 1. State Definition
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# 2. LLM Model Initialization
llm = ChatOllama(model="qwen2.5:3b")

# -------------------
# Tools

search_tool = DuckDuckGoSearchResults()

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given ticker symbol (e.g. 'AAPL', 'TSLA').
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=7JOABP9AXJ66RNXH"
    r = requests.get(url)
    return r.json()


tools = [search_tool, get_stock_price, calculator]

llm_with_tools = llm.bind_tools(tools)

# Node Function
def chat_node(state: ChatState):
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {'messages': [response]}

tool_node = ToolNode(tools)

# Checkpointer
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# Graph Construction
graph = StateGraph(ChatState)

# Nodes Add
graph.add_node('chat_node', chat_node)
graph.add_node('tools', tool_node)

# Flow Definition
graph.add_edge(START, 'chat_node')


graph.add_conditional_edges('chat_node', tools_condition)

graph.add_edge('tools', 'chat_node')

chatbot = graph.compile(checkpointer=checkpointer)


def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)