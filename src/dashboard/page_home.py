import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

def show():
    st.title("🏠 Product Review AI — Dashboard")
    st.markdown("AI-powered customer review intelligence platform for e-commerce.")
    st.markdown("---")

    # fetch dashboard data from API
    try:
        data = requests.get(f"{API_URL}/dashboard_data").json()
    except Exception as e:
        st.error(f"API not running. Start it with: uvicorn src.api.main:app --port 8000")
        return

    # KPI cards row 1
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Reviews", f"{data['total_reviews']:,}")

    with col2:
        st.metric("Average Rating", f"{data['avg_rating']} ⭐")

    with col3:
        st.metric("Positive Sentiment", f"{data['positive_pct']}%")

    with col4:
        health = data["model_health"]
        st.metric("Model Status", health["status"].upper())

    st.markdown("---")

    # model health card
    st.subheader("🔋 Model Health")
    health = data["model_health"]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Predictions", health.get("total_predictions", 0))
    with col2:
        st.metric("Positive Predictions", health.get("sentiment_positive", 0))
    with col3:
        st.metric("Negative Predictions", health.get("sentiment_negative", 0))

    st.markdown("---")

    # top products table
    st.subheader("🏆 Top 10 Most Reviewed Products")
    top_products = pd.DataFrame(data["top_products"])
    if "title" in top_products.columns:
        top_products["title"] = top_products["title"].str[:60]
    st.dataframe(top_products, use_container_width=True)

    # rating distribution
    st.markdown("---")
    st.subheader("⭐ Rating Distribution")
    rating_df = pd.DataFrame(data["rating_distribution"])
    st.bar_chart(rating_df.set_index("rating")["count"])