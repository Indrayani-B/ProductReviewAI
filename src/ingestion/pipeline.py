import json
import pandas as pd
import sqlite3
from pathlib import Path

INPUT  = Path("data/raw/Electronics.jsonl")
OUTPUT = Path("data/cleaned_reviews.csv")
DB     = Path("data/reviews.db")
SAMPLE = 100000   # change this number
META_INPUT = Path("data/raw/meta_Electronics.jsonl")
META_DB    = "products"


# ── 1. Load JSONL ──────────────────────────────────────────────────────────
def load_jsonl(path, n=None):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if n and i >= n:
                break
            records.append(json.loads(line))
    return pd.DataFrame(records)

    
def load_meta(path, n=None):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if n and i >= n:
                break
            try:
                row = json.loads(line)
                records.append({
                    "parent_asin":   row.get("parent_asin"),
                    "title":         row.get("title"),
                    "main_category": row.get("main_category"),
                    "price":         row.get("price"),
                    "average_rating": row.get("average_rating"),
                    "rating_number": row.get("rating_number"),
                })
            except:
                continue  # skip malformed lines
    return pd.DataFrame(records)

# ── 2. Save to CSV + SQLite ────────────────────────────────────────────────
def save(df):
    # drop images — list of dicts, SQLite can't store it, we don't need it
    df = df.drop(columns=["images"], errors="ignore")

    # CSV
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    print(f"Saved CSV → {OUTPUT}  ({len(df):,} rows)")

    # SQLite
    conn = sqlite3.connect(DB)
    df.to_sql("reviews", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Saved DB  → {DB}")
    

def save_meta(df_meta, df_reviews):
    # drop rows with no parent_asin
    df_meta = df_meta.dropna(subset=["parent_asin"])
    df_meta = df_meta.drop_duplicates(subset=["parent_asin"])
    
    # keep only products that appear in our reviews
    review_asins = set(df_reviews["parent_asin"].unique())
    df_meta = df_meta[df_meta["parent_asin"].isin(review_asins)]
    
    df_meta = df_meta.reset_index(drop=True)
    
    conn = sqlite3.connect(DB)
    df_meta.to_sql("products", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Saved products table → {len(df_meta):,} rows")

# ── 3. Run ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # reviews
    # print("Loading...")
    # df = load_jsonl(INPUT, n=SAMPLE)
    # print(f"Rows loaded: {len(df):,}")
    # print(f"Columns: {df.columns.tolist()}")
    # save(df)
    
    # load reviews from existing SQLite (already done)
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT parent_asin FROM reviews", conn)
    conn.close()
    print(f"Reviews loaded from DB: {len(df):,} rows")

    # meta
    print("\nLoading product metadata...")
    df_meta = load_meta(META_INPUT)
    print(f"Meta rows loaded: {len(df_meta):,}")
    save_meta(df_meta, df)