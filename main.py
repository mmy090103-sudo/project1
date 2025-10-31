# streamlit_games_visualization.py
# 🌌 한국어/우주 테마 고급 Streamlit 대시보드 (평점 순위 40개 버전)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="🌌 게임 데이터 대시보드 (한글)", layout="wide")

# -------------------- 스타일 --------------------
page_bg = """
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 10% 10%, #071029 0%, #081229 30%, #000014 100%);
    color: #ffffff !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#071029,#0b1a2b);
    color: #ffffff !important;
}
h1, h2, h3, h4, h5, h6, p, span, label, div {
    color: #ffffff !important;
    font-family: 'Pretendard', sans-serif;
}
.stButton>button {
    background-color: #0ea5e9;
    color: #ffffff;
    border-radius: 8px;
}
[data-testid="stMetricValue"] {
    color: #ffffff !important;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# -------------------- 데이터 로드 --------------------
@st.cache_data(show_spinner=True)
def load_data(path: str = 'games_dataset.csv') -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.rename(columns=lambda x: x.strip())
    if 'User Rating' in df.columns:
        df['User Rating'] = pd.to_numeric(df['User Rating'], errors='coerce')
    if 'Release Year' in df.columns:
        df['Release Year'] = pd.to_numeric(df['Release Year'], errors='coerce').astype('Int64')
    return df

try:
    df = load_data()
except Exception:
    st.error("❌ 'games_dataset.csv' 파일이 필요합니다. 사이드바에서 업로드해주세요.")
    uploaded = st.sidebar.file_uploader("CSV 업로드", type=['csv'])
    if uploaded is not None:
        df = load_data(uploaded)
    else:
        st.stop()

# -------------------- 한글 매핑 --------------------
KOREAN_NAME_MAP = {
    'The Legend of Zelda: Breath of the Wild': '젤다의 전설: 야생의 숨결',
    'Super Mario Odyssey': '슈퍼 마리오 오디세이',
    'Minecraft': '마인크래프트',
    'Grand Theft Auto V': '그랜드 테프트 오토 5',
    'Red Dead Redemption 2': '레드 데드 리뎀션 2',
    'League of Legends': '리그 오브 레전드',
    'Overwatch': '오버워치',
    'Fortnite': '포트나이트',
    'Call of Duty: Modern Warfare': '콜 오브 듀티: 모던 워페어',
    'Animal Crossing: New Horizons': '모여봐요 동물의 숲',
    'Elden Ring': '엘든 링',
    'Cyberpunk 2077': '사이버펑크 2077',
    'Genshin Impact': '원신',
    'PUBG: Battlegrounds': '배틀그라운드',
    "PlayerUnknown's Battlegrounds": '배틀그라운드',
    'The Witcher 3: Wild Hunt': '위쳐 3: 와일드 헌트',
}

df['Game Name KR'] = df.get('Game Name', pd.Series(df.index)).apply(lambda x: KOREAN_NAME_MAP.get(x, x))

# -------------------- 필터 --------------------
st.sidebar.header("🎮 필터")
uploaded = st.sidebar.file_uploader("CSV 업로드 (선택)", type=['csv'])
if uploaded is not None:
    df = load_data(uploaded)
    df['Game Name KR'] = df['Game Name'].apply(lambda x: KOREAN_NAME_MAP.get(x, x))

min_year = int(df['Release Year'].min())
max_year = int(df['Release Year'].max())
year_range = st.sidebar.slider("출시 연도", min_year, max_year, (min_year, max_year))

genres = ['전체'] + sorted(df['Genre'].dropna().unique().tolist())
selected_genres = st.sidebar.multiselect("장르", genres, default=['전체'])

rating_min = float(df['User Rating'].min())
rating_max = float(df['User Rating'].max())
rating_range = st.sidebar.slider("평점 범위", rating_min, rating_max, (rating_min, rating_max))

df_filtered = df[(df['Release Year'] >= year_range[0]) & (df['Release Year'] <= year_range[1])]
if '전체' not in selected_genres:
    df_filtered = df_filtered[df_filtered['Genre'].isin(selected_genres)]
df_filtered = df_filtered[(df_filtered['User Rating'] >= rating_range[0]) & (df_filtered['User Rating'] <= rating_range[1])]

# -------------------- 헤더 --------------------
st.title("🌌 게임 데이터 대시보드 (상위 40개 평점 순위 포함)")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
col1.metric("총 게임 수", f"{len(df_filtered):,}")
col2.metric("평균 평점", f"{df_filtered['User Rating'].mean():.2f}")
col3.metric("연도 범위", f"{df_filtered['Release Year'].min()} - {df_filtered['Release Year'].max()}")
col4.metric("장르 수", f"{df_filtered['Genre'].nunique()}")

# -------------------- 상위 40개 평점 순위 --------------------
st.header("🏆 상위 40개 게임 (평점 기준 순위)")
TOP_N = 40
top_n = df_filtered.sort_values(by="User Rating", ascending=False).head(TOP_N).copy()
top_n["순위"] = range(1, len(top_n) + 1)

fig_rank = px.bar(
    top_n[::-1],
    x="User Rating",
    y="Game Name KR",
    text="순위",
    orientation="h",
    title="🎯 상위 40개 게임 평점 순위",
    labels={"User Rating": "평점", "Game Name KR": "게임 이름"},
)
fig_rank.update_traces(
    texttemplate="🏅%{text}",
    textposition="outside",
    marker_color="#38bdf8"
)
fig_rank.update_layout(
    template="plotly_dark",
    margin=dict(l=200),
    font_color="white",
    height=900
)
st.plotly_chart(fig_rank, use_container_width=True)

# -------------------- 추가 그래프 --------------------
st.markdown("---")
st.header("📊 추가 시각화")

# 장르별 평균 평점
genre_avg = df_filtered.groupby("Genre")["User Rating"].mean().reset_index().sort_values("User Rating", ascending=True)
fig_genre = px.bar(genre_avg, x="User Rating", y="Genre", orientation="h", title="장르별 평균 평점", color="User Rating", color_continuous_scale="Blues")
fig_genre.update_layout(template="plotly_dark", font_color="white", height=600)
st.plotly_chart(fig_genre, use_container_width=True)

# 연도별 평점 추이
year_avg = df_filtered.groupby("Release Year")["User Rating"].mean().reset_index()
fig_year = px.line(year_avg, x="Release Year", y="User Rating", title="연도별 평균 평점 추이", markers=True)
fig_year.update_layout(template="plotly_dark", font_color="white")
st.plotly_chart(fig_year, use_container_width=True)

# 장르 비율
genre_share = df_filtered["Genre"].value_counts().reset_index()
genre_share.columns = ["Genre", "Count"]
fig_pie = px.pie(genre_share, values="Count", names="Genre", title="장르별 비율", color_discrete_sequence=px.colors.sequential.Blues)
fig_pie.update_traces(textposition="inside", textinfo="percent+label")
fig_pie.update_layout(template="plotly_dark", font_color="white")
st.plotly_chart(fig_pie, use_container_width=True)

# -------------------- 데이터 미리보기 --------------------
st.header("📋 데이터 미리보기 및 다운로드")
st.dataframe(df_filtered[["Game Name KR", "Genre", "Platform", "Release Year", "User Rating"]].rename(columns={
    "Game Name KR": "게임명(한글)", "User Rating": "평점"
}))

csv = df_filtered.to_csv(index=False).encode("utf-8-sig")
st.download_button("💾 CSV 다운로드", csv, "filtered_games_korean.csv", "text/csv")

st.caption("Made with ❤️ · 우주 테마 + 평점 순위 40개 버전")
