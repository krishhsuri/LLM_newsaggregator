import os
import sys

# Ensure our src module is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import chromadb
from chromadb.utils import embedding_functions
from sqlalchemy import create_engine, Column, String, Text, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from src.config import Config

# --- SQLite Schema Setup ---
Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    
    # We use the article ID as the primary key so we never save duplicates
    id = Column(String, primary_key=True)
    date = Column(String)
    source = Column(String)
    text = Column(Text)
    url = Column(String, nullable=True)
    
    # We will fill these later in Phase 3!
    sentiment_label = Column(String, default="UNPROCESSED")
    sentiment_score = Column(Float, default=0.0)

# --- Database Manager ---
class NewsDatabase:
    def __init__(self):
        # 1. Setup SQLite
        # We create a local file-based database for structured metadata
        self.engine = create_engine(f"sqlite:///{Config.SQLITE_DB_PATH}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # 2. Setup Vector Store (ChromaDB)
        # TODO: Initialize the ChromaDB client to save data persistently to your machine.
        # Hint: Use `chromadb.PersistentClient` and give it the shape: path=Config.CHROMA_PERSIST_DIR
        self.chroma_client =  chromadb.PersistentClient(path = Config.CHROMA_PERSIST_DIR)
        # 3. Embedding Model Setup
        # This function turns text into dense mathematical vectors (arrays of floats) for semantic search.
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=Config.EMBEDDING_MODEL
        )
        
        # 4. Create the Vector Collection
        # TODO: Use `self.chroma_client.get_or_create_collection`
        # Name it "financial_news" and pass `embedding_function=self.embed_fn`
        self.collection = self.chroma_client.get_or_create_collection(name="financial_news",embedding_function=self.embed_fn)
        

    def save_article(self, article_id, text, date, source, url=""):
        """Saves an article to BOTH SQLite and ChromaDB"""
        
        # TODO: 1. Save to SQLite
        # Use a context manager: `with self.Session() as session:`
        # create your article object: `new_article = Article(id=..., date=..., text=..., source=..., url=...)`
        # `session.merge(new_article)`  <-- Merge behaves like an UPSERT, preventing duplicates
        # `session.commit()`
        with self.Session() as session:
            new_article = Article(id=article_id,date=date,text=text,source=source,url=url)
            session.merge(new_article)
            session.commit()
        # TODO: 2. Save to ChromaDB
        # Call `self.collection.upsert(...)`
        # Pass 3 arguments as lists: 
        #   documents=[text]
        #   metadatas=[{"date": date, "source": source}]
        #   ids=[article_id]
        self.collection.upsert(documents=[text],metadatas=[{"date": date, "source": source}],ids=[article_id])


if __name__ == "__main__":
    print("Testing Database Components...")
    
    try:
        db = NewsDatabase()
        print("✅ Databases initialized!")
        
        # Let's test saving a fake article
        print("Saving test article...")
        db.save_article(
            article_id="test_123",
            text="Tech stocks surged by 10% today following the announcement of a revolutionary AI chip.",
            date="2026-04-16T12:00:00Z",
            source="Mock News"
        )
        
        print("✅ Article Saved to SQLite and ChromaDB!")
        
        # Let's test checking if the embedding worked!
        print("\nTesting Semantic Search...")
        results = db.collection.query(
            query_texts=["Did hardware companies do well today?"],
            n_results=1
        )
        print("Query: 'Did hardware companies do well today?'")
        print("Result:", results['documents'][0][0])
        print("✅ Success!")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
