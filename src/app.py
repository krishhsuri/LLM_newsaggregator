import os
import sys
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.digest.generator import DailyDigestAgent
from src.chat.rag_chain import RAGChatbot

# --- UI CONFIGURATION & PREMIUM STYLING ---
# Streamlit allows arbitrary CSS injection, letting us break out of the standard basic layout
st.set_page_config(page_title="AI News Terminal", layout="wide", page_icon="📈")

st.markdown("""
    <style>
        .stApp {
            background-color: #0f172a;
            color: #f8fafc;
        }
        h1, h2, h3 {
            color: #38bdf8 !important;
            font-family: 'Inter', sans-serif;
        }
        .stButton>button {
            background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
            border: none;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            width: 100%;
        }
        .stButton>button:hover {
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.5);
            border: none;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📈 AI Financial Terminal")
st.markdown("*Your MLOps-powered, Sentiment-Aware News Aggregator.*")

# --- INITIALIZE STATE & AI ENGINES ---
# @st.cache_resource ensures we only boot up the databases and models ONCE when the app starts
@st.cache_resource
def load_engines():
    digest_agent = DailyDigestAgent()
    chat_agent = RAGChatbot()
    return digest_agent, chat_agent

digest_agent, chat_agent = load_engines()

# In Streamlit, everything refreshes constantly. We need manually save chat history to `st.session_state`
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- LAYOUT WIDGETS ---
st.divider()

# We split the screen: 35% for the Digest, 65% for the RAG Chat
col1, col2 = st.columns([1, 1.8])

with col1:
    st.subheader("📰 Daily Digest")
    st.markdown("Generate a high-level summary of exactly what the market is doing today.")
    
    if st.button("Generate Today's Digest", use_container_width=True):
        with st.spinner("Analyzing Market Data..."):
            result = digest_agent.generate_digest()
            if result:
                st.markdown(result.text)
            else:
                st.warning("No data found to generate a digest.")

with col2:
    st.subheader("🤖 RAG Assitant")
    
    # 1. Display the previous chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # 2. Catch the User Input
    prompt = st.chat_input("Ask a question about the market...")
    if prompt:
        # a. Save user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # b. Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # c. Query the AI
        with st.spinner("Searching database..."):
            answer = chat_agent.ask(prompt)
            
        # d. Display the AI message
        with st.chat_message("assistant"):
            st.markdown(answer)
            
        # e. Save AI message
        st.session_state.messages.append({"role": "assistant", "content": answer})
