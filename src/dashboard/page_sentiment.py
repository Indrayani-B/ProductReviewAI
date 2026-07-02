import streamlit as st
import pandas as pd
import pickle
import plotly.express as px
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import sqlite3

DB_PATH = "data/reviews.db"
MODEL_DIR = "models"

def show():
    st.title("💬 Sentiment Analysis")
    st.markdown("---")

    # model comparison table
    st.subheader("🏆 Model Comparison")

    results = pd.DataFrame({
        "Model": ["Logistic Regression", "Random Forest", "XGBoost"],
        "Accuracy": [0.8975, 0.9172, 0.9011],
        "Precision": [0.9765, 0.9250, 0.9002],
        "Recall": [0.9027, 0.9835, 0.9956],
        "F1": [0.9382, 0.9534, 0.9455],
        "ROC-AUC": [0.9510, 0.9329, 0.9324],
        "Selected": ["✓", "", ""]
    })
    st.dataframe(results, use_container_width=True)

    st.info("""
    **Why Logistic Regression was selected despite lower F1:**
    Logistic Regression has the lowest False Positives (324 vs 1,191 for Random Forest).
    In a retail context, missing real negative reviews (False Positives) is more costly
    than investigating false alarms. Business context drives model selection, not just metrics.
    """)

    col1, col2 = st.columns(2)

    # confusion matrix
    with col1:
        st.subheader("Confusion Matrix — Logistic Regression")
        cm_data = [[2079, 324], [1454, 13491]]
        fig, ax = plt.subplots(figsize=(5, 4))
        im = ax.imshow(cm_data, cmap="Blues")
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["Negative", "Positive"])
        ax.set_yticklabels(["Negative", "Positive"])
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        for i in range(2):
            for j in range(2):
                ax.text(j, i, cm_data[i][j],
                        ha="center", va="center", color="black", fontsize=14)
        plt.tight_layout()
        st.pyplot(fig)

    # ROC chart
    with col2:
        st.subheader("ROC-AUC Comparison")
        roc_df = pd.DataFrame({
            "Model": ["Logistic Regression", "Random Forest", "XGBoost"],
            "ROC-AUC": [0.9510, 0.9329, 0.9324]
        })
        fig = px.bar(roc_df, x="Model", y="ROC-AUC",
                     color_discrete_sequence=["#2196F3"],
                     range_y=[0.9, 0.96])
        st.plotly_chart(fig, use_container_width=True)

    # live prediction
    st.markdown("---")
    st.subheader("🎯 Try It Live")
    user_text = st.text_area("Enter a review:", "This product is absolutely amazing!")

    if st.button("Predict Sentiment"):
        import requests
        try:
            resp = requests.post(
                "http://127.0.0.1:8000/predict_sentiment",
                json={"text": user_text}
            ).json()

            col1, col2 = st.columns(2)
            with col1:
                color = "green" if resp["sentiment"] == "positive" else "red"
                st.markdown(f"### :{color}[{resp['sentiment'].upper()}]")
            with col2:
                st.metric("Confidence", f"{resp['confidence']*100:.1f}%")

            st.progress(resp["positive_prob"])
            st.caption(f"Positive: {resp['positive_prob']*100:.1f}%  |  "
                      f"Negative: {resp['negative_prob']*100:.1f}%")
        except:
            st.error("API not running. Start with: uvicorn src.api.main:app --port 8000")