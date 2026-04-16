import os
import sys

# Ensure our src module is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import google.generativeai as genai
from src.config import Config
from src.ingestion.database import NewsDatabase, Article
from src.digest.prompts import SYSTEM_PROMPT, DIGEST_PROMPT

class DailyDigestAgent:
    def __init__(self):
        self.db = NewsDatabase()
        
        # 1. Setup the Gemini API Client
        # TODO: Call `genai.configure()` and pass `api_key=Config.GEMINI_API_KEY`
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        # 2. Initialize the LLM
        # TODO: Create the model instance using `genai.GenerativeModel("gemini-1.5-flash")`
        # Assign it to `self.model`
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def generate_digest(self, limit=10):
        print("Gathering articles for today's digest...")
        
        with self.db.Session() as session:
            # We'll just grab the 10 most recent articles that have sentiment
            articles = session.query(Article).filter(Article.sentiment_label != "UNPROCESSED").limit(limit).all()
            
            if not articles:
                print("No processed articles found.")
                return None
                
            # 3. Format the data into an LLM-friendly string block
            formatted_text = ""
            for a in articles:
                formatted_text += f"\n- [{a.sentiment_label.upper()}] {a.date}: {a.text[:300]}..."
                
            # 4. Inject the articles into our Prompt Template
            # TODO: Call `DIGEST_PROMPT.format(articles_text=formatted_text)` and save it to `final_prompt`
            final_prompt = DIGEST_PROMPT.format(articles_text=formatted_text)
            
            print(f"Sending {len(articles)} articles to Gemini...")
            
            # 5. Call the LLM
            # TODO: Call `self.model.generate_content(...)`
            # Pass it a list containing the `SYSTEM_PROMPT` first, and your `final_prompt` second.
            response = self.model.generate_content([SYSTEM_PROMPT, final_prompt]) 
            
            print("\n" + "="*50)
            print("📈 YOUR DAILY AI DIGEST 📈")
            print("="*50)
            print(response.text)
            
            return response

if __name__ == "__main__":
    agent = DailyDigestAgent()
    agent.generate_digest()
