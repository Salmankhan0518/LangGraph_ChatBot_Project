import sqlite3
import sys
import uuid
import os
import tempfile
import requests
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

# uuid_utils monkeypatching
sys.modules['uuid_utils'] = uuid
sys.modules['uuid_utils.compat'] = uuid

# DB path for FAISS
DB_PATH = "faiss_index_app"

# 1. State Definition
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# 2. LLM Model & Embeddings Initialization
llm = ChatOllama(model="qwen2.5:3b")
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Initialize / Load FAISS Vectorstore
if os.path.exists(DB_PATH):
    vector_store = FAISS.load_local(
        DB_PATH, 
        embeddings, 
        allow_dangerous_deserialization=True
    )
else:
    vector_store = None

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


@tool
def rag_tool(query: str) -> dict:
    """
    Retrieve relevant information from the uploaded PDF documents.
    Use this tool when the user asks questions about uploaded files or document contents.
    """
    global vector_store
    if vector_store is None:
        return {"error": "No PDF documents have been uploaded or indexed yet."}

    retriever = vector_store.as_retriever(search_type='similarity', search_kwargs={'k': 4})
    result = retriever.invoke(query)

    context = [doc.page_content for doc in result]
    metadata = [doc.metadata for doc in result]

    return {
        'query': query,
        'context': context,
        'metadata': metadata
    }


# Merge all tools
tools = [search_tool, get_stock_price, calculator, rag_tool]
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

# -------------------
# Helper Functions

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)


def ingest_pdf(file_bytes: bytes, thread_id: str, filename: str) -> dict:
    """
    Processes uploaded PDF bytes, chunks them, and embeds into FAISS vector store.
    """
    global vector_store

    # Create temporary PDF file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file_bytes)
        tmp_path = tmp_file.name

    try:
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        num_docs = len(docs)

        splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)
        num_chunks = len(chunks)

        for chunk in chunks:
            chunk.metadata["filename"] = filename
            chunk.metadata["thread_id"] = thread_id

        if vector_store is None:
            vector_store = FAISS.from_documents(chunks, embeddings)
        else:
            vector_store.add_documents(chunks)

        vector_store.save_local(DB_PATH)

        return {
            "filename": filename,
            "documents": num_docs,
            "chunks": num_chunks
        }
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)