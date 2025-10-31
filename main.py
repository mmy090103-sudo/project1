import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# 🔧 기본 설정
# -------------------------------
st.set_page_config(
    page_title="주민등록 인구 및 세대 현황 대시보드",
    page_icon="🏙️",
    layout="wide"
)

st.title("🏙️ 대한민국 주민등록 인구 및 세대 현황 대시보드")
st.markdown("""
이 대시보드는 행정안전부에서 제공하는 주민등록 인구 및 세대 데이터를 기반으로 합니다.  
**Plotly**를 활용해 지역별 인구 및 세대 현황을 시각적으로 탐색할 수 있습니다.
""")

# -------------------------------
# 📂 데이터 불러오기
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("202509_202509_주민등록인구및세대현황_월간.csv", encoding="cp949")
    return df

df = load_data()

# -------------------------------
# 📊 기본 정보
# -------------------------------
st.sidebar.header("⚙️ 필터 설정")

region_col = next((c for c in df.columns if "행정구역" in c), df.columns[0])
pop_col = next((c for c in df.columns if "인구" in c and "총" in c), df.columns[-1])
house_col = next((c for c in df.columns if "세대" in c), None)

regions = df[region_col].unique()
selected_regions = st.sidebar.multiselect(
    "📍 행정구역 선택",
    options=regions,
    default=regions[:10]
)

filtered_df = df[df[region_col].isin(selected_regions)]

st.sidebar.info(f"총 {len(filtered_df)}개 지역이 선택됨")

# -------------------------------
# 📈 주요 지표 요약
# -------------------------------
st.subheader("📋 주요 통계 요약")

total_pop = int(filtered_df[pop_col].sum())
total_house = int(filtered_df[house_col].sum()) if house_col else 0

col1, col2 = st.columns(2)
col1.metric(label="총 인구 수", value=f"{total_pop:,} 명")
if house_col:
    col2.metric(label="총 세대 수", value=f"{total_house:,} 세대")

# -------------------------------
# 🔹 인구수 막대그래프
# -------------------------------
st.markdown("### 👨‍👩‍👧‍👦 지역별 인구 수 비교")

fig_bar = px.bar(
    filtered_df.sort_values(by=pop_col, ascending=False),
    x=region_col,
    y=pop_col,
    text=pop_col,
    color=pop_col,
    color_continuous_scale="Tealgrn",
    title="지역별 인구수 막대그래프",
)
fig_bar.update_layout(
    xaxis_title="행정구역",
    yaxis_title="인구 수",
    template="plotly_white",
    height=550,
)
fig_bar.update_traces(texttemplate="%{text:,}", textposition="outside")
st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------------
# 🔹 세대수 비교 (존재 시)
# -------------------------------
if house_col:
    st.markdown("### 🏠 지역별 세대 수 비교")

    fig_house = px.bar(
        filtered_df.sort_values(by=house_col, ascending=False),
        x=region_col,
        y=house_col,
        text=house_col,
        color=house_col,
        color_continuous_scale="Viridis",
        title="지역별 세대수 막대그래프",
    )
    fig_house.update_layout(
        xaxis_title="행정구역",
        yaxis_title="세대 수",
        template="plotly_white",
        height=550,
    )
    fig_house.update_traces(texttemplate="%{text:,}", textposition="outside")
    st.plotly_chart(fig_house, use_container_width=True)

# -------------------------------
# 🔹 인구 비율 파이차트
# -------------------------------
st.markdown("### 🥧 지역별 인구 비율")

fig_pie = px.pie(
    filtered_df,
    names=region_col,
    values=pop_col,
    color_discrete_sequence=px.colors.sequential.Tealgrn,
    hole=0.4,
    title="선택된 지역의 인구 비율",
)
fig_pie.update_layout(template="plotly_white", height=550)
st.plotly_chart(fig_pie, use_container_width=True)

# -------------------------------
# 🔹 지도 시각화
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
        title="대한민국 지역별 인구 분포",
    )
    fig_map.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig_map, use_container_width=True)
except Exception as e:
    st.warning("⚠️ 지도 표시가 불가능합니다. (행정구역 이름 매칭 필요)")

# -------------------------------
# 📑 데이터 표
# -------------------------------
st.markdown("### 📋 세부 데이터 보기")
st.dataframe(filtered_df, use_container_width=True)

# -------------------------------
# 푸터
# -------------------------------
st.markdown("---")
st.caption("© 2025 대한민국 행정안전부 | Visualization by Streamlit + Plotly")
