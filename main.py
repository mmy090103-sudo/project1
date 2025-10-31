# streamlit_games_visualization.py
# Streamlit app to visualize games_dataset.csv using Plotly (high-quality, feature-rich)
# How to use:
# 1) Save this file as streamlit_app.py (or keep the name).
# 2) Place games_dataset.csv in the same folder or upload it via the sidebar upload widget.
# 3) Run: streamlit run streamlit_games_visualization.py
#
# This file is intended for GitHub. Commit it and create a Streamlit app from the repo.

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

st.set_page_config(page_title="Games Dataset Explorer", layout="wide", initial_sidebar_state="expanded")

# -------------------- Helpers & Caching --------------------
@st.cache_data(show_spinner=False)
def load_data(path=None, uploaded_file=None):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_csv(path) if path is not None else pd.DataFrame()
    # Normalize column names for convenience
    df = df.rename(columns=lambda s: s.strip())
    # Ensure types
    if 'Release Year' in df.columns:
        df['Release Year'] = pd.to_numeric(df['Release Year'], errors='coerce').astype('Int64')
    if 'User Rating' in df.columns:
        df['User Rating'] = pd.to_numeric(df['User Rating'], errors='coerce')
    return df

# -------------------- Load dataset --------------------
DEFAULT_PATH = "./games_dataset.csv"
uploaded = st.sidebar.file_uploader("Upload a CSV file (optional)", type=["csv"]) 

# Load default if upload not provided
df = load_data(path=DEFAULT_PATH, uploaded_file=uploaded)

if df.empty:
    st.sidebar.warning("No data loaded. Upload a CSV or place games_dataset.csv in the app folder.")
    st.stop()

# -------------------- Sidebar Filters --------------------
st.sidebar.header("Filters & Settings")
with st.sidebar.expander("Column selection / tidy up", expanded=False):
    cols = df.columns.tolist()
    chosen_cols = st.multiselect("Columns to include in analysis", cols, default=cols)
    df = df[chosen_cols]

# Quick checks and derived columns
if 'Release Year' not in df.columns:
    st.error("This app expects a 'Release Year' column. Please include it or map your year column.")
    st.stop()

if 'User Rating' not in df.columns:
    st.warning("No 'User Rating' column found. Some visualizations that depend on ratings will be hidden.")

# Filters
years = df['Release Year'].dropna().astype(int)
ymin, ymax = int(years.min()), int(years.max())
year_range = st.sidebar.slider("Release Year range", ymin, ymax, (ymin, ymax), step=1)

if 'Genre' in df.columns:
    genres = ['All'] + sorted(df['Genre'].dropna().unique().tolist())
    selected_genres = st.sidebar.multiselect("Genre (multi-select)", genres, default=['All'])
else:
    selected_genres = ['All']

if 'Platform' in df.columns:
    platforms = ['All'] + sorted(df['Platform'].dropna().unique().tolist())
    selected_platforms = st.sidebar.multiselect("Platform (multi-select)", platforms, default=['All'])
else:
    selected_platforms = ['All']

# rating filter
if 'User Rating' in df.columns:
    rmin = float(np.nanmin(df['User Rating']))
    rmax = float(np.nanmax(df['User Rating']))
    rating_range = st.sidebar.slider("User Rating range", float(rmin), float(rmax), (float(rmin), float(rmax)))
else:
    rating_range = None

# display options
st.sidebar.markdown("---")
show_top_k = st.sidebar.number_input("Show top K items in lists", min_value=5, max_value=100, value=10)
log_scale = st.sidebar.checkbox("Use log scale for counts", value=False)

# -------------------- Data filtering --------------------
df_filtered = df.copy()
# year
df_filtered = df_filtered[(df_filtered['Release Year'] >= year_range[0]) & (df_filtered['Release Year'] <= year_range[1])]
# genre
if 'Genre' in df_filtered.columns and 'All' not in selected_genres:
    df_filtered = df_filtered[df_filtered['Genre'].isin(selected_genres)]
# platform
if 'Platform' in df_filtered.columns and 'All' not in selected_platforms:
    df_filtered = df_filtered[df_filtered['Platform'].isin(selected_platforms)]
# rating
if rating_range is not None:
    df_filtered = df_filtered[(df_filtered['User Rating'] >= rating_range[0]) & (df_filtered['User Rating'] <= rating_range[1])]

# -------------------- Main layout --------------------
st.title("🎮 Games Dataset Explorer")
st.markdown("Interactive, production-grade Streamlit app using Plotly for visuals.\nUse the sidebar to filter data and the controls above charts to tune visuals.")

# Key metrics
col1, col2, col3, col4 = st.columns([1,1,1,1])
with col1:
    st.metric("Total games", f"{len(df_filtered):,}", delta=f"{len(df_filtered)-len(df):,}" )
with col2:
    if 'User Rating' in df_filtered.columns:
        st.metric("Avg. user rating", f"{df_filtered['User Rating'].mean():.2f}")
    else:
        st.metric("Avg. user rating", "N/A")
with col3:
    st.metric("Year range", f"{df_filtered['Release Year'].min()} — {df_filtered['Release Year'].max()}")
