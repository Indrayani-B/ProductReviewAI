import streamlit as st
import pandas as pd
import sqlite3
from PIL import Image
import os

DB_PATH = "data/reviews.db"

def show():
    st.title("🔍 Fake Review Detection")
    st.markdown("---")

    # methodology
    st.subheader("📋 Detection Methodology")
    st.info("""
    **Weak supervision approach** — no ground-truth labels existed.
    Labels created from 2 behavioral signals:
    - Same user posting identical text across multiple products (bot behavior)
    - Unverified purchase + very short review (<10 words)

    **Model:** XGBoost | **ROC-AUC:** 0.939 | **Fake rate detected:** 0.63%
    """)

    # SHAP feature importance
    st.subheader("🔬 SHAP Feature Importance")
    shap_path = "models/shap_fake_review.png"
    if os.path.exists(shap_path):
        img = Image.open(shap_path)
        st.image(img, caption="Feature importance — XGBoost Fake Review Detector")
    else:
        st.warning("SHAP plot not found. Run 03_Fake_Review.ipynb first.")

    st.markdown("""
    **Key findings from SHAP:**
    - `review_length` is the dominant predictor — fake reviews are very short
    - `user_review_count` is second — bot accounts post many reviews
    - `rating_deviation` — fake reviews tend to be extreme (1★ or 5★)
    """)

    # flagged reviews sample
    st.markdown("---")
    st.subheader("🚨 Sample Flagged Reviews")

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("""
        SELECT r.text, r.rating, r.verified_purchase,
               r.review_length, r.user_id
        FROM reviews_clean r
        WHERE r.review_length < 5 
          AND r.verified_purchase = 0
          AND r.rating = 5.0
        LIMIT 20
    """, conn)
    conn.close()

    df["risk"] = "🔴 High"
    df["reason"] = "Unverified + very short + 5★"
    st.dataframe(df[["text", "rating", "verified_purchase",
                      "review_length", "risk", "reason"]],
                 use_container_width=True)

    # live fake check
    st.markdown("---")
    st.subheader("🎯 Check a Review")

    col1, col2 = st.columns(2)
    with col1:
        check_text = st.text_area("Review text:", "Good product!")
        rating = st.slider("Rating", 1.0, 5.0, 5.0, 0.5)
    with col2:
        verified = st.checkbox("Verified Purchase", value=False)
        user_count = st.number_input("User's total reviews", 1, 500, 50)

    if st.button("Check for Fake"):
        import requests
        try:
            resp = requests.post(
                "http://127.0.0.1:8000/predict_fake_review",
                json={
                    "text": check_text,
                    "rating": rating,
                    "verified_purchase": verified,
                    "review_length": len(check_text.split()),
                    "user_review_count": user_count
                }
            ).json()

            risk_color = {"high": "red", "medium": "orange", "low": "green"}
            color = risk_color[resp["risk_level"]]
            st.markdown(f"### :{color}[Risk: {resp['risk_level'].upper()}]")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Fake Probability", f"{resp['fake_probability']*100:.1f}%")
            with col2:
                st.metric("Genuine Probability", f"{resp['genuine_probability']*100:.1f}%")
        except:
            st.error("API not running.")