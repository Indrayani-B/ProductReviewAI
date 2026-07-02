import sqlite3
import pandas as pd
from src.llm.client import call_llm
from src.llm.prompts import RECOMMEND_COT
from src.utils.config import DB_PATH
from src.llm.summarise import get_product_name

def get_negative_reviews(parent_asin, limit=20):
    """Focus on negative reviews for improvement recommendations."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("""
        SELECT text, rating 
        FROM reviews_clean 
        WHERE parent_asin = ? AND sentiment = 0
        ORDER BY helpful_vote DESC
        LIMIT ?
    """, conn, params=(parent_asin, limit))
    conn.close()
    return df

def recommend_improvements(parent_asin):
    """
    Generate top 5 product improvements from negative reviews.
    Uses CoT prompting — best for detailed analysis tasks.
    """
    df = get_negative_reviews(parent_asin)
    product_name = get_product_name(parent_asin)
    
    if len(df) == 0:
        return "No negative reviews found — product has excellent reception!"
    
    reviews_text = "\n".join([
        f"- ({row['rating']}★) {row['text'][:200]}"
        for _, row in df.iterrows()
    ])
    
    prompt = RECOMMEND_COT.format(reviews=reviews_text)
    recommendations = call_llm(prompt, max_tokens=1200)
    
    return {
        "parent_asin": parent_asin,
        "product_name": product_name,
        "negative_review_count": len(df),
        "recommendations": recommendations
    }

if __name__ == "__main__":
    result = recommend_improvements("B075X8471B")
    print(f"Product: {result['product_name']}")
    print(f"Based on {result['negative_review_count']} negative reviews")
    print(f"\nRecommendations:\n{result['recommendations']}")