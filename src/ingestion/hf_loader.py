import os
import sys

# Ensure our src module is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from datasets import load_dataset
from src.config import Config

def stream_news_from_hf(subsets=None, limit=1000):
    """
    Generator function that streams news articles from the HuggingFace dataset.
    
    Args:
        subsets (list): List of dataset subsets to load. Defaults to Config.DEFAULT_SUBSETS.
        limit (int): Maximum number of articles to yield per subset.
        
    Yields:
        dict: A dictionary representing a single news article.
    """
    # 1. Fallback if subsets is None
    # TODO: Set `subsets` to `Config.DEFAULT_SUBSETS` if it wasn't provided
    if subsets is None:
        subsets = Config.DEFAULT_SUBSETS
    
    # 2. Iterate over the subsets
    for subset in subsets:
        print(f"Streaming from subset: {subset}...")
        
        # Path logic specific to this dataset's structure
        data_files = f"data/{subset}/*.parquet"

        dataset = load_dataset(path=Config.HF_DATASET_PATH, data_files=data_files, split="train", streaming=True)
        
        # 3. Load the dataset
        # TODO: Call `load_dataset` using the datasets library. 
        # You need to pass:
        #   - path: Config.HF_DATASET_PATH
        #   - data_files: the data_files variable above
        #   - split: "train"
        #   - streaming: True (This prevents downloading the 20GB dataset onto your hard drive at once!) 
        
        count = 0
        
        # 4. Yield the rows one by one
        # TODO: Create a for-loop iterating over `dataset`.
        #   - yield the row
        #   - increment `counts`
        #   - implement an if statement to `break` out of the loop if `counts == limit`
        for data in dataset :
            yield data
            count +=1 
            if count == limit :
                break


# This block allows you to test your function standalone!
if __name__ == "__main__":
    print("Testing HuggingFace Streamer...")
    
    # Let's test with just 3 articles
    news_stream = stream_news_from_hf(limit=3)
    
    for idx, article in enumerate(news_stream):
        print(f"\n--- Article {idx + 1} ---")
        print("Date:", article.get("date"))
        print("Text Preview:", article.get("text")[:100], "...")
