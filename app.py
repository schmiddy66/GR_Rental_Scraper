import os
import pandas as pd
import streamlit as st
import psycopg2

st.set_page_config(page_title="GR Rentals Dashboard", layout="wide")

DB_URL = os.getenv("DATABASE_URL") or st.secrets.get("DATABASE_URL")
APP_PASSWORD = os.getenv("APP_PASSWORD") or st.secrets.get("APP_PASSWORD", "")

# Optional password
if APP_PASSWORD:
    pw = st.text_input("Enter password", type="password")
    if pw != APP_PASSWORD:
        st.stop()

def get_conn():
    if not DB_URL:
        st.error("DATABASE_URL not set. Add it in Streamlit secrets or env vars.")
        st.stop()
    return psycopg2.connect(DB_URL)

@st.cache_data(ttl=300)
def load_df():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM listings", conn)
    conn.close()
    return df

def main():
    st.title("GR Rentals Dashboard (Supabase)")

    df = load_df()
    if df.empty:
        st.info("No data yet. Wait for the GitHub Action to run or add rows via import script.")
        return

    with st.sidebar:
        st.header("Filters")
        srcs = sorted([s for s in df["source"].dropna().unique()])
        src = st.multiselect("Sources", srcs, default=srcs)
        beds_min, beds_max = st.slider("Bedrooms", 0.0, float(df["bedrooms"].max() if df["bedrooms"].notna().any() else 5.0), (0.0, float(df["bedrooms"].max() if df["bedrooms"].notna().any() else 5.0)))
        price_min, price_max = st.slider("Price", 0, int(df["price"].max() if df["price"].notna().any() else 5000), (0, int(df["price"].max() if df["price"].notna().any() else 5000)))
        ac = st.selectbox("Central Air", ["Any", "Yes", "No"])
        prk = st.selectbox("Off-street Parking", ["Any", "Yes", "No"])

    q = df.copy()
    if src:
        q = q[q["source"].isin(src)]
    if q["bedrooms"].notna().any():
        q = q[(q["bedrooms"].fillna(0) >= beds_min) & (q["bedrooms"].fillna(0) <= beds_max)]
    if q["price"].notna().any():
        q = q[(q["price"].fillna(0) >= price_min) & (q["price"].fillna(0) <= price_max)]
    if ac != "Any":
        q = q[q["has_central_air"].fillna(0) == (1 if ac == "Yes" else 0)]
    if prk != "Any":
        q = q[q["has_offstreet_prk"].fillna(0) == (1 if prk == "Yes" else 0)]

    st.subheader("Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Listings", len(q))
    with col2:
        st.metric("Median Price", int(q["price"].median()) if q["price"].notna().any() else 0)
    with col3:
        st.metric("Avg Beds", round(q["bedrooms"].mean(),2) if q["bedrooms"].notna().any() else 0)
    with col4:
        st.metric("With Central Air", int(q["has_central_air"].sum()) if "has_central_air" in q.columns else 0)

    st.subheader("Listings")
    show_cols = ["source","price","bedrooms","bathrooms","sqft","has_central_air","has_offstreet_prk","has_garage","has_dishwasher","pets_allowed","neighborhood","city","title","url","posted_at"]
    show_cols = [c for c in show_cols if c in q.columns]
    st.dataframe(q[show_cols].sort_values(["price","bedrooms"], ascending=[True, True]), use_container_width=True)

    st.subheader("Price by Bedrooms")
    if q["bedrooms"].notna().any() and q["price"].notna().any():
        chart_df = q[["bedrooms","price"]].dropna()
        st.scatter_chart(chart_df, x="bedrooms", y="price")

    st.caption("Data updates after the scheduled GitHub Action run.")

if __name__ == "__main__":
    main()
