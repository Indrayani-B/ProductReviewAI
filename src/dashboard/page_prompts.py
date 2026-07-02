import streamlit as st
import pandas as pd
import sqlite3
from src.llm.client import call_llm
from src.llm import prompts

DB_PATH = "data/reviews.db"

def show():
    st.title("🧪 Prompt Playground")
    st.markdown("Compare zero-shot, few-shot, and chain-of-thought prompting strategies.")
    st.markdown("---")

    # load saved experiment results
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT * FROM prompt_experiments", conn)
        conn.close()

        st.subheader("📊 Saved Experiment Results")
        st.dataframe(df[["task", "strategy", "output_length", "output"]],
                     use_container_width=True)
    except:
        st.warning("No saved experiments found. Run 04_LLM_Experiments.ipynb first.")

    st.markdown("---")

    # live prompt comparison
    st.subheader("🔴 Live Comparison")
    st.warning("Each test uses 3 API calls. Wait between runs to avoid rate limits.")

    custom_text = st.text_area(
        "Enter review text to summarize:",
        "Battery life is amazing but the camera quality is disappointing in low light."
    )

    strategy = st.radio(
        "Select strategy to test:",
        ["Zero-shot", "Few-shot", "Chain-of-Thought"],
        horizontal=True
    )

    if st.button("Run Prompt"):
        with st.spinner("Calling Gemini..."):
            try:
                if strategy == "Zero-shot":
                    prompt = prompts.SUMMARY_ZERO_SHOT.format(reviews=custom_text)
                elif strategy == "Few-shot":
                    prompt = prompts.SUMMARY_FEW_SHOT.format(reviews=custom_text)
                else:
                    prompt = prompts.SUMMARY_COT.format(reviews=custom_text)

                result = call_llm(prompt)

                st.markdown(f"**Strategy:** {strategy}")
                st.markdown(f"**Output length:** {len(result)} chars")
                st.markdown("---")
                st.write(result)
            except Exception as e:
                st.error(f"Error: {e}")

    # strategy explanation
    st.markdown("---")
    st.subheader("📚 Strategy Guide")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Zero-shot**")
        st.markdown("No examples given. Just the instruction and input. Fastest and cheapest.")

    with col2:
        st.markdown("**Few-shot**")
        st.markdown("2-3 examples shown. Model mimics the style. More consistent output.")

    with col3:
        st.markdown("**Chain-of-Thought**")
        st.markdown("Step by step reasoning. Most thorough. Best for complex analysis.")