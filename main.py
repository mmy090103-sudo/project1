# streamlit_games_visualization_neon.py
# 🌌 네온 우주 게이밍 테마 Streamlit 대시보드 (한글 + 평점 순위 40개)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ✅ 페이지 설정
st.set_page_config(page_title="🎮 전세계 게임 데이터 분석 🎮", layout="wide")

# -------------------- 🎨 네온 테마 스타일 --------------------
neon_style = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@400;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 20% 20%, #0a0a2a, #050517, #000010);
    color: #ffffff !important;
    font-family: 'Rajdhani', sans-serif;
}

/* 사이드바 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(10,10,40,0.95), rgba(20,20,60,0.95));
    border-right: 2px solid rgba(0,255,255,0.3);
    box-shadow: 0 0 15px rgba(0, 200, 255, 0.3);
}

/* 헤더 & 텍스트 네온 효과 */
h1, h2, h3, h4, h5, h6 {
    color: #9be8ff !important;
    font-family: 'Orbitron', sans-serif;
    text-shadow: 0 0 8px #00eaff, 0 0 20px #0077ff;
    transition: 0.3s;
}
h1:hover, h2:hover, h3:hover {
    color: #ffffff !important;
    text-shadow: 0 0 15px #ff00ff, 0 0 25px #00ffff;
}

/* 일반 텍스트 및 링크 */
p, label, span, div {
    color: #d4f1ff !important;
}
a {
    color: #00eaff !important;
    text-decoration: none;
}
a:hover {
    color: #ff66ff !important;
    text-shadow: 0 0 10px #ff00ff;
}

/* 버튼 */
.stButton>button {
    background: linear-gradient(90deg, #0ea5e9, #9333ea);
    color: white;
    border-radius: 8px;
    font-weight: 700;
    border: 1px solid #00ffff;
    box-shadow: 0 0 15px rgba(0,255,255,0.4);
    transition: all 0.3s ease;
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 25px #00eaff, 0 0 40px #ff00ff;
}

/* 표 & 데이터프레임 */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    border: 1px solid rgba(0,255,255,0.3);
    box-shadow: 0 0 15px rgba(0,200,255,0.2);
}

/* 마우스오버 시 텍스트 강조 */
label:hover, span:hover, div:hover {
    text-shadow: 0 0 6px #00ffff, 0 0 12px #ff00ff;
}

/* 애니메이션 배경 효과 */
@keyframes bg-glow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
html, body {
    background: linear-gradient(270deg, #010025, #0a0033, #1a004a);
    background-size: 600% 600%;
    animation: bg-glow 30s ease infinite;
}
</style>
"""
st.markdown(neon_style, unsafe_allow_html=True)

# -------------------- 데이터 로드 --------------------
@st.cache_data
def load_data(path='games_dataset.csv'):
    df = pd.read_csv(path)
    df = df.rename(columns=lambda x: x.strip())
    df['User Rating'] = pd.to_numeric(df['User Rating'], errors='coerce')
    df['Release Year'] = pd.to_numeric(df['Release Year'], errors='coerce').astype('Int64')
    return df

try:
    df = load_data()
except:
    st.error("⚠️ 'games_dataset.csv' 파일이 없습니다. 업로드해주세요.")
    uploaded = st.sidebar.file_uploader("CSV 업로드", type=['csv'])
    if uploaded:
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
if uploaded:
    df = load_data(uploaded)
    df['Game Name KR'] = df['Game Name'].apply(lambda x: KOREAN_NAME_MAP.get(x, x))

year_range = st.sidebar.slider("출시 연도", int(df['Release Year'].min()), int(df['Release Year'].max()), (int(df['Release Year'].min()), int(df['Release Year'].max())))
genres = ['전체'] + sorted(df['Genre'].dropna().unique().tolist())
selected_genres = st.sidebar.multiselect("장르", genres, default=['전체'])
rating_range = st.sidebar.slider("평점 범위", float(df['User Rating'].min()), float(df['User Rating'].max()), (float(df['User Rating'].min()), float(df['User Rating'].max())))

df_filtered = df[(df['Release Year'] >= year_range[0]) & (df['Release Year'] <= year_range[1])]
if '전체' not in selected_genres:
    df_filtered = df_filtered[df_filtered['Genre'].isin(selected_genres)]
df_filtered = df_filtered[(df_filtered['User Rating'] >= rating_range[0]) & (df_filtered['User Rating'] <= rating_range[1])]

# -------------------- 헤더 --------------------
st.markdown("<h1 style='text-align:center;'>🎮 전세계 게임 데이터 분석 🎮</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid rgba(0,255,255,0.3);'/>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("총 게임 수", f"{len(df_filtered):,}")
col2.metric("평균 평점", f"{df_filtered['User Rating'].mean():.2f}")
col3.metric("연도 범위", f"{df_filtered['Release Year'].min()} - {df_filtered['Release Year'].max()}")
col4.metric("장르 수", f"{df_filtered['Genre'].nunique()}")

# -------------------- 상위 40개 평점 순위 --------------------
st.markdown("<h2>🏆 상위 40개 게임 (평점 기준)</h2>", unsafe_allow_html=True)
TOP_N = 40
top_n = df_filtered.sort_values(by="User Rating", ascending=False).head(TOP_N)
top_n["순위"] = range(1, len(top_n) + 1)

fig_rank = px.bar(
    top_n[::-1],
    x="User Rating",
    y="Game Name KR",
    text="순위",
    orientation="h",
    title="상위 40개 게임 순위 (평점 기준)",
    labels={"User Rating": "평점", "Game Name KR": "게임명"}
)
fig_rank.update_traces(texttemplate="🏅 %{text}", textposition="outside", marker_color="#00eaff")
fig_rank.update_layout(template="plotly_dark", margin=dict(l=200), font_color="white", height=900)
st.plotly_chart(fig_rank, use_container_width=True)

# -------------------- 장르별 평균 --------------------
st.markdown("<h2>📋 장르별 평균 평점</h2>", unsafe_allow_html=True)
genre_avg = df_filtered.groupby("Genre")["User Rating"].mean().reset_index().sort_values("User Rating", ascending=True)
fig_genre = px.bar(genre_avg, x="User Rating", y="Genre", orientation="h", color="User Rating", color_continuous_scale="Blues")
fig_genre.update_layout(template="plotly_dark", font_color="white", height=600)
st.plotly_chart(fig_genre, use_container_width=True)

# -------------------- 데이터 미리보기 --------------------
st.markdown("<h2>🧾 데이터 미리보기</h2>", unsafe_allow_html=True)
st.dataframe(df_filtered[["Game Name KR", "Genre", "Platform", "Release Year", "User Rating"]].rename(columns={
    "Game Name KR": "게임명(한글)", "User Rating": "평점"
}))
