# python -m spacy download en_core_web_sm

import pandas as pd
import sqlite3
import pickle
import spacy
from collections import Counter
from src.utils.config import DB_PATH, MODEL_DIR

# ── 1. Load spaCy model ────────────────────────────────────────────────────
nlp = spacy.load("en_core_web_sm")

# ── 2. Load saved sentiment model + vectorizer ─────────────────────────────
def load_sentiment_model():
    with open(f"{MODEL_DIR}/sentiment_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open(f"{MODEL_DIR}/tfidf_vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    return model, vectorizer

# ── 3. Extract candidate aspect nouns from a review ────────────────────────
def extract_aspects(text, nlp_model):
    """
    Find noun chunks in the text that could be product aspects.
    Example: "the battery life", "this camera quality" → battery, camera
    """
    doc = nlp_model(text)
    aspects = []
    
    for chunk in doc.noun_chunks:
        # take the root noun of the phrase, lowercase, strip
        word = chunk.root.text.lower().strip()
        # filter out junk — pronouns, very short words, stopwords
        if len(word) > 2 and chunk.root.pos_ == "NOUN":
            aspects.append(word)
    
    return aspects

# ── 4. Get sentence containing a specific aspect word ──────────────────────
def get_aspect_sentence(text, aspect, nlp_model):
    """
    Find the sentence that mentions this aspect — 
    so we can score sentiment for JUST that part, not the whole review.
    """
    doc = nlp_model(text)
    for sent in doc.sents:
        if aspect in sent.text.lower():
            return sent.text
    return text  # fallback to full text if not found

# ── 5. Predict sentiment for a piece of text ───────────────────────────────
def predict_sentiment(text, model, vectorizer):
    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]
    return "positive" if pred == 1 else "negative"

# ── 6. Process all reviews and build aspect-sentiment table ───────────────
def process_reviews(df, model, vectorizer, nlp_model, top_n_aspects=15):
    print("Finding most common aspects across all reviews...")
    
    # first pass — find globally common aspects (battery, camera, screen etc)
    all_aspects = []
    sample = df["text"].sample(min(5000, len(df)), random_state=42)
    for text in sample:
        all_aspects.extend(extract_aspects(text, nlp_model))
    
    common_aspects = [w for w, c in Counter(all_aspects).most_common(top_n_aspects)]
    print(f"Top {top_n_aspects} aspects found: {common_aspects}")
    
    # second pass — for each review, check which common aspects it mentions
    # and score sentiment for that specific aspect
    results = []
    
    for idx, row in df.iterrows():
        text = row["text"]
        review_aspects = set(extract_aspects(text, nlp_model))
        matched = review_aspects.intersection(common_aspects)
        
        for aspect in matched:
            sentence = get_aspect_sentence(text, aspect, nlp_model)
            sentiment = predict_sentiment(sentence, model, vectorizer)
            
            results.append({
                "parent_asin": row["parent_asin"],
                "user_id": row["user_id"],
                "aspect": aspect,
                "sentiment": sentiment,
                "sentence": sentence[:200]  # truncate for storage
            })
        
        if idx % 5000 == 0:
            print(f"Processed {idx:,} reviews...")
    
    return pd.DataFrame(results)

# ── 7. Save to SQLite ───────────────────────────────────────────────────────
def save_aspects(df_aspects):
    conn = sqlite3.connect(DB_PATH)
    df_aspects.to_sql("aspects", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Saved aspects table → {len(df_aspects):,} rows")

# ── 8. Run ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT parent_asin, user_id, text FROM reviews_clean", conn)
    conn.close()
    print(f"Loaded: {len(df):,} reviews (sample for speed)")
    
    model, vectorizer = load_sentiment_model()
    
    df_aspects = process_reviews(df, model, vectorizer, nlp)
    
    print(f"\nTotal aspect mentions found: {len(df_aspects):,}")
    print("\nAspect sentiment summary:")
    print(df_aspects.groupby(["aspect", "sentiment"]).size().unstack(fill_value=0))
    
    save_aspects(df_aspects)