import streamlit as st
from langGraph_backend import chatbot
from langchain_core.messages import HumanMessage

# PAGE CONFIG & DECENT STYLING
st.set_page_config(
    page_title="LangGraph AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Theme-Adaptive CSS (Supports Light & Dark Modes seamlessly)
st.markdown("""
<style>
    /* Base CSS Variables & Reset */
    :root {
        --card-bg-light: #f8f9fa;
        --card-border-light: #e9ecef;
        --card-bg-dark: #161b22;
        --card-border-dark: #30363d;
        --subtext-light: #6c757d;
        --subtext-dark: #8b949e;
    }

    /* Header Styling */
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

    /* Dynamic Divider */
    hr {
        margin-top: 0;
        border-color: var(--card-border-light);
    }
    @media (prefers-color-scheme: dark) {
        hr {
            border-color: var(--card-border-dark);
        }
    }

    /* Adaptive Welcome Container */
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

    /* Dark Mode Adjustments for Container */
    @media (prefers-color-scheme: dark) {
        .welcome-container {
            border-color: var(--card-border-dark);
            background-color: var(--card-bg-dark);
        }
        .welcome-container p {
            color: var(--subtext-dark);
        }
    }

    /* Footer text inside sidebar */
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
""", unsafe_allow_html=True)


# SIDEBAR SETUP
with st.sidebar:
    st.title("🤖 Chat Control")
    st.markdown("---")
    
    st.caption("Active Session Thread:")
    st.code("thread-1", language="text")
    
    st.markdown("---")
    
    # Clear Chat Feature
    if st.button("🗑️ Clear Conversation", use_container_width=True, type="secondary"):
        st.session_state['message_history'] = []
        st.rerun()

    st.markdown("---")
    st.markdown(
        "<div class='sidebar-footer'>"
        "Powered by <b>LangGraph & Streamlit</b><br>"
        "Made by <b>Salman Khan</b> ❤️"
        "</div>", 
        unsafe_allow_html=True
    )


# MAIN INTERFACE & LOGIC (UNTOUCHED)

# Header Title
st.markdown("""
<div class="main-header">
    <h1>LangGraph AI Assistant</h1>
    <p>Real-time streaming conversation powered by LangGraph runtime</p>
</div>
""", unsafe_allow_html=True)

CONFIG = {'configurable': {'thread_id': 'thread-1'}}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Display Empty State if no history exists
if not st.session_state['message_history']:
    st.markdown("""
    <div class="welcome-container">
        <h3>How can I help you today?</h3>
        <p>Type your message below to start a streaming conversation.</p>
    </div>
    """, unsafe_allow_html=True)

# loading the conversation history 
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Ask anything...')

if user_input:

    # first add the message to message history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # stream assistant response
    with st.chat_message('assistant'):

        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config={'configurable': {'thread_id': 'thread-1'}},
                stream_mode='messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})