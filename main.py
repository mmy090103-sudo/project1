# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.neighbors import NearestNeighbors

st.set_page_config(page_title="🎮 Global Games Dashboard", page_icon="🎯", layout="wide")
st.title("🎮 Games Dataset — Interactive Analytics (Plotly + Streamlit)")

# -------------------------
# Helpers: load & clean data
# -------------------------
@st.cache_data
def load_csv_try_encodings(path):
    encs = ["utf-8", "cp949", "euc-kr", "latin1"]
    for e in encs:
        try:
            df = pd.read_csv(path, encoding=e)
            return df, e
        except Exception:
            continue
    raise ValueError("Cannot read CSV with common encodings.")

def clean_games_df(df: pd.DataFrame) -> pd.DataFrame:
    # normalize column names
    df = df.rename(columns=lambda c: c.strip())
    # required cols: Game Name, Genre, Platform, Release Year, User Rating
    for c in ["Game Name", "Genre", "Platform", "Release Year", "User Rating"]:
        if c not in df.columns:
            df[c] = np.nan

    # trim strings
    df["Game Name"] = df["Game Name"].astype(str).str.strip()
    df["Genre"] = df["Genre"].astype(str).str.strip()
    df["Platform"] = df["Platform"].astype(str).str.strip()

    # numeric conversions
    df["Release Year"] = pd.to_numeric(df["Release Year"], errors="coerce").astype("Int64")
    df["User Rating"] = pd.to_numeric(df["User Rating"], errors="coerce")

    # drop rows without game name
    df = df[~df["Game Name"].isna() & (df["Game Name"] != "nan")].copy()
    # reset index
    df = df.reset_index(drop=True)
    return df

# Load dataset (local uploaded file path)
DATA_PATH = "games_dataset.csv"  # replace if you change filename
df_raw, used_encoding = load_csv_try_encodings(DATA_PATH)
df = clean_games_df(df_raw)

# -------------------------
# Sidebar: filters & controls
# -------------------------
st.sidebar.header("🔎 Filters & Controls")

# platform & genre lists
platforms = sorted(df["Platform"].dropna().unique().tolist())
genres = sorted(df["Genre"].dropna().unique().tolist())
years = df["Release Year"].dropna().astype(int)
year_min, year_max = int(years.min()) if not years.empty else 2000, int(years.max()) if not years.empty else 2024

sel_platforms = st.sidebar.multiselect("Platforms", options=platforms, default=platforms[:6])
sel_genres = st.sidebar.multiselect("Genres", options=genres, default=genres[:6])
sel_year_range = st.sidebar.slider("Release Year range", min_value=year_min, max_value=year_max,
                                   value=(year_min, year_max), step=1)
rating_min, rating_max = float(np.nanmin(df["User Rating"])), float(np.nanmax(df["User Rating"]))
sel_rating = st.sidebar.slider("User Rating range", min_value=round(rating_min,2), max_value=round(rating_max,2),
                               value=(round(rating_min,2), round(rating_max,2)), step=0.1)

top_n = st.sidebar.slider("Top N games (by rating)", min_value=5, max_value=100, value=20, step=5)

st.sidebar.markdown("---")
st.sidebar.write(f"CSV encoding detected: **{used_encoding}**")
st.sidebar.caption("Dataset columns: " + ", ".join(df.columns.tolist()))
st.sidebar.markdown("⚙️ App by ChatGPT — customize further in code")

# -------------------------
# Apply filters
# -------------------------
mask = (
    df["Platform"].isin(sel_platforms) &
    df["Genre"].isin(sel_genres) &
    (df["Release Year"].fillna(0).astype(int) >= sel_year_range[0]) &
    (df["Release Year"].fillna(9999).astype(int) <= sel_year_range[1]) &
    (df["User Rating"].between(sel_rating[0], sel_rating[1], inclusive="both"))
)
filtered = df[mask].copy()

# -------------------------
# Top KPI row
# -------------------------
st.markdown("## Key metrics")
col1, col2, col3, col4 = st.columns([1.2,1.2,1.2,1.2])
col1.metric("🎮 Dataset rows (filtered)", f"{len(filtered):,}")
col2.metric("🏷️ Unique Games", f"{filtered['Game Name'].nunique():,}")
col3.metric("⭐ Avg User Rating", f"{filtered['User Rating'].mean():.2f}")
col4.metric("📅 Year range", f"{int(filtered['Release Year'].min()) if filtered['Release Year'].notna().any() else '-'} — {int(filtered['Release Year'].max()) if filtered['Release Year'].notna().any() else '-'}")

st.markdown("---")

# -------------------------
# Top-N by rating bar chart
# -------------------------
st.subheader(f"Top {top_n} Games by User Rating")
top_df = filtered.sort_values(by="User Rating", ascending=False).head(top_n).copy()
if top_df.empty:
    st.info("No data after filters — adjust filters to see results.")
