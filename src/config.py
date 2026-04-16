import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    HF_TOKEN = os.getenv("HF_TOKEN")
    
    # Model configs
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    SENTIMENT_MODEL = "ProsusAI/finbert"
    
    # Storage paths
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", os.path.join(DATA_DIR, "chroma_db"))
    SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", os.path.join(DATA_DIR, "news.db"))
    
    # Dataset config
    HF_DATASET_PATH = "Brianferrell787/financial-news-multisource"
    
    # We load a small subset for testing unless specified otherwise
    DEFAULT_SUBSETS = os.getenv(
        "DEFAULT_SUBSETS", 
        "cnbc_headlines,bloomberg_reuters,sp500_daily_headlines"
    ).split(',')

# Ensure data dictionary exists when config is loaded
os.makedirs(Config.DATA_DIR, exist_ok=True)
