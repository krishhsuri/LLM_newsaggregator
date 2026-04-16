import os
import sys
import json
import hashlib
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.config import Config
# TODO: Import stream_news_from_hf from src.ingestion.hf_loader
# TODO: Import NewsDatabase from src.ingestion.database
from src.ingestion.hf_loader import stream_news_from_hf
from src.ingestion.database import NewsDatabase

def run_ingestion(limit_per_subset=100):
    print("🚀 Starting Data Ingestion Pipeline...\n")
    
    # 1. Initialize our databases
    # TODO: Create an instance of NewsDatabase (e.g., db = NewsDatabase())
    db = NewsDatabase()
    
    # 2. Start streaming from HuggingFace
    # TODO: Call stream_news_from_hf(limit=limit_per_subset)
    news_stream = stream_news_from_hf(limit=limit_per_subset) 
    
    print(f"Ingesting up to {limit_per_subset} articles per subset...")
    
    # We use tqdm to show a progress bar
    for article in tqdm(news_stream, desc="Saving to DB"):
        
        # 3. Extract the metadata we need
        raw_text = article.get("text", "")
        # Skip if there's no text
        if not raw_text or len(raw_text) < 10:
            continue
            
        date = article.get("date", "Unknown")
        
        # We need a unique ID. We can make one by hashing the text.
        article_id = hashlib.md5(raw_text.encode('utf-8')).hexdigest()
        
        # The extra stuff like URL and source is hiding inside a JSON string called 'extra_fields'
        source = "Unknown"
        url = ""
        try:
            extras = json.loads(article.get("extra_fields", "{}"))
            source = extras.get("source", "Unknown")
            url = extras.get("url", "")
        except:
            db.save_article(article_id,text=raw_text,date=date,source=source,url=url)
            
        # 4. Save to the databases!
        # TODO: Call `db.save_article` and pass all the variables we just created:
        # article_id, text=raw_text, date=date, source=source, url=url
        

if __name__ == "__main__":
    # We'll ingest a small test batch of 100 articles per subset for now
    run_ingestion(limit_per_subset=100)
    print("\n✅ Ingestion Complete!")