else:
    # show rank, rating, year, platform
    top_df["Rank"] = range(1, len(top_df)+1)
    fig_top = px.bar(top_df[::-1],  # invert for horizontal descending
                     x="User Rating", y="Game Name",
                     orientation="h",
                     color="Platform",
                     hover_data=["Genre", "Platform", "Release Year", "User Rating"],
                     height=40*min(top_n,30))
    fig_top.update_layout(template="plotly_white", xaxis_title="User Rating", yaxis_title="")
    st.plotly_chart(fig_top, use_container_width=True)

    # Show detail for clicked (interactive selection is limited in streamlit; add selection dropdown)
    sel_game = st.selectbox("🔎 Show details for", options=["(none)"] + top_df["Game Name"].tolist())
    if sel_game != "(none)":
        row = top_df[top_df["Game Name"] == sel_game].iloc[0]
        st.markdown(f"**{row['Game Name']}**  —  {row['Platform']} / {row['Genre']} / {row['Release Year']}")
        st.metric("User Rating", f"{row['User Rating']:.2f}")

# -------------------------
# Distribution by Platform & Genre
# -------------------------
st.subheader("Rating distribution by Platform & Genre")

col_a, col_b = st.columns(2)

with col_a:
    fig_box = px.box(filtered, x="Platform", y="User Rating", color="Platform",
                     points="all", hover_data=["Game Name", "Genre", "Release Year"])
    fig_box.update_layout(template="plotly_white", showlegend=False, height=520)
    st.plotly_chart(fig_box, use_container_width=True)

with col_b:
    fig_violin = px.violin(filtered, x="Genre", y="User Rating", color="Genre", box=True, points="all",
                           hover_data=["Game Name", "Platform", "Release Year"])
    fig_violin.update_layout(template="plotly_white", showlegend=False, height=520)
    st.plotly_chart(fig_violin, use_container_width=True)

# -------------------------
# Yearly trend: avg rating by year
# -------------------------
st.subheader("Average User Rating by Release Year")

if filtered["Release Year"].notna().any():
    trend = filtered.dropna(subset=["Release Year"]).groupby("Release Year", as_index=False)["User Rating"].mean()
    trend = trend.sort_values("Release Year")
    fig_trend = px.line(trend, x="Release Year", y="User Rating", markers=True,
                        title="Average rating per year", labels={"User Rating":"Avg Rating"})
    fig_trend.update_layout(template="plotly_white", height=420)
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.info("No Release Year data available for selected filters.")

# -------------------------
# Sunburst: Genre -> Platform -> Count
# -------------------------
st.subheader("Composition: Genre → Platform → Count")
sun = filtered.groupby(["Genre","Platform"], as_index=False).size().reset_index(name="Count")
if not sun.empty:
    fig_sun = px.sunburst(sun, path=["Genre","Platform"], values="Count", color="Count",
                         color_continuous_scale="Blues", title="Genre/Platform composition")
    fig_sun.update_layout(template="plotly_white", height=520)
    st.plotly_chart(fig_sun, use_container_width=True)
else:
    st.info("No composition data to show.")

# -------------------------
# Similar game recommender (simple)
# -------------------------
st.subheader("🧭 Find similar games (by Genre, Platform, Rating)")
if not filtered.empty:
    # prepare features: one-hot genre & platform + normalized rating
    feat = pd.get_dummies(filtered[["Genre","Platform"]].fillna("Unknown"), prefix=["G","P"])
    feat["Rating"] = (filtered["User Rating"].fillna(filtered["User Rating"].mean()) - filtered["User Rating"].mean()) / (filtered["User Rating"].std() + 1e-9)
    # fit nearest neighbors
    nbrs = NearestNeighbors(n_neighbors=6, algorithm="auto").fit(feat.values)
    # selection
    choose = st.selectbox("Choose a game to find similar ones", options=filtered["Game Name"].tolist())
    if choose:
        idx = filtered[filtered["Game Name"]==choose].index[0]
        distances, indices = nbrs.kneighbors([feat.loc[idx].values])
        similar_idxs = indices[0][1:]  # exclude itself
        sim_df = filtered.iloc[similar_idxs][["Game Name","Platform","Genre","Release Year","User Rating"]]
        st.write("### Similar games")
        st.dataframe(sim_df.reset_index(drop=True))
else:
    st.info("No data to compute recommendations. Adjust filters.")

# -------------------------
# Correlation & heatmap (if numeric present beyond rating/year)
# -------------------------
st.subheader("📊 Numeric correlations")
num = filtered.select_dtypes(include=[np.number]).dropna(axis=1, how="all")
if num.shape[1] >= 2:
    corr = num.corr()
    fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", title="Correlation matrix")
    fig_corr.update_layout(template="plotly_white", height=420)
    st.plotly_chart(fig_corr, use_container_width=True)
else:
    st.info("Not enough numeric columns for correlation.")

# -------------------------
# Data table + download
# -------------------------
st.markdown("---")
st.subheader("📁 Data Explorer & Download")
st.write("Rows in filtered dataset:", len(filtered))
st.dataframe(filtered.reset_index(drop=True), use_container_width=True, height=300)

csv = filtered.to_csv(index=False).encode("utf-8-sig")
st.download_button("Download filtered CSV", data=csv, file_name="games_filtered.csv", mime="text/csv")

# -------------------------
# Footer / credits
# -------------------------
st.markdown("---")
st.markdown("Made with ❤️  — Streamlit + Plotly. Customize further as needed.")

