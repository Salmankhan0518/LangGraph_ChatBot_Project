# LangGraph AI Assistant

An interactive, multi-thread AI chatbot built with **LangGraph**, **Streamlit**, and local LLMs via **Ollama**. This application features persistent thread state management using **SQLite**, real-time streaming responses, and adaptive light/dark UI styling.


## Features

* **Local LLM Integration:** Powered by `ChatOllama` (defaulting to `qwen2.5:3b` or custom local models) for complete privacy and offline capabilities.
* **Stateful Multi-Thread Persistence:** Powered by LangGraph's `SqliteSaver` checkpointer, allowing users to create, switch, and resume distinct chat sessions seamlessly.
* **Real-Time Streaming:** Instant message response streaming powered by Streamlit's `st.write_stream` and LangGraph event loops.
* **Responsive Theme-Adaptive UI:** Features a sleek, modern Streamlit UI that automatically adjusts to light and dark system preferences.
* **Thread Management:** Easily create new chat threads, inspect active thread UUIDs, load previous histories, or clear current conversations.

---

## 📂 Project Structure

```text
.
├── frontend.py                     # Streamlit UI & session management
├── langgraph_database_backend.py   # LangGraph graph, Ollama LLM setup, & SQLite checkpointer
├── chatbot.db                      # SQLite database storing conversation checkpoints (Auto-generated)
├── requirements.txt                # Python dependencies
└── README.md                       # Project documentation

```

---

## Prerequisites

Before getting started, make sure you have installed:

1. **Python 3.10+**
2. **Ollama:** Install from [ollama.com](https://ollama.com/?utm_source=gemini) and pull your target model:
```bash
ollama pull qwen2.5:3b

```



---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/langgraph-ai-assistant.git
cd langgraph-ai-assistant

```

### 2. Create a Virtual Environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate

```

### 3. Install Dependencies

Create a `requirements.txt` file (if not already present) with:

```text
streamlit
langchain-core
langchain-ollama
langgraph
langgraph-checkpoint-sqlite

```

Then install them using:

```bash
pip install -r requirements.txt

```

### 4. Run the Application

Start the Streamlit application by running:

```bash
streamlit run frontend.py

```

---

## System Architecture & Workflow

1. **Backend (`langgraph_database_backend.py`):**
* Defines `ChatState` with an append-only message history annotation.
* Compiles a `StateGraph` backed by SQLite checkpointer (`SqliteSaver`).
* Interacts with local Ollama instances through `ChatOllama`.
* Exposes `retrieve_all_threads()` to query existing chat thread IDs directly from SQLite checkpoints.


2. **Frontend (`frontend.py`):**
* Configures custom CSS and sidebar controls.
* Manages state across sessions using Streamlit's `st.session_state`.
* Streams chunks incrementally from `chatbot.stream(...)` onto the user interface.



---

## Customization

* **Change the LLM Model:** Modify the model string in `langgraph_database_backend.py`:
```python
llm = ChatOllama(model="llama3.2")  # or mistral, deepseek-r1, etc.

```


* **Database File:** SQLite data is persisted locally in `chatbot.db`. Delete this file if you wish to reset all stored conversation history completely.

---