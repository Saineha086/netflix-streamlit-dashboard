import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Netflix Content Analytics", layout="wide")

st.title("📺 Netflix Content Analytics Dashboard")
st.caption("Interactive EDA project built with Streamlit (filters + insights).")

# ---------- Load Data ----------
@st.cache_data
def load_data():
    df = pd.read_csv("Netflix Dataset.csv")

    # Standardize columns
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Dates
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["year"] = df["release_date"].dt.year

    # Fill missing
    df["country"] = df["country"].fillna("Unknown")
    df["rating"] = df["rating"].fillna("Unrated")

    # Clean key cols
    df["category"] = df["category"].astype(str).str.strip()   # Movie / TV Show
    df["type"] = df["type"].astype(str).str.strip()           # Genres combos

    return df

df = load_data()

# ---------- Sidebar Filters ----------
st.sidebar.header("🔎 Filters")

# Year filter
min_year = int(df["year"].dropna().min()) if df["year"].notna().any() else 2000
max_year = int(df["year"].dropna().max()) if df["year"].notna().any() else 2025
year_range = st.sidebar.slider("Year range", min_year, max_year, (min_year, max_year))

# Category filter (Movie / TV Show)
category_options = ["All"] + sorted(df["category"].dropna().unique().tolist())
category_choice = st.sidebar.selectbox("Content Category", category_options)

# Rating filter
rating_options = ["All"] + sorted(df["rating"].dropna().unique().tolist())
rating_choice = st.sidebar.selectbox("Rating", rating_options)

# Country filter (top list to keep it fast)
country_options = ["All"] + sorted(df["country"].dropna().unique().tolist())
country_choice = st.sidebar.selectbox("Country", country_options)

# Genre filter (explode type into individual genres)
genres = (
    df["type"].str.split(",").explode().str.strip()
    .replace("nan", np.nan).dropna().unique().tolist()
)
genres = ["All"] + sorted(genres)
genre_choice = st.sidebar.selectbox("Genre", genres)

# ---------- Apply Filters ----------
filtered = df.copy()

filtered = filtered[(filtered["year"].fillna(0) >= year_range[0]) & (filtered["year"].fillna(0) <= year_range[1])]

if category_choice != "All":
    filtered = filtered[filtered["category"] == category_choice]

if rating_choice != "All":
    filtered = filtered[filtered["rating"] == rating_choice]

if country_choice != "All":
    # handles multi-country rows like "United States, India"
    filtered = filtered[filtered["country"].str.contains(country_choice, na=False)]

if genre_choice != "All":
    filtered = filtered[filtered["type"].str.contains(genre_choice, na=False)]

# ---------- KPI Row ----------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Titles (filtered)", f"{len(filtered):,}")
col2.metric("Total Titles (dataset)", f"{len(df):,}")

movie_pct = (filtered["category"].value_counts(normalize=True).get("Movie", 0) * 100)
tv_pct = (filtered["category"].value_counts(normalize=True).get("TV Show", 0) * 100)
col3.metric("Movie %", f"{movie_pct:.1f}%")
col4.metric("TV Show %", f"{tv_pct:.1f}%")

st.divider()

# ---------- Charts ----------
left, right = st.columns(2)

with left:
    st.subheader("Movies vs TV Shows (%)")
    pct = (filtered["category"].value_counts(normalize=True) * 100).round(1)

    fig = plt.figure(figsize=(6,4))
    pct.plot(kind="bar")
    plt.xlabel("Category")
    plt.ylabel("Percentage (%)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    st.pyplot(fig)

with right:
    st.subheader("Titles Added Over Time")
    titles_by_year = filtered.groupby("year")["show_id"].count().sort_index()

    fig = plt.figure(figsize=(6,4))
    titles_by_year.plot()
    plt.xlabel("Year")
    plt.ylabel("Number of Titles")
    plt.tight_layout()
    st.pyplot(fig)

st.divider()

c1, c2 = st.columns(2)

with c1:
    st.subheader("Top Countries (Top 10)")
    top_countries = (
        filtered["country"].str.split(",").explode().str.strip()
        .value_counts().head(10)
    )
    fig = plt.figure(figsize=(7,4))
    top_countries.plot(kind="bar")
    plt.xlabel("Country")
    plt.ylabel("Titles")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig)

with c2:
    st.subheader("Top Genres (Top 10)")
    top_genres = (
        filtered["type"].str.split(",").explode().str.strip()
        .value_counts().head(10)
    )
    fig = plt.figure(figsize=(7,4))
    top_genres.sort_values().plot(kind="barh")
    plt.xlabel("Titles")
    plt.ylabel("Genre")
    plt.tight_layout()
    st.pyplot(fig)

st.divider()

st.subheader("Key Insights (Auto from current filters)")
st.write(
    f"- Dataset contains **{len(df):,}** titles; current filters show **{len(filtered):,}** titles.\n"
    f"- Movies share: **{movie_pct:.1f}%** | TV Shows share: **{tv_pct:.1f}%** in the filtered view.\n"
    f"- Top country (filtered): **{top_countries.index[0] if len(top_countries) else 'N/A'}**\n"
    f"- Top genre (filtered): **{top_genres.index[-1] if len(top_genres) else 'N/A'}**"
)
