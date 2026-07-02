import sqlite3
import pandas as pd
from src.llm.client import call_llm
from src.llm.prompts import SUMMARY_FEW_SHOT
from src.utils.config import DB_PATH

def get_product_reviews(parent_asin, limit=20):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("""
        SELECT text, rating 
        FROM reviews_clean 
        WHERE parent_asin = ? 
        LIMIT ?
    """, conn, params=(parent_asin, limit))
    conn.close()
    return df

def get_product_name(parent_asin):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("""
        SELECT title FROM products 
        WHERE parent_asin = ?
        LIMIT 1
    """, conn, params=(parent_asin,))
    conn.close()
    if len(df) > 0 and df["title"].iloc[0]:
        return df["title"].iloc[0]
    return parent_asin  # fallback to ASIN if no title

def summarise_product(parent_asin):
    """
    Given a parent_asin, fetch reviews and return an LLM-generated summary.
    Uses few-shot prompting — best strategy from our prompt experiments.
    """
    df = get_product_reviews(parent_asin)
    
    if len(df) == 0:
        return "No reviews found for this product."
    
    product_name = get_product_name(parent_asin)
    
    reviews_text = "\n".join([
        f"- ({row['rating']}★) {row['text'][:200]}"
        for _, row in df.iterrows()
    ])
    
    prompt = SUMMARY_FEW_SHOT.format(reviews=reviews_text)
    summary = call_llm(prompt)
    
    return {
        "parent_asin": parent_asin,
        "product_name": product_name,
        "review_count": len(df),
        "summary": summary
    }

if __name__ == "__main__":
    result = summarise_product("B075X8471B")
    print(f"Product: {result['product_name']}")
    print(f"Reviews: {result['review_count']}")
    print(f"\nSummary:\n{result['summary']}")