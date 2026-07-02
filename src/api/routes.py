from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pickle
import sqlite3
import pandas as pd
from src.utils.config import DB_PATH, MODEL_DIR
from src.llm.summarise import summarise_product
from src.llm.compare import compare_products
from src.llm.recommend import recommend_improvements
from src.llm.report import generate_report, save_report_pdf
from src.utils.logger import log_prediction, get_model_health
from fastapi.responses import FileResponse

router = APIRouter()

# ── load models once at startup ─────────────────────────────────
with open(f"{MODEL_DIR}/sentiment_model.pkl", "rb") as f:
    sentiment_model = pickle.load(f)

with open(f"{MODEL_DIR}/tfidf_vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

with open(f"{MODEL_DIR}/fake_review_model.pkl", "rb") as f:
    fake_model = pickle.load(f)

# ── request/response schemas ─────────────────────────────────────
class ReviewInput(BaseModel):
    text: str
    rating: float = None
    verified_purchase: bool = True
    review_length: int = None
    title_length: int = 0
    helpful_vote: int = 0
    user_review_count: int = 1
    rating_deviation: float = 0.0

class ProductInput(BaseModel):
    parent_asin: str

class CompareInput(BaseModel):
    asin_a: str
    asin_b: str

# ── 1. predict sentiment ─────────────────────────────────────────
@router.post("/predict_sentiment")
def predict_sentiment(data: ReviewInput):
    try:
        vec = vectorizer.transform([data.text])
        pred = sentiment_model.predict(vec)[0]
        prob = sentiment_model.predict_proba(vec)[0]
        
        result = {
            "sentiment": "positive" if pred == 1 else "negative",
            "confidence": round(float(max(prob)), 4),
            "positive_prob": round(float(prob[1]), 4),
            "negative_prob": round(float(prob[0]), 4)
        }
        
        # log prediction for monitoring
        log_prediction("sentiment", data.text[:100], result["sentiment"], result["confidence"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── 2. predict fake review ────────────────────────────────────────
@router.post("/predict_fake_review")
def predict_fake_review(data: ReviewInput):
    try:
        review_length = data.review_length or len(data.text.split())
        
        features = pd.DataFrame([{
            "review_length":    review_length,
            "title_length":     data.title_length,
            "helpful_vote":     data.helpful_vote,
            "rating_deviation": data.rating_deviation,
            "user_review_count": data.user_review_count,
            "rating":           data.rating or 3.0
        }])
        
        pred = fake_model.predict(features)[0]
        prob = fake_model.predict_proba(features)[0]
        
        return {
            "is_fake": bool(pred),
            "fake_probability": round(float(prob[1]), 4),
            "genuine_probability": round(float(prob[0]), 4),
            "risk_level": "high" if prob[1] > 0.7 else "medium" if prob[1] > 0.4 else "low"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── 3. product summary ────────────────────────────────────────────
@router.post("/product_summary")
def product_summary(data: ProductInput):
    try:
        result = summarise_product(data.parent_asin)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── 4. compare products ───────────────────────────────────────────
@router.post("/compare_products")
def compare(data: CompareInput):
    try:
        result = compare_products(data.asin_a, data.asin_b)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── 5. executive report ───────────────────────────────────────────
@router.post("/executive_report")
def executive_report(data: ProductInput):
    try:
        result = generate_report(data.parent_asin)
        pdf_path = save_report_pdf(result)
        return {
            "product_name": result["product_name"],
            "stats": result["stats"],
            "report": result["report"],
            "pdf_path": pdf_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── 6. dashboard data ─────────────────────────────────────────────
@router.get("/dashboard_data")
def dashboard_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        
        total = pd.read_sql("SELECT COUNT(*) as count FROM reviews_clean", conn).iloc[0]["count"]
        avg_rating = pd.read_sql("SELECT ROUND(AVG(rating),2) as avg FROM reviews_clean", conn).iloc[0]["avg"]
        positive_pct = pd.read_sql("SELECT ROUND(AVG(sentiment)*100,1) as pct FROM reviews_clean", conn).iloc[0]["pct"]
        
        top_products = pd.read_sql("""
            SELECT r.parent_asin, p.title, COUNT(*) as review_count,
                   ROUND(AVG(r.rating),2) as avg_rating
            FROM reviews_clean r
            LEFT JOIN products p ON r.parent_asin = p.parent_asin
            GROUP BY r.parent_asin
            ORDER BY review_count DESC
            LIMIT 10
        """, conn)
        
        rating_dist = pd.read_sql("""
            SELECT rating, COUNT(*) as count 
            FROM reviews_clean 
            GROUP BY rating 
            ORDER BY rating
        """, conn)
        
        conn.close()
        
        health = get_model_health()
        
        return {
            "total_reviews": int(total),
            "avg_rating": float(avg_rating),
            "positive_pct": float(positive_pct),
            "top_products": top_products.to_dict(orient="records"),
            "rating_distribution": rating_dist.to_dict(orient="records"),
            "model_health": health
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))