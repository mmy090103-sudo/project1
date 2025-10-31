# streamlit_games_visualization.py
# 고급 버전: 한글 UI + 보기 좋은 스타일 + 다양한 Plotly 시각화 + 인터랙티브 기능
# 실행방법:
# 1) games_dataset.csv 파일을 동일 폴더에 두세요.
# 2) 터미널에서: streamlit run streamlit_games_visualization.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="🎮 게임 데이터 시각화 대시보드", layout="wide")

# -------------------- 사용자 정의 CSS (배경, 폰트, 색상) --------------------
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #f6f7fb;
}
[data-testid="stSidebar"] {
    background-color: #f0f2f6;
}
h1, h2, h3, h4, h5, h6 {
    color: #1e1e1e;
}
p, span, label, div {
    font-family: 'Pretendard', sans-serif;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# -------------------- 데이터 불러오기 --------------------
@st.cache_data(show_spinner=True)
def load_data(path: str):
    df = pd.read_csv(path)
    df = df.rename(columns=lambda x: x.strip())
    return df

try:
    df = load_data("games_dataset.csv")
except FileNotFoundError:
    st.error("❌ 'games_dataset.csv' 파일이 폴더에 없습니다. 업로드하거나 경로를 확인하세요.")
    st.stop()

# -------------------- 사이드바 --------------------
st.sidebar.title("🎮 필터 설정")

# 기본 필터
years = sorted(df['Release Year'].dropna().unique())
year_min, year_max = st.sidebar.select_slider(
    '출시 연도 범위 선택',
    options=years,
    value=(min(years), max(years))
)

selected_genres = st.sidebar.multiselect(
    '장르 선택', ['전체'] + sorted(df['Genre'].dropna().unique()), default=['전체']
)
selected_platforms = st.sidebar.multiselect(
    '플랫폼 선택', ['전체'] + sorted(df['Platform'].dropna().unique()), default=['전체']
)

rating_min, rating_max = st.sidebar.slider(
    '사용자 평점 범위', float(df['User Rating'].min()), float(df['User Rating'].max()), (float(df['User Rating'].min()), float(df['User Rating'].max()))
)

# 데이터 필터링
df_filtered = df[(df['Release Year'] >= year_min) & (df['Release Year'] <= year_max)]
if '전체' not in selected_genres:
    df_filtered = df_filtered[df_filtered['Genre'].isin(selected_genres)]
if '전체' not in selected_platforms:
    df_filtered = df_filtered[df_filtered['Platform'].isin(selected_platforms)]
df_filtered = df_filtered[(df_filtered['User Rating'] >= rating_min) & (df_filtered['User Rating'] <= rating_max)]

# -------------------- 제목 및 요약 --------------------
st.title("🎮 게임 데이터 시각화 대시보드")
st.caption("Plotly 기반 인터랙티브 시각화 / Streamlit 고급 버전")

col1, col2, col3, col4 = st.columns(4)
col1.metric("게임 수", f"{len(df_filtered):,}")
col2.metric("평균 평점", f"{df_filtered['User Rating'].mean():.2f}")
col3.metric("출시 연도 범위", f"{df_filtered['Release Year'].min()} - {df_filtered['Release Year'].max()}")
col4.metric("고유 장르 수", f"{df_filtered['Genre'].nunique()}")

st.markdown("---")

# -------------------- 시각화 섹션 --------------------

# 1️⃣ 사용자 평점 분포
st.subheader("📊 사용자 평점 분포")
fig_hist = px.histogram(df_filtered, x='User Rating', nbins=30, color='Genre', marginal='box', title='사용자 평점 히스토그램', hover_data=['Game Name', 'Platform'])
st.plotly_chart(fig_hist, use_container_width=True)

# 2️⃣ 연도별 게임 출시 추이
st.subheader("📈 연도별 게임 출시 수")
count_by_year = df_filtered.groupby('Release Year').size().reset_index(name='출시 수')
fig_bar = px.bar(count_by_year, x='Release Year', y='출시 수', text='출시 수', title='연도별 출시된 게임 수', color='출시 수', color_continuous_scale='Blues')
fig_bar.update_traces(textposition='outside')
st.plotly_chart(fig_bar, use_container_width=True)

# 3️⃣ 장르별 평균 평점
st.subheader("⭐ 장르별 평균 평점")
avg_rating = df_filtered.groupby('Genre')['User Rating'].mean().reset_index().sort_values(by='User Rating', ascending=False)
fig_avg = px.bar(avg_rating, x='User Rating', y='Genre', orientation='h', title='장르별 평균 사용자 평점', color='User Rating', color_continuous_scale='Viridis')
st.plotly_chart(fig_avg, use_container_width=True)

# 4️⃣ 장르 - 플랫폼 트리맵
st.subheader("🌳 장르와 플랫폼 관계 (트리맵)")
if 'Genre' in df_filtered.columns and 'Platform' in df_filtered.columns:
    tree_data = df_filtered.groupby(['Genre', 'Platform']).size().reset_index(name='count')
    fig_tree = px.treemap(tree_data, path=['Genre', 'Platform'], values='count', color='count', color_continuous_scale='Aggrnyl', title='장르별 플랫폼 분포')
    st.plotly_chart(fig_tree, use_container_width=True)

# 5️⃣ 산점도 (평점 vs 출시년도)
st.subheader("🎯 평점과 출시년도 관계")
fig_scatter = px.scatter(df_filtered, x='Release Year', y='User Rating', color='Genre', hover_data=['Game Name', 'Platform'], trendline='ols', title='출시년도에 따른 평점 분포')
st.plotly_chart(fig_scatter, use_container_width=True)

# 6️⃣ 플랫폼별 평균 평점
st.subheader("🕹️ 플랫폼별 평균 평점")
platform_rating = df_filtered.groupby('Platform')['User Rating'].mean().reset_index().sort_values(by='User Rating', ascending=False)
fig_platform = px.bar(platform_rating, x='Platform', y='User Rating', title='플랫폼별 평균 평점', color='User Rating', color_continuous_scale='RdYlGn')
st.plotly_chart(fig_platform, use_container_width=True)

# -------------------- 데이터 미리보기 및 다운로드 --------------------
st.markdown("---")
st.subheader("📋 필터링된 데이터 미리보기")
st.dataframe(df_filtered)

csv = df_filtered.to_csv(index=False)
st.download_button(
    label="💾 CSV 파일로 다운로드",
    data=csv,
    file_name='filtered_games.csv',
    mime='text/csv'
)

# -------------------- 푸터 --------------------
st.markdown("---")
st.caption("Made with ❤️ by Streamlit + Plotly | 데이터 분석 연습용 예제입니다.")
