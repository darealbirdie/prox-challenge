#!/usr/bin/env python3
"""
Frontend for Claude Welding Agent - Interactive Chat Interface
Run with: streamlit run app.py
"""

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from claude_agent import ProxWeldingAgent
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="Prox Welding Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    .chat-container {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
    }
    .user-msg {
        background: linear-gradient(135deg, #00d4ff, #0099cc);
        color: white;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .bot-msg {
        background: rgba(255,255,255,0.1);
        color: #e0e0e0;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 4px solid #00d4ff;
    }
    .sidebar .sidebar-content {
        background: rgba(0,0,0,0.3);
    }
    h1, h2, h3 {
        color: #00d4ff;
    }
</style>
""")

# Sidebar
with st.sidebar:
    st.title("🤖 Prox Agent")
    st.markdown("---")
    
    if st.button("🚀 Initialize Agent", use_container_width=True):
        with st.spinner("Connecting..."):
            st.session_state.agent = ProxWeldingAgent()
        st.success("✓ Agent Ready!")
    
    st.markdown("---")
    
    if st.session_state.agent:
        stats = st.session_state.agent.get_knowledge_stats()
        st.metric("Knowledge Notes", stats['total_notes'])
        st.metric("Total Tags", len(stats['tags']))
    
    st.markdown("---")
    st.markdown("### Quick Actions")
    
    if st.button("📊 Clear Chat", use_container_width=True):
        st.session_state.messages = []
    
    st.markdown("---")
    st.markdown("""
    **Features**
    - RAG-based Q&A
    - PDF extraction
    - Image analysis
    - Auto-linking
    """)

# Main Chat Interface
st.title("🤖 Prox Welding Assistant")
st.markdown("Ask questions about welding equipment, safety, and procedures.")
st.markdown("---")

# Display chat messages
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        if message['role'] == 'user':
            st.markdown(f"""
                <div class="user-msg">
                    <strong>You:</strong> {message['content']}
                </div>
            """, unsafe_allow_html=True)
        else:
            with st.expander("🤖 Agent Response", expanded=True):
                st.markdown(f"**Answer:**\n\n{message['content']}")
                if 'sources' in message and message['sources']:
                    st.caption(f"Sources: {', '.join(message['sources'][:5])}")

# Chat input
if st.session_state.agent is None:
    st.warning("⚠️ Please initialize the agent first (click button in sidebar)")
else:
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input(
            "Ask a question about welding:",
            placeholder="e.g., What's the MIG welding duty cycle at 200A?",
            key="user_input"
        )
    with col2:
        send_btn = st.button("Send", use_container_width=True, type="primary")
    
    if (user_input and send_btn) or (user_input and st.session_state.get("enter_pressed", False)):
        # Add user message
        st.session_state.messages.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now()
        })
        
        # Get AI response
        with st.spinner("🤖 Agent is thinking..."):
            try:
                result = st.session_state.agent.answer_question(user_input)
                
                answer = result['answer']
                sources = result.get('sources', [])
                
                # Add bot message
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': answer,
                    'sources': sources,
                    'timestamp': datetime.now()
                })
                
            except Exception as e:
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': f"Error: {str(e)}",
                    'timestamp': datetime.now()
                })
        
        # Rernder updated chat
        st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>Prox Welding Agent | Claude-powered R&A System</small>
</div>
""", unsafe_allow_html=True)
