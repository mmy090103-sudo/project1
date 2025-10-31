import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="📊 주민등록 인구 및 세대 현황 시각화", layout="wide")

# -------------------------------
# 데이터 불러오기
# -------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("202509_202509_주민등록인구및세대현황_월간.csv", encoding="cp949")
    except:
        df = pd.read_csv("202509_202509_주민등록인구및세대현황_월간.csv", encoding="utf-8")
    return df

df = load_data()
st.title("📈 주민등록 인구 및 세대 현황 시각화 대시보드")

# -------------------------------
# 데이터 기본 구조 확인
# -------------------------------
with st.expander("데이터 미리보기"):
    st.write(df.head())
    st.write(f"데이터 크기: {df.shape[0]} 행 × {df.shape[1]} 열")

# -------------------------------
# 컬럼 자동 탐색
# -------------------------------
cols = df.columns.tolist()
time_col = next((c for c in cols if "연도" in c or "기간" in c or "월" in c), cols[0])
region_col = next((c for c in cols if "행정구역" in c or "시도" in c), cols[1])
pop_col = next((c for c in cols if "인구" in c or "세대" in c), cols[-1])

# -------------------------------
# 필터 사이드바
# -------------------------------
st.sidebar.header("🔍 필터 설정")

regions = st.sidebar.multiselect(
    "지역 선택", df[region_col].unique().tolist(),
    default=df[region_col].unique()[:5]
)

st.sidebar.markdown("---")
chart_type = st.sidebar.selectbox(
    "📊 시각화 종류 선택",
    ["📈 선 그래프", "📊 막대 그래프", "🥧 파이 차트", "🌍 지도 시각화"]
)

# -------------------------------
# 필터링
# -------------------------------
filtered_df = df[df[region_col].isin(regions)]

# -------------------------------
# 인구 합계 및 주요 통계
# -------------------------------
if pd.api.types.is_numeric_dtype(df[pop_col]):
    total_pop = int(filtered_df[pop_col].sum())
else:
    filtered_df[pop_col] = (
        filtered_df[pop_col].astype(str)
        .str.replace(",", "")
        .astype(float)
    )
    total_pop = int(filtered_df[pop_col].sum())

st.markdown(f"### 💡 선택한 지역 총 인구: **{total_pop:,}명**")

# -------------------------------
# 시각화 섹션
# -------------------------------
st.subheader("📉 인구 변화 추이")

# 1️⃣ 선 그래프
if "선" in chart_type:
    fig = px.line(
        filtered_df,
        x=time_col,
        y=pop_col,
        color=region_col,
        title="지역별 인구 추이",
        markers=True
    )
    fig.update_traces(line=dict(width=3))
    st.plotly_chart(fig, use_container_width=True)

# 2️⃣ 막대 그래프
elif "막대" in chart_type:
    fig = px.bar(
        filtered_df,
        x=region_col,
        y=pop_col,
        color=region_col,
        title="지역별 인구 비교",
        barmode="group"
    )
    st.plotly_chart(fig, use_container_width=True)

# 3️⃣ 파이 차트
elif "파이" in chart_type:
    fig = px.pie(
        filtered_df.groupby(region_col, as_index=False)[pop_col].sum(),
        names=region_col,
        values=pop_col,
        title="지역별 인구 비율"
    )
    fig.update_traces(textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

# 4️⃣ 지도 시각화
elif "지도" in chart_type:
    st.warning("🗺️ 지도 시각화는 지역명이 좌표 정보와 연결될 경우만 가능합니다.")
    st.map()

# -------------------------------
# 시간대별 분석
# -------------------------------
st.subheader("⏰ 월별 총 인구 추이 (전국 기준)")

time_df = df.groupby(time_col, as_index=False)[pop_col].sum()
fig_time = px.line(
    time_df,
    x=time_col,
    y=pop_col,
    title="전국 월별 인구 변화",
    markers=True
)
st.plotly_chart(fig_time, use_container_width=True)

# -------------------------------
# 상관관계 분석 (추가 기능)
# -------------------------------
st.subheader("📈 변수 간 상관관계 분석")
numeric_df = df.select_dtypes(include=['number'])
if len(numeric_df.columns) > 1:
    corr = numeric_df.corr()
    fig_corr = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        title="수치형 컬럼 간 상관관계 Heatmap"
    )
    st.plotly_chart(fig_corr, use_container_width=True)
else:
    st.info("상관관계를 분석할 수 있는 수치형 데이터가 부족합니다.")

# -------------------------------
# 다운로드 기능
# -------------------------------
st.sidebar.download_button(
    label="📥 필터링된 데이터 다운로드 (CSV)",
    data=filtered_df.to_csv(index=False).encode("utf-8-sig"),
    file_name="filtered_population.csv",
    mime="text/csv"
)

st.sidebar.markdown("---")
st.sidebar.info("Made with ❤️ by Streamlit + Plotly")


