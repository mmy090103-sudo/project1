# streamlit_games_visualization.py
# 🌌 한국어/우주 테마 고급 Streamlit 대시보드
# - 보기 쉬운 막대/라인/파이 차트 중심
# - 게임명 한글 매핑(자주 쓰이는 타이틀), 검색, 필터, 상위 순위(상위 25)
# - Plotly (plotly.express, graph_objects) 사용

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="🌌 게임 데이터 대시보드 (한글)", layout="wide")

# -------------------- 스타일 (우주 테마) --------------------
page_bg = """
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 10% 10%, #071029 0%, #081229 30%, #000014 100%);
    color: #e6eef8;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#071029,#0b1a2b);
}
h1, h2, h3, h4, h5, h6 { color: #f0f6ff; font-family: 'Pretendard', sans-serif; }
.stButton>button { background-color: #0ea5e9; }
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# -------------------- 데이터 불러오기 --------------------
@st.cache_data(show_spinner=True)
def load_data(path: str = 'games_dataset.csv') -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.rename(columns=lambda x: x.strip())
    # 안전한 타입 변환
    if 'User Rating' in df.columns:
        df['User Rating'] = pd.to_numeric(df['User Rating'], errors='coerce')
    if 'Release Year' in df.columns:
        df['Release Year'] = pd.to_numeric(df['Release Year'], errors='coerce').astype('Int64')
    return df

try:
    df = load_data()
except Exception as e:
    st.error("❌ 데이터 파일을 찾을 수 없습니다. 'games_dataset.csv'가 앱 폴더에 있는지 확인하거나 사이드바에서 업로드해주세요.")
    uploaded = st.sidebar.file_uploader("CSV 업로드 (선택)", type=['csv'])
    if uploaded is not None:
        df = load_data(uploaded)
    else:
        st.stop()

# -------------------- 한글 매핑 (영문 -> 한국어) --------------------
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
    'PlayerUnknown\'s Battlegrounds': '배틀그라운드',
    'The Witcher 3: Wild Hunt': '위쳐 3: 와일드 헌트',
}

# 매핑 함수
def map_korean_name(name: str) -> str:
    if pd.isna(name):
        return name
    return KOREAN_NAME_MAP.get(name, name)

if 'Game Name' in df.columns:
    df['Game Name KR'] = df['Game Name'].apply(map_korean_name)
else:
    df['Game Name'] = df.index.astype(str)
    df['Game Name KR'] = df['Game Name']

# -------------------- 사이드바: 필터 및 업로드 --------------------
st.sidebar.header('🔎 데이터 옵션')
uploaded = st.sidebar.file_uploader('CSV 업로드 (선택)', type=['csv'])
if uploaded is not None:
    df = load_data(uploaded)
    df['Game Name KR'] = df['Game Name'].apply(map_korean_name)

# 필터 UI
st.sidebar.header('🎮 필터')
min_year = int(df['Release Year'].min())
max_year = int(df['Release Year'].max())
year_range = st.sidebar.slider('출시 연도', min_year, max_year, (min_year, max_year), step=1)

genres = ['전체'] + sorted(df['Genre'].dropna().unique().tolist())
platforms = ['전체'] + sorted(df['Platform'].dropna().unique().tolist())
selected_genres = st.sidebar.multiselect('장르', genres, default=['전체'])
selected_platforms = st.sidebar.multiselect('플랫폼', platforms, default=['전체'])

rating_min = float(df['User Rating'].min())
rating_max = float(df['User Rating'].max())
rating_range = st.sidebar.slider('평점 범위', rating_min, rating_max, (rating_min, rating_max))

# 필터 적용
df_filtered = df[(df['Release Year'] >= year_range[0]) & (df['Release Year'] <= year_range[1])]
if '전체' not in selected_genres:
    df_filtered = df_filtered[df_filtered['Genre'].isin(selected_genres)]
if '전체' not in selected_platforms:
    df_filtered = df_filtered[df_filtered['Platform'].isin(selected_platforms)]
df_filtered = df_filtered[(df_filtered['User Rating'] >= rating_range[0]) & (df_filtered['User Rating'] <= rating_range[1])]

# -------------------- 상단 요약 카드 --------------------
st.title('🌌 게임 데이터 대시보드 (한글화 및 간편 시각화)')
st.markdown('---')
col1, col2, col3, col4 = st.columns(4)
col1.metric('총 게임 수', f"{len(df_filtered):,}")
col2.metric('평균 평점', f"{df_filtered['User Rating'].mean():.2f}")
col3.metric('연도 범위', f"{df_filtered['Release Year'].min()} - {df_filtered['Release Year'].max()}")
col4.metric('장르 수', f"{df_filtered['Genre'].nunique()}")

# -------------------- 검색 기능 --------------------
st.markdown('### 🔍 게임 검색')
search_text = st.text_input('게임 이름으로 검색 (영문/한글 모두 가능)', '')
if search_text:
    mask = df_filtered['Game Name'].str.contains(search_text, case=False, na=False) | df_filtered['Game Name KR'].str.contains(search_text, case=False, na=False)
    search_results = df_filtered[mask]
    st.write(f'검색 결과: {len(search_results)}개')
    st.dataframe(search_results[['Game Name KR','Game Name','Genre','Platform','Release Year','User Rating']])

st.markdown('---')

# -------------------- 1) 장르별 평균 평점 (막대) --------------------
st.header('1️⃣ 장르별 평균 평점')
genre_avg = df_filtered.groupby('Genre', dropna=False)['User Rating'].agg(['mean','count']).reset_index().sort_values('mean', ascending=False)
fig_genre = px.bar(genre_avg, x='mean', y='Genre', orientation='h', text='mean',
                   labels={'mean':'평균 평점','Genre':'장르','count':'게임 수'},
                   title='장르별 평균 사용자 평점 (내림차순)')
fig_genre.update_traces(texttemplate='%{text:.2f}', textposition='outside')
fig_genre.update_layout(template='plotly_dark', margin=dict(l=150))
st.plotly_chart(fig_genre, use_container_width=True)

# -------------------- 2) 플랫폼별 게임 수 (막대) --------------------
st.header('2️⃣ 플랫폼별 게임 수')
plat_count = df_filtered['Platform'].value_counts().reset_index()
plat_count.columns = ['Platform','Count']
fig_plat = px.bar(plat_count, x='Platform', y='Count', text='Count', title='플랫폼별 게임 수', labels={'Count':'게임 수'})
fig_plat.update_traces(textposition='outside')
fig_plat.update_layout(template='plotly_dark', xaxis_tickangle=-45)
st.plotly_chart(fig_plat, use_container_width=True)

# -------------------- 3) 연도별 평균 평점 (라인) --------------------
st.header('3️⃣ 연도별 평균 평점 추이')
year_avg = df_filtered.groupby('Release Year')['User Rating'].mean().reset_index()
fig_year = go.Figure()
fig_year.add_trace(go.Scatter(x=year_avg['Release Year'], y=year_avg['User Rating'], mode='lines+markers', name='평균 평점', line=dict(color='#7dd3fc', width=3)))
fig_year.update_layout(title='출시 연도별 평균 사용자 평점', xaxis_title='출시 연도', yaxis_title='평균 평점', template='plotly_dark')
st.plotly_chart(fig_year, use_container_width=True)

# -------------------- 4) 상위 N 게임 (평점 기준, 막대) --------------------
st.header('4️⃣ 상위 게임 순위 (평점 기준)')
TOP_N = 25
top_n = df_filtered.sort_values(by='User Rating', ascending=False).head(TOP_N).copy()
# 한글명 칼럼 사용
if 'Game Name KR' in top_n.columns:
    top_n['label'] = top_n['Game Name KR']
else:
    top_n['label'] = top_n['Game Name']

fig_top = px.bar(top_n[::-1], x='User Rating', y='label', orientation='h', text='User Rating', title=f'상위 {TOP_N}개 게임 (평점 기준)')
fig_top.update_traces(texttemplate='%{text:.2f}', textposition='outside')
fig_top.update_layout(template='plotly_dark', margin=dict(l=220))
st.plotly_chart(fig_top, use_container_width=True)

# -------------------- 5) 파이 차트: 장르 비율 --------------------
st.header('5️⃣ 장르 비율')
genre_share = df_filtered['Genre'].value_counts().reset_index()
genre_share.columns = ['Genre','Count']
fig_pie = px.pie(genre_share, values='Count', names='Genre', title='장르별 비율 (퍼센트)')
fig_pie.update_traces(textposition='inside', textinfo='percent+label')
fig_pie.update_layout(template='plotly_dark')
st.plotly_chart(fig_pie, use_container_width=True)

# -------------------- 6) 데이터 요약 및 다운로드 --------------------
st.markdown('---')
st.header('📋 데이터 요약 및 다운로드')

# 요약 테이블
summary_table = df_filtered.groupby(['Genre']).agg(게임수=('Game Name','count'), 평균평점=('User Rating','mean')).reset_index().sort_values('평균평점', ascending=False)
st.dataframe(summary_table)

# 원본 컬럼 포함 미리보기
st.subheader('데이터 미리보기')
st.dataframe(df_filtered[['Game Name KR','Game Name','Genre','Platform','Release Year','User Rating']].rename(columns={'Game Name KR':'게임명(한글)','Game Name':'게임명(원본)','User Rating':'평점'}))

# 다운로드
csv = df_filtered.to_csv(index=False).encode('utf-8-sig')
st.download_button(label='💾 필터 결과 CSV 다운로드', data=csv, file_name='filtered_games_korean.csv', mime='text/csv')

# -------------------- 추가 기능: 사용자가 매핑 추가하기 --------------------
st.markdown('---')
st.header('🔧 게임명 한글 매핑 추가 (선택)')
with st.expander('직접 한글명 추가 / 수정'):
    st.write('영문 게임명과 한글명을 입력하면 현재 세션에서 매핑이 적용됩니다. (영구 저장은 GitHub 레포에 매핑 파일을 추가하세요)')
    eng = st.text_input('영문 게임명')
    kor = st.text_input('한글 게임명')
    if st.button('매핑 추가/적용'):
        if eng and kor:
            KOREAN_NAME_MAP[eng] = kor
            df['Game Name KR'] = df['Game Name'].apply(map_korean_name)
            st.success(f'매핑 추가됨: "{eng}" → "{kor}"')
        else:
            st.error('영문과 한글명을 모두 입력하세요.')

st.markdown('---')
st.caption('Made with ❤️ · 우주 테마 버전 · 한글 매핑 포함')
