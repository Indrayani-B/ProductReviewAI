import numpy as np
import pandas as pd
import sqlite3
import pickle
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from src.utils.config import DB_PATH, MODEL_DIR


# ── 1. Load clean data from SQLite ────────────────────────────────────────
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM reviews_clean", conn)
    conn.close()
    print(f"Loaded: {len(df):,} rows")
    return df

# ── 2. TF-IDF features (for sentiment model) ─────────────────────────────────────────────
def build_tfidf(df, max_features=5000):
    
    print("Building TF-IDF matrix...")
    
    vectorizer = TfidfVectorizer(     #Imagine you're making a dictionary of important words.
        max_features=max_features,    # keep top 5000 words/bigrams
        ngram_range=(1, 2),          # unigrams + bigrams
        min_df=5,                    # ignore words appearing in <5 reviews
        max_df=0.95,                 # ignore words in >95% of reviews (too common)
        strip_accents="unicode",     # handle special characters
        stop_words="english"         # remove "the", "is", "a" etc
        )
    
    tfidf_matrix = vectorizer.fit_transform(df["text"])
    print(f"TF-IDF shape: {tfidf_matrix.shape}")
    # shape = (86738 reviews, 5000 features)
    # each review is now a row of 5000 numbers
    
    return tfidf_matrix, vectorizer

# ── 3. Tabular features (for fake review model) ───────────────────────────
def build_tabular_features(df):
    """
    These are hand-crafted features based on our EDA findings.
    Each feature captures a fake review signal we discovered.
    """
    features = pd.DataFrame()
    
    # feature 1 — review length
    # EDA finding: fake reviews tend to be very short or unusually long
    features["review_length"] = df["review_length"]
    
    # feature 2 — verified purchase
    # EDA finding: unverified reviews more likely to be fake
    features["verified_purchase"] = df["verified_purchase"].astype(int)
    
    # feature 3 — rating deviation from product average
    # fake reviews tend to be extreme (1 or 5 stars)
    # a product with avg rating 3.8 getting a 5.0 review is suspicious
    product_avg = df.groupby("parent_asin")["rating"].transform("mean")
    features["rating_deviation"] = abs(df["rating"] - product_avg)
    
    # feature 4 — user review count
    # EDA finding: bot accounts post many reviews
    # a user who reviewed 50 products is more suspicious than one who reviewed 2
    user_counts = df.groupby("user_id")["rating"].transform("count")
    features["user_review_count"] = user_counts
    
    # feature 5 — title length
    # fake reviews often have very short or missing titles
    features["title_length"] = df["title_length"]
    
    # feature 6 — helpful votes
    # real reviews tend to get more helpful votes over time
    features["helpful_vote"] = df["helpful_vote"]
    
    print("Tabular features shape:", features.shape)
    print("Features created:", features.columns.tolist())
    print("\nSample:")
    print(features.head(3))
    
    return features

# ── 4. Save vectorizer for later use in API ────────────────────────────────
def save_vectorizer(vectorizer):
    path = Path(MODEL_DIR) / "tfidf_vectorizer.pkl"
    Path(MODEL_DIR).mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(vectorizer, f)
    print(f"Saved vectorizer → {path}")

# ── 5. Save features to SQLite ────────────────────────────────────────────
def save_tabular_features(df, features):
    # combine with original columns needed for training
    features["sentiment"]   = df["sentiment"].values
    features["parent_asin"] = df["parent_asin"].values
    features["user_id"]     = df["user_id"].values
    features["rating"]      = df["rating"].values

    conn = sqlite3.connect(DB_PATH)
    features.to_sql("features", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Saved features table → {len(features):,} rows")

# ── 6. Run ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # load
    df = load_data()
    
    # build tfidf
    tfidf_matrix, vectorizer = build_tfidf(df)
    
    # build tabular features
    features = build_tabular_features(df)
    
    # save
    save_vectorizer(vectorizer)
    save_tabular_features(df, features)
    
    print("\nFeature engineering complete.")
    print(f"TF-IDF matrix:   {tfidf_matrix.shape}")
    print(f"Tabular features: {features.shape}")
