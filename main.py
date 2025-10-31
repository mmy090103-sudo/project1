import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------
# ⚙️ 기본 페이지 설정
# -------------------------------
st.set_page_config(
    page_title="대한민국 인구 및 세대 현황 분석 대시보드",
    page_icon="📊",
    layout="wide",
)

st.title("📊 대한민국 인구 및 세대 현황 분석 대시보드")
st.markdown("""
이 대시보드는 **행정안전부 주민등록 인구 및 세대 현황 데이터**를 바탕으로  
지역별 인구 구조를 시각화하고 통계적으로 탐색할 수 있도록 제작되었습니다.  
데이터는 월간 기준이며, **Plotly**를 사용해 동적이고 직관적인 시각화를 제공합니다.
""")

# -------------------------------
# 📂 데이터 불러오기 & 전처리
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("202509_202509_주민등록인구및세대현황_월간.csv", encoding="cp949")

    # 🔹 문자열 숫자 정리 (쉼표, 공백 등 제거)
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("-", "0", regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="ignore")
    return df

df = load_data()

# -------------------------------
# 🔍 주요 컬럼 자동 탐색
# -------------------------------
region_col = next((c for c in df.columns if "행정구역" in c), df.columns[0])
pop_col = next((c for c in df.columns if "총인구" in c or "총 인구" in c), df.columns[-1])
male_col = next((c for c in df.columns if "남" in c and "인구" in c), None)
female_col = next((c for c in df.columns if "여" in c and "인구" in c), None)
house_col = next((c for c in df.columns if "세대" in c), None)

# -------------------------------
# 🧭 사이드바 설정
# -------------------------------
st.sidebar.header("⚙️ 설정 패널")

regions = df[region_col].unique().tolist()
selected_regions = st.sidebar.multiselect("📍 행정구역 선택", regions, default=regions[:8])

# 숫자형 보정
df[pop_col] = pd.to_numeric(df[pop_col], errors="coerce").fillna(0)
if house_col:
    df[house_col] = pd.to_numeric(df[house_col], errors="coerce").fillna(0)

filtered_df = df[df[region_col].isin(selected_regions)]

# -------------------------------
# 🧮 핵심 요약 지표
# -------------------------------
st.subheader("📈 주요 요약 통계")

total_pop = int(filtered_df[pop_col].sum())
total_house = int(filtered_df[house_col].sum()) if house_col else 0
avg_pop = int(filtered_df[pop_col].mean())

col1, col2, col3 = st.columns(3)
col1.metric("총 인구 수", f"{total_pop:,} 명")
col2.metric("평균 인구 수(선택 지역)", f"{avg_pop:,} 명")
if house_col:
    col3.metric("총 세대 수", f"{total_house:,} 세대")

st.markdown("---")

# -------------------------------
# 📊 인구 수 비교 막대그래프
# -------------------------------
st.markdown("### 👨‍👩‍👧‍👦 지역별 인구 비교")

fig_bar = px.bar(
    filtered_df.sort_values(by=pop_col, ascending=False),
    x=region_col,
    y=pop_col,
    color=pop_col,
    color_continuous_scale="tealgrn",
    text=pop_col,
    title="지역별 총인구수 비교",
)
fig_bar.update_layout(
    template="plotly_white",
    xaxis_title="행정구역",
    yaxis_title="인구 수",
    height=550,
)
fig_bar.update_traces(texttemplate="%{text:,}", textposition="outside")
st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------------
# 👥 성별 인구 비교 (존재 시)
# -------------------------------
if male_col and female_col:
    st.markdown("### ⚧️ 성별 인구 분포")

    sex_df = filtered_df.melt(
        id_vars=[region_col],
        value_vars=[male_col, female_col],
        var_name="성별",
        value_name="인구 수"
    )

    fig_sex = px.bar(
        sex_df,
        x=region_col,
        y="인구 수",
        color="성별",
        barmode="group",
        color_discrete_map={male_col: "#4C78A8", female_col: "#F58518"},
        title="성별 인구 비교",
    )
    fig_sex.update_layout(template="plotly_white", height=500)
    st.plotly_chart(fig_sex, use_container_width=True)

# -------------------------------
# 🏠 세대수 비교
# -------------------------------
if house_col:
    st.markdown("### 🏠 지역별 세대 수")

    fig_house = px.bar(
        filtered_df.sort_values(by=house_col, ascending=False),
        x=region_col,
        y=house_col,
        color=house_col,
        color_continuous_scale="Viridis",
        text=house_col,
        title="지역별 세대 수 비교",
    )
    fig_house.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig_house.update_layout(template="plotly_white", height=550)
    st.plotly_chart(fig_house, use_container_width=True)

# -------------------------------
# 🥧 인구 비율 파이차트
# -------------------------------
st.markdown("### 🥧 인구 비율 (선택 지역 기준)")

fig_pie = px.pie(
    filtered_df,
    names=region_col,
    values=pop_col,
    color_discrete_sequence=px.colors.sequential.Tealgrn,
    hole=0.4,
    title="지역별 인구 비율",
)
fig_pie.update_layout(template="plotly_white", height=550)
st.plotly_chart(fig_pie, use_container_width=True)

# -------------------------------
# 🗺️ 지도 시각화
# -------------------------------
st.markdown("### 🗺️ 전국 인구 분포 지도")

try:
    fig_map = px.choropleth(
        filtered_df,
        geojson="https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2013/json/skorea_municipalities_geo_simple.json",
        locations=region_col,
        featureidkey="properties.name",
        color=pop_col,
        color_continuous_scale="YlGnBu",
        title="대한민국 지역별 인구 분포 지도",
    )
    fig_map.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig_map, use_container_width=True)
except Exception:
    st.warning("⚠️ 지도 표시가 불가능합니다. (행정구역 이름이 매칭되지 않을 수 있습니다)")

# -------------------------------
# ⏱️ 인구 변화 추이 (시간 컬럼 존재 시)
# -------------------------------
time_cols = [c for c in df.columns if "월" in c or "시점" in c or "연도" in c]
if time_cols:
    st.markdown("### ⏱️ 시간별 인구 변화 (추이 분석)")
    time_col = time_cols[0]
    time_df = df.groupby(time_col)[pop_col].sum().reset_index()

    fig_line = px.line(
        time_df,
        x=time_col,
        y=pop_col,
        markers=True,
        title="월별 총 인구 변화 추이",
        color_discrete_sequence=["#008080"],
    )
    fig_line.update_layout(template="plotly_white", height=500)
    st.plotly_chart(fig_line, use_container_width=True)

# -------------------------------
# 💾 데이터 다운로드
# -------------------------------
st.markdown("### 💾 데이터 다운로드")
csv = filtered_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="📥 선택된 데이터 다운로드 (CSV)",
    data=csv,
    file_name="filtered_population_data.csv",
    mime="text/csv",
)

# -------------------------------
# 📋 데이터 테이블
# -------------------------------
st.markdown("### 📋 세부 데이터 보기")
st.dataframe(filtered_df, use_container_width=True, height=500)

# -------------------------------
# 📘 푸터
# -------------------------------
st.markdown("---")
st.caption("© 2025 대한민국 행정안전부 데이터 기반 | Visualization by Streamlit + Plotly")
