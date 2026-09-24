import uuid
from langchain_core.messages import HumanMessage
from langGraph_backend import chatbot
import streamlit as st

# ********************* Utility functions ********************


def generate_thread_id():
  return str(uuid.uuid4())


def reset_chat():
  thread_id = generate_thread_id()
  st.session_state['thread_id'] = thread_id
  add_thread(st.session_state['thread_id'])
  st.session_state['message_history'] = []


def add_thread(thread_id):
  if thread_id not in st.session_state['chat_threads']:
    st.session_state['chat_threads'].append(thread_id)


def load_conversation(thread_id):
  try:
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    if state and hasattr(state, 'values') and 'messages' in state.values:
      return state.values['messages']
    return []
  except Exception:
    return []


# PAGE CONFIG & STYLING
st.set_page_config(
    page_title="LangGraph AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ******************* Session Setup ***********************
if 'message_history' not in st.session_state:
  st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
  st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
  st.session_state['chat_threads'] = []

add_thread(st.session_state['thread_id'])


# Custom Theme-Adaptive CSS
st.markdown(
    """
<style>
    :root {
        --card-bg-light: #f8f9fa;
        --card-border-light: #e9ecef;
        --card-bg-dark: #161b22;
        --card-border-dark: #30363d;
        --subtext-light: #6c757d;
        --subtext-dark: #8b949e;
    }

    .main-header {
        text-align: center;
        padding-bottom: 1.5rem;
    }
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        color: var(--text-color);
    }
    .main-header p {
        font-size: 0.95rem;
        color: var(--subtext-light);
    }
    @media (prefers-color-scheme: dark) {
        .main-header p {
            color: var(--subtext-dark);
        }
    }

    hr {
        margin-top: 0;
        border-color: var(--card-border-light);
    }
    @media (prefers-color-scheme: dark) {
        hr {
            border-color: var(--card-border-dark);
        }
    }

    .welcome-container {
        text-align: center;
        padding: 3rem 1.5rem;
        border: 1px dashed var(--card-border-light);
        border-radius: 12px;
        background-color: var(--card-bg-light);
        margin-top: 1.5rem;
    }
    .welcome-container h3 {
        font-weight: 600;
        color: var(--text-color);
        margin-bottom: 0.5rem;
    }
    .welcome-container p {
        font-size: 0.9rem;
        color: var(--subtext-light);
        margin: 0;
    }

    @media (prefers-color-scheme: dark) {
        .welcome-container {
            border-color: var(--card-border-dark);
            background-color: var(--card-bg-dark);
        }
        .welcome-container p {
            color: var(--subtext-dark);
        }
    }

    .sidebar-footer {
        font-size: 0.8rem;
        text-align: center;
        color: var(--subtext-light);
    }
    @media (prefers-color-scheme: dark) {
        .sidebar-footer {
            color: var(--subtext-dark);
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


# SIDEBAR SETUP
with st.sidebar:
  st.title("🤖 Chat Control")
  st.title("LangGraph Chatbot")

  if st.button("➕ New Chat", use_container_width=True):
    reset_chat()
    st.rerun()

  st.header("My conversations")

  for t_id in st.session_state["chat_threads"][::-1]:
    # Active thread highlighted with primary button style
    button_type = (
        "primary" if t_id == st.session_state["thread_id"] else "secondary"
    )

    if st.button(
        f" {str(t_id)[:8]}...",
        key=f"btn_{t_id}",
        type=button_type,
        use_container_width=True,
    ):
      st.session_state["thread_id"] = t_id
      messages = load_conversation(t_id)

      temp_message = []
      for msg in messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        temp_message.append({"role": role, "content": msg.content})

      # FIXED: Correct variable name used & rerun triggered
      st.session_state["message_history"] = temp_message
      st.rerun()

  st.markdown("---")

  st.caption("Active Session Thread:")
  st.code(st.session_state["thread_id"], language="text")

  st.markdown("---")

  # Clear Chat Feature
  if st.button(
      "🗑️ Clear Conversation", use_container_width=True, type="secondary"
  ):
    st.session_state["message_history"] = []
    st.rerun()

  st.markdown("---")
  st.markdown(
      "<div class='sidebar-footer'>"
      "Powered by <b>LangGraph & Streamlit</b><br>"
      "Made by <b>Salman Khan</b> ❤️"
      "</div>",
      unsafe_allow_html=True,
  )


# MAIN INTERFACE & LOGIC

# Header Title
st.markdown(
    """
<div class="main-header">
    <h1>LangGraph AI Assistant</h1>
    <p>Real-time streaming conversation powered by LangGraph runtime</p>
</div>
""",
    unsafe_allow_html=True,
)

CONFIG = {"configurable": {"thread_id": st.session_state["thread_id"]}}


# Display Empty State if no history exists
if not st.session_state["message_history"]:
  st.markdown(
      """
    <div class="welcome-container">
        <h3>How can I help you today?</h3>
        <p>Type your message below to start a streaming conversation.</p>
    </div>
    """,
      unsafe_allow_html=True,
  )

# Display active thread's conversation history
for message in st.session_state["message_history"]:
  with st.chat_message(message["role"]):
    st.text(message["content"])

user_input = st.chat_input("Ask anything...")

if user_input:
  # First add the message to message history
  st.session_state["message_history"].append(
      {"role": "user", "content": user_input}
  )
  with st.chat_message("user"):
    st.text(user_input)

  # Stream assistant response
  with st.chat_message("assistant"):
    ai_message = st.write_stream(
        message_chunk.content
        for message_chunk, metadata in chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode="messages",
        )
    )

  st.session_state["message_history"].append(
      {"role": "assistant", "content": ai_message}
  )