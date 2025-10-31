# streamlit_games_visualization.py
# 🌌 한글 버전 고급 Streamlit 대시보드 (우주 테마)
# 보기 좋은 Plotly 그래프, 게임 순위 표시, 다채로운 시각화 포함

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="🌌 게임 데이터 대시보드", layout="wide")

# -------------------- 스타일 (우주 테마) --------------------
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top, #0d1b2a, #1b263b, #000814);
    color: #e0e1dd;
}
[data-testid="stSidebar"] {
    background-color: #1b263b;
}
h1, h2, h3, h4, h5, h6 {
    color: #f5f6fa;
    font-family: 'Pretendard', sans-serif;
}
[data-testid="stMetricValue"] {
    color: #f5f6fa;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# -------------------- 데이터 로드 --------------------
@st.cache_data(show_spinner=True)
def load_data(path: str):
    df = pd.read_csv(path)
    df = df.rename(columns=lambda x: x.strip())
    df['User Rating'] = pd.to_numeric(df['User Rating'], errors='coerce')
    return df

try:
    df = load_data("games_dataset.csv")
except FileNotFoundError:
    st.error("❌ 'games_dataset.csv' 파일이 없습니다. 업로드 또는 경로 확인.")
    st.stop()

# -------------------- 사이드바 필터 --------------------
st.sidebar.title("🎮 필터 설정")

years = sorted(df['Release Year'].dropna().unique())
year_min, year_max = st.sidebar.select_slider(
    '출시 연도 범위', options=years, value=(min(years), max(years))
)

genres = ['전체'] + sorted(df['Genre'].dropna().unique())
platforms = ['전체'] + sorted(df['Platform'].dropna().unique())

selected_genres = st.sidebar.multiselect('장르 선택', genres, default=['전체'])
selected_platforms = st.sidebar.multiselect('플랫폼 선택', platforms, default=['전체'])

rating_min, rating_max = st.sidebar.slider('평점 범위', float(df['User Rating'].min()), float(df['User Rating'].max()), (float(df['User Rating'].min()), float(df['User Rating'].max())))

# 필터 적용
df_filtered = df[(df['Release Year'] >= year_min) & (df['Release Year'] <= year_max)]
if '전체' not in selected_genres:
    df_filtered = df_filtered[df_filtered['Genre'].isin(selected_genres)]
if '전체' not in selected_platforms:
    df_filtered = df_filtered[df_filtered['Platform'].isin(selected_platforms)]
df_filtered = df_filtered[(df_filtered['User Rating'] >= rating_min) & (df_filtered['User Rating'] <= rating_max)]

# -------------------- 메인 타이틀 --------------------
st.title("🌌 게임 데이터 분석 대시보드")
st.caption("Plotly + Streamlit 기반 인터랙티브 데이터 시각화")

# -------------------- 주요 통계 --------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("게임 수", f"{len(df_filtered):,}")
col2.metric("평균 평점", f"{df_filtered['User Rating'].mean():.2f}")
col3.metric("출시 연도", f"{df_filtered['Release Year'].min()} - {df_filtered['Release Year'].max()}")
col4.metric("장르 수", f"{df_filtered['Genre'].nunique()}")

st.markdown("---")

# -------------------- 상위 게임 순위 --------------------
st.subheader("🏆 최고 평점 게임 순위")
top_games = df_filtered.sort_values(by='User Rating', ascending=False).head(15).reset_index(drop=True)
top_games['순위'] = top_games.index + 1
fig_rank = px.bar(top_games, x='User Rating', y='Game Name', orientation='h', color='Genre', text='순위', title='상위 15개 게임 (평점 기준)')
fig_rank.update_traces(textposition='outside')
fig_rank.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_rank, use_container_width=True)

# -------------------- 평점 분포 --------------------
st.subheader("⭐ 평점 분포")
fig_hist = px.violin(df_filtered, y='User Rating', x='Genre', box=True, points='all', color='Genre', title='장르별 평점 분포', color_discrete_sequence=px.colors.qualitative.Dark2)
st.plotly_chart(fig_hist, use_container_width=True)

# -------------------- 출시연도 추이 --------------------
st.subheader("📈 연도별 게임 출시 추이")
count_by_year = df_filtered.groupby('Release Year').size().reset_index(name='게임 수')
fig_line = go.Figure()
fig_line.add_trace(go.Scatter(x=count_by_year['Release Year'], y=count_by_year['게임 수'], mode='lines+markers', line=dict(color='#00b4d8', width=3)))
fig_line.update_layout(title='연도별 게임 출시 추이', xaxis_title='출시 연도', yaxis_title='게임 수', template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig_line, use_container_width=True)

# -------------------- 장르 & 플랫폼 트리맵 --------------------
st.subheader("🌌 장르-플랫폼 트리맵")
if 'Genre' in df_filtered.columns and 'Platform' in df_filtered.columns:
    tree_data = df_filtered.groupby(['Genre', 'Platform']).size().reset_index(name='count')
    fig_tree = px.treemap(tree_data, path=['Genre', 'Platform'], values='count', color='count', color_continuous_scale='deep', title='장르별 플랫폼 분포')
    st.plotly_chart(fig_tree, use_container_width=True)

# -------------------- 평점 vs 출시연도 --------------------
st.subheader("🚀 출시연도와 평점 관계")
fig_scatter = px.scatter(df_filtered, x='Release Year', y='User Rating', color='Genre', hover_data=['Game Name', 'Platform'], title='출시년도에 따른 평점 관계')
fig_scatter.update_traces(marker=dict(size=10, line=dict(width=1, color='white')))
fig_scatter.update_layout(template='plotly_dark')
st.plotly_chart(fig_scatter, use_container_width=True)

# -------------------- 데이터 테이블 및 다운로드 --------------------
st.markdown("---")
st.subheader("📋 필터링된 데이터")
st.dataframe(df_filtered)

csv = df_filtered.to_csv(index=False)
st.download_button("💾 CSV로 저장", csv, "filtered_games.csv", "text/csv")

# -------------------- 푸터 --------------------
st.markdown("---")
st.caption("🌌 Made with ❤️ by Streamlit + Plotly | 우주 테마 버전 | 게임 데이터 시각화")
