import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import google.generativeai as genai
from src.config import Config
from src.ingestion.database import NewsDatabase

# Prompt engineering tailored strictly for RAG
RAG_SYSTEM_PROMPT = """You are a helpful and expert financial AI assistant.
Use ONLY the context provided below to answer the user's question. 
If the answer is not contained in the context, politely say "I don't have enough information in today's news to answer that." 
Do NOT make up information or use outside knowledge.

CONTEXT ARTICLES:
{context}
"""

class RAGChatbot:
    def __init__(self):
        self.db = NewsDatabase()
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        # We'll use the working 2.5-flash model you fixed!
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def ask(self, user_query):
        # 1. Retrieve the mathematical closest articles to the user's question
        # TODO: Call `self.db.collection.query(...)` 
        # Pass exactly two arguments: `query_texts=[user_query]` and `n_results=5`
        search_results = self.db.collection.query(query_texts=[user_query], n_results=5)     
        
        if not search_results or not search_results['documents'][0]:
            return "No relevant articles found in the database."

        # 2. Format the retrieved context
        # search_results['documents'][0] contains a list of the 5 closest text matches
        retrieved_texts = search_results['documents'][0]
        
        # We stitch them together with a line break so the AI can read them as one big document
        context_block = "\n---\n".join(retrieved_texts)
        
        # 3. Build the prompt
        # TODO: Inject our `context_block` into the RAG_SYSTEM_PROMPT
        # Hint: RAG_SYSTEM_PROMPT.format(context=...)
        system_instruction = RAG_SYSTEM_PROMPT.format(context=context_block)
        
        # 4. Generate the response
        # TODO: Call `self.model.generate_content(...)`
        # Pass it a list exactly like last time: `[system_instruction, user_query]`
        response = self.model.generate_content([system_instruction, user_query])
        
        return response.text

if __name__ == "__main__":
    bot = RAGChatbot()
    print("Welcome to the Financial News Chatbot! (Type 'quit' to exit)")
    
    # Simple interactive loop for the terminal
    while True:
        question = input("\nUser: ")
        if question.lower().strip() in ['quit', 'exit']:
            break
            
        print("Bot is thinking...")
        answer = bot.ask(question)
        print(f"\nBot:\n {answer}")
