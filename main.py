# 🌌 전세계 게임 데이터 분석 (네온 게이밍 테마 ver.3)
# author: GPT-5

import streamlit as st
import pandas as pd
import plotly.express as px

# ✅ 페이지 설정
st.set_page_config(page_title="🎮 전세계 게임 데이터 분석 🎮", layout="wide")

# -------------------- 🎨 네온 테마 스타일 --------------------
neon_style = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Do+Hyeon&family=Russo+One&family=Press+Start+2P&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 30% 30%, #0a0033, #050017, #000010);
    color: #ffffff !important;
    font-family: 'Do Hyeon', sans-serif;
}

/* 🟦 사이드바 스타일 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(5,10,35,0.95), rgba(20,0,50,0.95));
    border-right: 2px solid rgba(0,255,255,0.3);
    box-shadow: 0 0 15px rgba(0, 200, 255, 0.3);
}
[data-testid="stSidebar"] * {
    color: #00eaff !important;  /* 사이드바 글씨 색상 */
    font-weight: 600;
}
[data-baseweb="select"] > div {
    background-color: rgba(15, 15, 40, 0.8) !important;
    color: white !important;
    border-radius: 8px !important;
    border: 1px solid rgba(0,255,255,0.4) !important;
}
[data-baseweb="input"] input {
    color: white !important;
}
.css-1y4p8pa, .css-qrbaxs, .css-10trblm, .css-1dp5vir {
    color: #00ffff !important;
}
.stSlider > div > div > div > div {
    background: linear-gradient(90deg, #00ffff, #7f00ff) !important;
}

/* 제목 */
h1 {
    color: #9be8ff !important;
    font-family: 'Orbitron', sans-serif;
    text-align: center;
    text-shadow: 0 0 15px #00ffff, 0 0 30px #0077ff;
    letter-spacing: 2px;
    margin-bottom: 10px;
    transition: 0.3s;
}
h1:hover {
    color: #ffffff;
    text-shadow: 0 0 25px #ff00ff, 0 0 40px #00ffff;
}
h2 {
    color: #90e0ff;
    font-family: 'Russo One', sans-serif;
    text-shadow: 0 0 8px #00eaff, 0 0 20px #0077ff;
    margin-top: 40px;
}

/* 버튼 */
.stButton>button {
    background: linear-gradient(90deg, #00c6ff, #7f00ff);
    color: white;
    border-radius: 10px;
    font-weight: 700;
    font-family: 'Press Start 2P', cursive;
    font-size: 12px;
    letter-spacing: 1px;
    border: 1px solid #00ffff;
    box-shadow: 0 0 15px rgba(0,255,255,0.5);
    transition: all 0.3s ease;
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 25px #00ffff, 0 0 40px #ff00ff;
}

/* 데이터프레임 */
[data-testid="stDataFrame"] {
    border-radius: 15px;
    border: 1px solid rgba(0,255,255,0.2);
    box-shadow: 0 0 20px rgba(0,200,255,0.2);
}

/* 배경 애니메이션 */
@keyframes glow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
html, body {
    background: linear-gradient(270deg, #010025, #0a0033, #1a004a, #001d4a);
    background-size: 600% 600%;
    animation: glow 40s ease infinite;
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

# -------------------- 한글 게임명 매핑 --------------------
KOREAN_NAME_MAP = {
    'Minecraft': '마인크래프트',
    'League of Legends': '리그 오브 레전드',
    'Fortnite': '포트나이트',
    'PUBG: Battlegrounds': '배틀그라운드',
    'The Legend of Zelda: Breath of the Wild': '젤다의 전설: 야생의 숨결',
    'Super Mario Odyssey': '슈퍼 마리오 오디세이',
    'Red Dead Redemption 2': '레드 데드 리뎀션 2',
    'Elden Ring': '엘든 링',
    'Genshin Impact': '원신',
    'The Witcher 3: Wild Hunt': '위쳐 3: 와일드 헌트',
}
df['Game Name KR'] = df.get('Game Name', pd.Series(df.index)).apply(lambda x: KOREAN_NAME_MAP.get(x, x))

# -------------------- 필터 --------------------
st.sidebar.header("🎮 필터")
year_range = st.sidebar.slider("출시 연도", int(df['Release Year'].min()), int(df['Release Year'].max()),
                               (int(df['Release Year'].min()), int(df['Release Year'].max())))
genres = ['전체'] + sorted(df['Genre'].dropna().unique().tolist())
selected_genres = st.sidebar.multiselect("장르", genres, default=['전체'])
rating_range = st.sidebar.slider("평점 범위", float(df['User Rating'].min()), float(df['User Rating'].max()),
                                 (float(df['User Rating'].min()), float(df['User Rating'].max())))

df_filtered = df[(df['Release Year'] >= year_range[0]) & (df['Release Year'] <= year_range[1])]
if '전체' not in selected_genres:
    df_filtered = df_filtered[df_filtered['Genre'].isin(selected_genres)]
df_filtered = df_filtered[(df_filtered['User Rating'] >= rating_range[0]) & (df_filtered['User Rating'] <= rating_range[1])]

# -------------------- 타이틀 --------------------
st.markdown("<h1>🎮 전세계 게임 데이터 분석 🎮</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid rgba(0,255,255,0.4);'/>", unsafe_allow_html=True)

# -------------------- 요약 --------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("총 게임 수", f"{len(df_filtered):,}")
col2.metric("평균 평점", f"{df_filtered['User Rating'].mean():.2f}")
col3.metric("출시연도", f"{df_filtered['Release Year'].min()} ~ {df_filtered['Release Year'].max()}")
col4.metric("장르 수", f"{df_filtered['Genre'].nunique()}")

# -------------------- 상위 40 게임 --------------------
st.markdown("<h2>🏆 평점 상위 40 게임</h2>", unsafe_allow_html=True)
top_40 = df_filtered.sort_values(by="User Rating", ascending=False).head(40)
top_40["순위"] = range(1, len(top_40)+1)

fig_rank = px.bar(
    top_40[::-1],
    x="User Rating",
    y="Game Name KR",
    text="순위",
    orientation="h",
    color="User Rating",
    color_continuous_scale=["#0ff", "#80f", "#f0f"],
    title="상위 40 게임 평점 순위"
)
fig_rank.update_traces(
    texttemplate="🏅 %{text}",
    textposition="outside",
    marker_line_width=0,
    marker_line_color="rgba(255,255,255,0)"
)
fig_rank.update_layout(
    template="plotly_dark",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="white",
    margin=dict(l=180, r=20, t=50, b=50),
    height=950,
)
st.plotly_chart(fig_rank, use_container_width=True)

# -------------------- 장르별 평균 --------------------
st.markdown("<h2>📊 장르별 평균 평점</h2>", unsafe_allow_html=True)
genre_avg = df_filtered.groupby("Genre")["User Rating"].mean().reset_index().sort_values("User Rating", ascending=True)
fig_genre = px.bar(
    genre_avg, x="User Rating", y="Genre", orientation="h",
    color="User Rating", color_continuous_scale="Plasma",
)
fig_genre.update_layout(
    template="plotly_dark",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="white",
    height=600
)
st.plotly_chart(fig_genre, use_container_width=True)

# -------------------- 데이터 미리보기 --------------------
st.markdown("<h2>🧾 데이터 미리보기</h2>", unsafe_allow_html=True)
st.dataframe(df_filtered[["Game Name KR", "Genre", "Platform", "Release Year", "User Rating"]].rename(columns={
    "Game Name KR": "게임명(한글)", "User Rating": "평점"
}))
