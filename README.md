LangGraph + Ollama Streamlit Chatbot

An interactive, stateful AI Chatbot application built using Streamlit, LangGraph, and LangChain Ollama. It leverages local LLMs (like qwen2.5:3b) via Ollama with in-memory thread checkpointing to maintain smooth, continuous conversations.

Features

Local LLM Integration: Powered by Ollama (qwen2.5:3b).

Stateful Conversation: Utilizes LangGraph MemorySaver and unique thread IDs for session management.

Interactive UI: Clean Streamlit chat interface (st.chat_input, st.chat_message).

Session Controls: Easy chat resetting via the sidebar widget.

Installation & Setup

1. Prerequisites

Make sure you have Python 3.10+ installed. Also, download and install Ollama.

Pull the required model in your terminal:

ollama pull qwen2.5:3b