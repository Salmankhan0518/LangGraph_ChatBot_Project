import streamlit as st
from langGraph_backend import chatbot
from langchain_core.messages import HumanMessage

# Page Configuration & Styling
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished UI
st.markdown("""
<style>
    /* Modern Chat Styling */
    .stApp {
        max-width: 900px;
        margin: 0 auto;
    }
    .stChatMessage {
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    /* Header Container */
    .header-box {
        text-align: center;
        padding: 1rem 0 2rem 0;
    }
    .header-box h1 {
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .header-box p {
        color: #6c757d;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

CONFIG = {'configurable': {'thread_id': 'thread-1'}}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Sidebar Controls
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.title("Settings & Actions")
    st.markdown("---")
    
    # Clear Chat Feature
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state['message_history'] = []
        st.rerun()
        
    st.markdown("---")
    st.caption("⚡ Powered by **LangGraph** & **Streamlit**")

# Main Page Header
st.markdown("""
<div class="header-box">
    <h1>🤖 Smart AI Assistant</h1>
    <p>Powered by LangGraph Agent with Persistent Memory</p>
</div>
""", unsafe_allow_html=True)

# Loading the conversation history 
for message in st.session_state['message_history']:
    avatar = "👤" if message['role'] == "user" else "🤖"
    with st.chat_message(message['role'], avatar=avatar):
        st.markdown(message['content'])

user_input = st.chat_input('Type your message here...')

if user_input:

    # first add the message to message history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user', avatar="👤"):
        st.markdown(user_input)

    # Spinner animation while generating response
    with st.chat_message('assistant', avatar="🤖"):
        with st.spinner("Thinking..."):
            response = chatbot.invoke({'messages': HumanMessage(content=user_input)}, config=CONFIG)
            ai_message = response['messages'][-1].content
            st.markdown(ai_message)

    # first add the message to message history
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})