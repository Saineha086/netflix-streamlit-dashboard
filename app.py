import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---------------- Page Config ----------------
st.set_page_config(page_title="Netflix Content Analytics", layout="wide")

st.title("📺 Netflix Content Analytics Dashboard")
st.caption("Interactive EDA project built with Streamlit (filters + insights).")

# ---------------- Load Data ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("Netflix Dataset.csv")

    # Standardize columns
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Parse dates
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["year"] = df["release_date"].dt.year

    # Fill missing values for key fields
    df["country"] = df["country"].fillna("Unknown")
    df["rating"] = df["rating"].fillna("Unrated")

    # Clean category + genre fields
    df["category"] = df["category"].astype(str).str.strip()  # Movie / TV Show
    df["type"] = df["type"].astype(str).str.strip()          # Genres (comma-separated)

    # Optional: handle duration parsing (not required for charts, but good for extension)
    if "duration" in df.columns:
        df["duration_value"] = df["duration"].astype(str).str.extract(r"(\d+)").astype(float)
        df["duration_unit"] = df["duration"].astype(str).str.extract(r"([A-Za-z]+)")

    return df

df = load_data()

# ---------------- Sidebar Filters ----------------
st.sidebar.header("🔎 Filters")

# Year range slider (handle missing year gracefully)
year_series = df["year"].dropna()
if len(year_series) > 0:
    min_year = int(year_series.min())
    max_year = int(year_series.max())
else:
    min_year, max_year = 2000, 2025

year_range = st.sidebar.slider("Year range", min_year, max_year, (min_year, max_year))

# Category filter (Movie / TV Show)
category_options = ["All"] + sorted(
        [x for x in df["category"].dropna().unique().tolist() if x != "nan"]
)
