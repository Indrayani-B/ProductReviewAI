import streamlit as st
import requests
import sqlite3
import pandas as pd

API_URL = "http://127.0.0.1:8000"
DB_PATH = "data/reviews.db"

def get_top_products():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("""
        SELECT r.parent_asin, p.title, COUNT(*) as review_count
        FROM reviews_clean r
        LEFT JOIN products p ON r.parent_asin = p.parent_asin
        GROUP BY r.parent_asin
        ORDER BY review_count DESC
        LIMIT 20
    """, conn)
    conn.close()
    df["label"] = df["title"].str[:50] + " (" + df["review_count"].astype(str) + " reviews)"
    return df

def show():
    st.title("🤖 LLM Insights")
    st.markdown("---")

    products_df = get_top_products()
    product_options = dict(zip(products_df["label"], products_df["parent_asin"]))

    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Product Summary",
        "⚔️ Compare Products",
        "💡 Improvements",
        "📊 Executive Report"
    ])

    # tab 1 — product summary
    with tab1:
        st.subheader("Product Summary")
        selected = st.selectbox("Select product:", list(product_options.keys()), key="sum")
        asin = product_options[selected]

        if st.button("Generate Summary", key="btn_sum"):
            with st.spinner("Generating summary with Gemini..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/product_summary",
                        json={"parent_asin": asin}
                    ).json()
                    st.success("Summary generated!")
                    st.markdown(f"**Product:** {resp['product_name']}")
                    st.markdown(f"**Reviews analyzed:** {resp['review_count']}")
                    st.markdown("---")
                    st.write(resp["summary"])
                except Exception as e:
                    st.error(f"Error: {e}")

    # tab 2 — compare products
    with tab2:
        st.subheader("Compare Two Products")
        col1, col2 = st.columns(2)
        with col1:
            sel_a = st.selectbox("Product A:", list(product_options.keys()), key="cmp_a")
        with col2:
            sel_b = st.selectbox("Product B:", list(product_options.keys()),
                                  index=1, key="cmp_b")

        if st.button("Compare", key="btn_cmp"):
            if sel_a == sel_b:
                st.warning("Please select two different products.")
            else:
                with st.spinner("Comparing with Gemini..."):
                    try:
                        resp = requests.post(
                            f"{API_URL}/compare_products",
                            json={
                                "asin_a": product_options[sel_a],
                                "asin_b": product_options[sel_b]
                            }
                        ).json()
                        st.markdown(f"**A:** {resp['product_a']['name']}")
                        st.markdown(f"**B:** {resp['product_b']['name']}")
                        st.markdown("---")
                        st.write(resp["comparison"])
                    except Exception as e:
                        st.error(f"Error: {e}")

    # tab 3 — improvements
    with tab3:
        st.subheader("Product Improvement Recommendations")
        selected = st.selectbox("Select product:", list(product_options.keys()), key="rec")
        asin = product_options[selected]

        if st.button("Get Recommendations", key="btn_rec"):
            with st.spinner("Analyzing negative reviews with Gemini..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/executive_report",
                        json={"parent_asin": asin}
                    ).json()
                    st.markdown(f"**Product:** {resp['product_name']}")
                    st.markdown("---")
                    # call recommend directly
                    import sys
                    sys.path.insert(0, ".")
                    from src.llm.recommend import recommend_improvements
                    result = recommend_improvements(asin)
                    st.write(result["recommendations"])
                except Exception as e:
                    st.error(f"Error: {e}")

    # tab 4 — executive report
    with tab4:
        st.subheader("Executive Report")
        selected = st.selectbox("Select product:", list(product_options.keys()), key="rep")
        asin = product_options[selected]

        if st.button("Generate Report", key="btn_rep"):
            with st.spinner("Generating executive report..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/executive_report",
                        json={"parent_asin": asin}
                    ).json()

                    # stats
                    stats = resp["stats"]
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Reviews", stats["review_count"])
                    with col2:
                        st.metric("Avg Rating", stats["avg_rating"])
                    with col3:
                        st.metric("Positive", f"{stats['positive_pct']}%")

                    st.markdown("---")
                    st.write(resp["report"])
                    st.success(f"PDF saved to: {resp['pdf_path']}")
                except Exception as e:
                    st.error(f"Error: {e}")