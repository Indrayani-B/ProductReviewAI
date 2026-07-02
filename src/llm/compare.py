import sqlite3
import pandas as pd
from src.llm.client import call_llm
from src.llm.prompts import COMPARE_FEW_SHOT
from src.utils.config import DB_PATH
from src.llm.summarise import get_product_name

def get_reviews_text(parent_asin, limit=15):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("""
        SELECT text, rating 
        FROM reviews_clean 
        WHERE parent_asin = ? 
        LIMIT ?
    """, conn, params=(parent_asin, limit))
    conn.close()
    return "\n".join([
        f"- ({row['rating']}★) {row['text'][:150]}"
        for _, row in df.iterrows()
    ])

def compare_products(asin_a, asin_b):
    """
    Compare two products using customer reviews.
    Uses few-shot prompting strategy.
    """
    name_a = get_product_name(asin_a)
    name_b = get_product_name(asin_b)
    
    reviews_a = get_reviews_text(asin_a)
    reviews_b = get_reviews_text(asin_b)
    
    if not reviews_a or not reviews_b:
        return "Insufficient reviews for one or both products."
    
    prompt = COMPARE_FEW_SHOT.format(
        reviews_a=reviews_a,
        reviews_b=reviews_b
    )
    
    comparison = call_llm(prompt, max_tokens=1000)
    
    return {
        "product_a": {"asin": asin_a, "name": name_a},
        "product_b": {"asin": asin_b, "name": name_b},
        "comparison": comparison
    }

if __name__ == "__main__":
    result = compare_products("B075X8471B", "B01K8B8YA8")
    print(f"Comparing:")
    print(f"  A: {result['product_a']['name']}")
    print(f"  B: {result['product_b']['name']}")
    print(f"\nComparison:\n{result['comparison']}")