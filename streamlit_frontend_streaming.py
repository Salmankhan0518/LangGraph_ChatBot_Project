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

# Custom CSS for polished interface
st.markdown("""
<style>
    /* Main Background & Text Cleanups */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Header Styling */
    .main-header {
        text-align: center;
        padding-bottom: 2rem;
    }
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.2rem;
    }
    .main-header p {
        color: #8b949e;
        font-size: 0.95rem;
    }

    /* Subtle divider */
    hr {
        border-color: #21262d;
        margin-top: 0;
    }

    /* Sidebar Styling */
    .stSidebar {
        background-color: #161b22;
        border-right: 1px solid #21262d;
    }
    
    /* Empty State Welcome Container */
    .welcome-container {
        text-align: center;
        padding: 3rem 1rem;
        border: 1px dashed #30363d;
        border-radius: 12px;
        background-color: #161b22;
        margin-top: 2rem;
    }
    .welcome-container h3 {
        color: #c9d1d9;
        font-weight: 600;
    }
    .welcome-container p {
        color: #8b949e;
        font-size: 0.9rem;
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
        "<div style='font-size: 0.8rem; color: #8b949e; text-align: center;'>"
        "Powered by <b>LangGraph & Streamlit</b>"
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