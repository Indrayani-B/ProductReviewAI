import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.figure_factory as ff

DB_PATH = "data/reviews.db"

def show():
    st.title("📊 Exploratory Data Analysis")
    st.markdown("---")

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM reviews_clean", conn)
    conn.close()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["month"] = df["timestamp"].dt.to_period("M").astype(str)

    # rating distribution
    st.subheader("⭐ Rating Distribution")
    fig = px.histogram(df, x="rating", color_discrete_sequence=["#2196F3"],
                       nbins=5, title="Rating Distribution")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    # sentiment split
    with col1:
        st.subheader("💬 Sentiment Split")
        sentiment_counts = df["sentiment"].value_counts().reset_index()
        sentiment_counts.columns = ["sentiment", "count"]
        sentiment_counts["label"] = sentiment_counts["sentiment"].map(
            {1: "Positive", 0: "Negative"}
        )
        fig = px.pie(sentiment_counts, values="count", names="label",
                     color_discrete_sequence=["#4CAF50", "#F44336"])
        st.plotly_chart(fig, use_container_width=True)

    # verified purchase
    with col2:
        st.subheader("✅ Verified Purchase")
        vp_counts = df["verified_purchase"].value_counts().reset_index()
        vp_counts.columns = ["verified", "count"]
        vp_counts["label"] = vp_counts["verified"].map(
            {1: "Verified", 0: "Not Verified"}
        )
        fig = px.pie(vp_counts, values="count", names="label",
                     color_discrete_sequence=["#2196F3", "#FF9800"])
        st.plotly_chart(fig, use_container_width=True)

    # review length distribution
    st.subheader("📝 Review Length Distribution")
    fig = px.histogram(df, x="review_length", nbins=50,
                       range_x=[0, 300],
                       color_discrete_sequence=["#9C27B0"],
                       title="Review Length (words) — clipped at 300")
    st.plotly_chart(fig, use_container_width=True)

    # monthly trend
    st.subheader("📅 Reviews Over Time")
    monthly = df.groupby("month").size().reset_index(name="count")
    monthly = monthly[monthly["month"] != "NaT"]
    fig = px.line(monthly, x="month", y="count",
                  title="Monthly Review Volume",
                  color_discrete_sequence=["#2196F3"])
    fig.add_annotation(
        x="2023-03", y=monthly[monthly["month"]=="2023-03"]["count"].values[0]
        if "2023-03" in monthly["month"].values else 0,
        text="Incomplete month",
        showarrow=True, arrowhead=1
    )
    st.plotly_chart(fig, use_container_width=True)

    # correlation matrix
    st.subheader("🔗 Correlation Matrix")
    corr_cols = ["rating", "review_length", "helpful_vote",
                 "verified_purchase", "sentiment"]
    corr_df = df[corr_cols].corr().round(2)

    fig = px.imshow(corr_df, text_auto=True, color_continuous_scale="RdBu",
                    title="Pearson Correlation Matrix", zmin=-1, zmax=1)
    st.plotly_chart(fig, use_container_width=True)

    st.info("""
    **Key finding:** `review_length ↔ verified_purchase = -0.33`
    Unverified reviewers write longer reviews — likely attempting to appear legitimate.
    This is used as a feature in the fake review detection model.
    """)