with col4:
    if 'Genre' in df_filtered.columns:
        st.metric("Unique genres", f"{df_filtered['Genre'].nunique()}")
    else:
        st.metric("Unique genres", "N/A")

st.markdown("---")

# -------------------- Charts: top row --------------------
chart1, chart2 = st.columns([1.2, 1])

with chart1:
    st.subheader("Ratings distribution")
    if 'User Rating' in df_filtered.columns:
        fig_hist = px.histogram(df_filtered, x='User Rating', nbins=30, marginal='box', hover_data=df_filtered.columns, labels={'User Rating':'User Rating'}, title='Distribution of User Ratings')
        fig_hist.update_layout(margin=dict(t=40,l=20,r=20,b=20))
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("User Rating column not available for this chart.")

with chart2:
    st.subheader("Games per Year")
    count_by_year = df_filtered.groupby('Release Year').size().reset_index(name='count')
    if log_scale:
        fig_line = px.line(count_by_year, x='Release Year', y='count', markers=True, title='Games released per year (log scale)')
        fig_line.update_yaxes(type='log')
    else:
        fig_line = px.bar(count_by_year, x='Release Year', y='count', title='Games released per year')
    fig_line.update_layout(margin=dict(t=40,l=20,r=20,b=20))
    st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")

# -------------------- Charts: middle row --------------------
mid1, mid2 = st.columns([1,1])

with mid1:
    st.subheader("Rating vs Release Year (scatter)")
    if 'User Rating' in df_filtered.columns:
        # jitter release year slightly for better spread
        df_plot = df_filtered.copy()
        df_plot['year_jitter'] = df_plot['Release Year'] + np.random.normal(0, 0.18, size=len(df_plot))
        color_col = 'Genre' if 'Genre' in df_plot.columns else None
        fig_scatter = px.scatter(df_plot, x='year_jitter', y='User Rating', color=color_col, hover_data=['Game Name','Platform','Release Year'], labels={'year_jitter':'Release Year'}, title='User Rating by Release Year')
        fig_scatter.update_layout(showlegend=True, margin=dict(t=40,l=20,r=20,b=20))
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("User Rating column not available for this chart.")

with mid2:
    st.subheader("Top genres & platforms")
    cols_to_count = []
    if 'Genre' in df_filtered.columns:
        top_genres = df_filtered['Genre'].value_counts().nlargest(show_top_k).reset_index()
        top_genres.columns = ['Genre','count']
        fig_gen = px.bar(top_genres, x='count', y='Genre', orientation='h', title=f'Top {show_top_k} Genres', hover_data=['count'])
        st.plotly_chart(fig_gen, use_container_width=True)
    if 'Platform' in df_filtered.columns:
        top_plats = df_filtered['Platform'].value_counts().nlargest(show_top_k).reset_index()
        top_plats.columns = ['Platform','count']
        fig_plat = px.bar(top_plats, x='count', y='Platform', orientation='h', title=f'Top {show_top_k} Platforms', hover_data=['count'])
        st.plotly_chart(fig_plat, use_container_width=True)

st.markdown("---")

# -------------------- Sunburst / Treemap --------------------
st.subheader("Genre → Platform breakdown (Sunburst)")
if 'Genre' in df_filtered.columns and 'Platform' in df_filtered.columns:
    sun = df_filtered.groupby(['Genre','Platform']).size().reset_index(name='count')
    fig_sun = px.sunburst(sun, path=['Genre','Platform'], values='count', title='Genre → Platform distribution')
    st.plotly_chart(fig_sun, use_container_width=True)
else:
    st.info("Need both Genre and Platform columns for Sunburst.")

st.markdown("---")

# -------------------- Table & Detail panel --------------------
st.subheader("Data table & game detail")
with st.expander("Filtered data (preview)", expanded=True):
    st.dataframe(df_filtered.reset_index(drop=True))

# Row selection by game name
game_to_inspect = st.selectbox("Select a game to inspect (by name)", options=['(none)'] + sorted(df_filtered['Game Name'].dropna().unique().tolist()))
if game_to_inspect and game_to_inspect != '(none)':
    row = df_filtered[df_filtered['Game Name'] == game_to_inspect].iloc[0]
    st.markdown(f"**{row.get('Game Name','-')}**  ")
    st.write(row.to_frame().T)

# Download filtered dataset
csv = df_filtered.to_csv(index=False)
st.download_button("Download filtered data as CSV", data=csv, file_name="games_filtered.csv", mime='text/csv')

st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ by Streamlit + Plotly. Customize on GitHub.")

# -------------------- Footer: tips for customization --------------------
with st.expander("Developer tips & customization (for GitHub)"):
    st.markdown(
        """
        - To publish: push this file + games_dataset.csv to a GitHub repo and connect the repo to Streamlit Cloud (app will run automatically).
        - Add additional columns (Sales, Critic Score, Publisher) to unlock more visualizations (maps, correlation matrix, regression lines).
        - Consider adding caching for heavy transforms and using `st.session_state` for complex interactions.
        - This app uses Plotly for interactive visuals; you can add `plotly.graph_objects` traces to compose more advanced figures.
        """
    )

# End of file
