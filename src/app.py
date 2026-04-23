import os
import sys
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from scripts.ingest_data import run_ingestion
from src.config import Config
from src.digest.generator import DailyDigestAgent
from src.chat.rag_chain import RAGChatbot
from src.analysis.sentiment import SentimentAnalyzer
# --- SELF-HEALING STARTUP PIPELINE ---
# This function checks if the database exists. If not, it builds everything from scratch.
# In MLOps, systems should bootstrap themselves without human intervention.
@st.cache_resource
def initialize_pipeline():
    """Checks if data exists; if not, runs the full ingestion + sentiment pipeline."""
    
    # Check if the SQLite database file already exists on disk
    if os.path.exists(Config.SQLITE_DB_PATH):
        print("✅ Database found. Skipping ingestion.")
        return True
    
    print("⚠️ No database found. Running auto-ingestion pipeline...")
    
    # TODO: Import and run the ingestion pipeline
    # 1. Import `run_ingestion` from `scripts.ingest_data`
    # 2. Call `run_ingestion(limit_per_subset=50)` (we use 50 to keep cloud startup fast)
    run_ingestion(limit_per_subset=50)
    
    # TODO: Import and run the sentiment pipeline
    # 3. Import `SentimentAnalyzer` from `src.analysis.sentiment`
    # 4. Create an instance: `analyzer = SentimentAnalyzer()`
    # 5. Call `analyzer.process_unprocessed_articles()`
    analyzer = SentimentAnalyzer()
    analyzer.process_unprocessed_articles()
    
    print("✅ Auto-ingestion complete!")
    return True

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

# Run the startup health check, then load the AI models
initialize_pipeline()
digest_agent, chat_agent = load_engines()

from src.analysis.analytics import render_analytics_dashboard

# In Streamlit, everything refreshes constantly. We need to manually save chat history to `st.session_state`
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- LAYOUT WIDGETS ---
st.divider()

tab1, tab2, tab3 = st.tabs(["📰 Daily Digest", "🤖 RAG Assistant", "📊 Analytics"])

with tab1:
    st.markdown("Generate a high-level AI summary of what the market is doing today.")
    
    if st.button("Generate Today's Digest", use_container_width=True):
        with st.spinner("Analyzing Market Data..."):
            result = digest_agent.generate_digest()
            if result:
                st.markdown(result.text)
            else:
                st.warning("No data found to generate a digest.")

with tab2:
    # 1. Display the previous chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # 2. Catch the User Input
    prompt = st.chat_input("Ask a question about the market...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.spinner("Searching database..."):
            answer = chat_agent.ask(prompt)
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

with tab3:
    render_analytics_dashboard()
