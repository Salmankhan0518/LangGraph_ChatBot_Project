import uuid
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph_tool_backend import chatbot, retrieve_all_threads

# =========================== Page Config ===========================
st.set_page_config(
    page_title="LangGraph AI Assistant",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================== CSS ===========================
st.markdown(
    """
    <style>
        /* Global Typography & Reset */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Main Container Layout Spacing */
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2rem;
            max-width: 950px;
        }

        /* Top Header Banner */
        .main-app-header {
            border-bottom: 1px solid rgba(128, 128, 128, 0.15);
            padding-bottom: 1rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .main-app-title {
            font-size: 1.4rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: var(--text-color);
            margin: 0;
        }

        .main-app-subtitle {
            font-size: 0.85rem;
            opacity: 0.6;
            margin-top: 0.2rem;
        }

        /* Active Thread Badge */
        .status-badge {
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.25rem 0.6rem;
            border-radius: 20px;
            background-color: rgba(66, 133, 244, 0.1);
            color: #4285f4;
            border: 1px solid rgba(66, 133, 244, 0.2);
            display: inline-block;
        }

        /* Sidebar Custom Styling */
        section[data-testid="stSidebar"] {
            background-color: #fafbfc;
            border-right: 1px solid #e5e8eb;
        }
        
        @media (prefers-color-scheme: dark) {
            section[data-testid="stSidebar"] {
                background-color: #111318;
                border-right: 1px solid #1f232b;
            }
        }

        .sidebar-brand {
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: -0.01em;
            margin-bottom: 0.2rem;
        }

        .sidebar-subtext {
            font-size: 0.78rem;
            opacity: 0.55;
            margin-bottom: 1.2rem;
        }

        /* Button Styling Refinement */
        .stButton button {
            border-radius: 6px;
            font-weight: 500;
            font-size: 0.85rem;
            box-shadow: none !important;
        }

        /* Empty / Welcome Card */
        .welcome-card {
            border: 1px dashed rgba(128, 128, 128, 0.25);
            border-radius: 12px;
            padding: 3.5rem 2rem;
            text-align: center;
            margin: 2rem 0;
            background-color: rgba(128, 128, 128, 0.02);
        }

        .welcome-card h3 {
            font-size: 1.35rem;
            font-weight: 600;
            margin-bottom: 0.4rem;
        }

        .welcome-card p {
            font-size: 0.9rem;
            opacity: 0.65;
            margin: 0;
        }

        /* Chat Input Formatting */
        div[data-testid="stChatInput"] {
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================== Utilities ===========================
def generate_thread_id():
    return uuid.uuid4()


def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(thread_id)
    st.session_state["message_history"] = []


def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def load_conversation(thread_id):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    return state.values.get("messages", [])


# ======================= Session Initialization ===================
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

add_thread(st.session_state["thread_id"])

# ============================ Sidebar ============================
with st.sidebar:
    st.markdown('<div class="sidebar-brand">LangGraph Workspace</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtext">Stateful Multi-Thread Engine</div>', unsafe_allow_html=True)

    if st.button("New Chat", use_container_width=True, type="primary"):
        reset_chat()
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Recent Conversations**")

    for thread_id in st.session_state["chat_threads"][::-1]:
        is_active = thread_id == st.session_state["thread_id"]
        button_type = "secondary" if not is_active else "primary"

        short_id = f"Session - {str(thread_id)[:8]}"

        if st.button(
            short_id,
            key=f"btn_{thread_id}",
            use_container_width=True,
            type=button_type,
        ):
            st.session_state["thread_id"] = thread_id
            messages = load_conversation(thread_id)

            temp_messages = []
            for msg in messages:
                role = "user" if isinstance(msg, HumanMessage) else "assistant"
                temp_messages.append({"role": role, "content": msg.content})
            st.session_state["message_history"] = temp_messages
            st.rerun()

# ============================ Main Header ============================
st.markdown(
    f"""
    <div class="main-app-header">
        <div>
            <div class="main-app-title">LangGraph AI Assistant</div>
            <div class="main-app-subtitle">Powered by LangGraph Agent System & SQLite Checkpoints</div>
        </div>
        <div>
            <span class="status-badge">Active Thread: {str(st.session_state['thread_id'])[:8]}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================ Main UI ============================

# Empty Welcome State
if not st.session_state["message_history"]:
    st.markdown(
        """
        <div class="welcome-card">
            <h3>How can I assist you today?</h3>
            <p>Type your query below to start a conversation with automated tool execution.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Render conversation history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Ask a question or request a task...")

if user_input:
    # Show user's message
    st.session_state["message_history"].append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.write(user_input)

    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {"thread_id": st.session_state["thread_id"]},
        "run_name": "chat_turn",
    }

    # Assistant streaming block
    with st.chat_message("assistant"):
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"Executing {tool_name}...", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"Executing {tool_name}...",
                            state="running",
                            expanded=True,
                        )

                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        # Finalize status
        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="Execution complete", state="complete", expanded=False
            )

    # Save assistant message
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )