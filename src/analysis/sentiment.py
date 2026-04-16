import os
import sys
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.config import Config
from src.ingestion.database import NewsDatabase, Article

# HuggingFace Transformers is the standard ML library for text models
from transformers import pipeline

class SentimentAnalyzer:
    def __init__(self):
        print("Loading FinBERT Model...")
        # 1. Setup the HuggingFace Pipeline
        # TODO: Initialize a transformers pipeline.
        # Hint: use `pipeline("sentiment-analysis", model=Config.SENTIMENT_MODEL)`
        self.analyzer = pipeline("sentiment-analysis",model=Config.SENTIMENT_MODEL)
        
        self.db = NewsDatabase()

    def process_unprocessed_articles(self):
        """Finds all articles without sentiment and processes them."""
        print("Connecting to database...")
        
        # We need a session to query SQLite
        with self.db.Session() as session:
            unprocessed_articles = session.query(Article).filter(Article.sentiment_label == "UNPROCESSED").all()
            # 2. Query for unprocessed articles
            # TODO: Query the Article table for items where sentiment_label == "UNPROCESSED"
            # It should look something like: `session.query(Article).filter( ... ).all()`
            
            if not unprocessed_articles:
                print("No unprocessed articles found!")
                return
                
            print(f"Found {len(unprocessed_articles)} articles to process.")
            
            # 3. Loop through and analyze
            for article in tqdm(unprocessed_articles, desc="Analyzing Sentiment"):
                try:
                    # Neural networks have a maximum 'context window'. FinBERT rejects texts longer than 512 tokens.
                    # We truncate to the first 1000 characters to safely feed it just the headline/intro paragraph.
                    text_preview = article.text[:1000]
                    result = self.analyzer(text_preview)
                    # 4. Generate the sentiment
                    # TODO: Pass `text_preview` into `self.analyzer()`. 
                    # Note: Pipeline returns a list containing a dict, e.g., [{'label': 'positive', 'score': 0.99}]
                    # Extract the dictionary out of the list before moving to step 5!                    
                    # 5. Update the SQLite object
                    # TODO: Set `article.sentiment_label` to the result's label
                    article.sentiment_label = result[0]['label']
                    article.sentiment_score = result[0]['score']
                    # TODO: Set `article.sentiment_score` to the result's score
                    session.merge(article)
                    
                except Exception as e:
                    # If it fails (token size issues, weird characters), we mark it to not try again
                    article.sentiment_label = "ERROR"
            
            # 6. Commit the changes back to the database safely
            print("Saving results to database...")
            session.commit()
            print("Done!")

if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    analyzer.process_unprocessed_articles()
