import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import streamlit as st

st.set_page_config(
    page_title="Product Review AI",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# sidebar navigation
st.sidebar.title("🛒 Product Review AI")
st.sidebar.markdown("---")

pages = {
    "🏠 Home":              "home",
    "📊 EDA":               "eda",
    "💬 Sentiment":         "sentiment",
    "🔍 Fake Reviews":      "fake",
    "🤖 LLM Insights":      "llm",
    "🧪 Prompt Playground": "prompts",
}

selection = st.sidebar.radio("Navigate", list(pages.keys()))
page = pages[selection]

st.sidebar.markdown("---")
st.sidebar.caption("Built for Amazon RBS Interview")
st.sidebar.caption("Model: Logistic Regression + Gemini 2.5")

# load selected page
if page == "home":
    from src.dashboard.page_home import show
    show()
elif page == "eda":
    from src.dashboard.page_eda import show
    show()
elif page == "sentiment":
    from src.dashboard.page_sentiment import show
    show()
elif page == "fake":
    from src.dashboard.page_fake import show
    show()
elif page == "llm":
    from src.dashboard.page_llm import show
    show()
elif page == "prompts":
    from src.dashboard.page_prompts import show
    show()