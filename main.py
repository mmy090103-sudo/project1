import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# 데이터 불러오기
# -------------------------------
@st.cache_data
def load_data():
    # 파일 이름 변경 시 아래 경로 수정
    df = pd.read_csv("202509_202509_주민등록인구및세대현황_월간.csv", encoding="cp949")
    return df

df = load_data()

st.title("📈 주민등록 인구 및 세대 현황 대시보드")
st.markdown("출처: 행정안전부 | 데이터 시각화: Plotly + Streamlit")

# -------------------------------
# 데이터 확인
# -------------------------------
st.subheader("데이터 미리보기")
st.dataframe(df.head(20))

# -------------------------------
# 컬럼 선택
# -------------------------------
columns = df.columns.tolist()

# '행정구역', '총인구수', '세대수' 등 주요 컬럼 이름 자동 탐색
region_col = next((c for c in columns if "행정구역" in c), columns[0])
pop_col = next((c for c in columns if "인구" in c), columns[-1])
house_col = next((c for c in columns if "세대" in c), None)

# -------------------------------
# 필터 기능
# -------------------------------
regions = df[region_col].unique()
selected_regions = st.multiselect("📍 행정구역 선택", regions, default=regions[:5])

filtered_df = df[df[region_col].isin(selected_regions)]

# -------------------------------
# 시각화 ① : 지역별 인구 수 막대그래프
# -------------------------------
st.subheader("👨‍👩‍👧‍👦 지역별 인구 수 비교")

fig1 = px.bar(
    filtered_df,
    x=region_col,
    y=pop_col,
    color=region_col,
    title="지역별 인구수 비교",
    text=pop_col,
)
fig1.update_traces(texttemplate="%{text:,}", textposition="outside")
st.plotly_chart(fig1, use_container_width=True)

# -------------------------------
# 시각화 ② : 세대수 비교 (존재 시)
# -------------------------------
if house_col:
    st.subheader("🏠 지역별 세대수 비교")
    fig2 = px.bar(
        filtered_df,
        x=region_col,
        y=house_col,
        color=region_col,
        title="지역별 세대수 비교",
        text=house_col,
    )
    fig2.update_traces(texttemplate="%{text:,}", textposition="outside")
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# 시각화 ③ : 인구 비율 원형 차트
# -------------------------------
st.subheader("🥧 인구 비율 (선택된 지역 기준)")
fig3 = px.pie(
    filtered_df,
    names=region_col,
    values=pop_col,
    title="인구 비율 파이차트",
)
st.plotly_chart(fig3, use_container_width=True)

# -------------------------------
# 시각화 ④ : 지도 시각화 (행정구역 이름이 시·도 단위일 경우)
# -------------------------------
st.subheader("🗺️ 인구수 지도 시각화 (대한민국 기준)")
try:
    fig4 = px.choropleth(
        filtered_df,
        geojson="https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2013/json/skorea_municipalities_geo_simple.json",
        locations=region_col,
        featureidkey="properties.name",
        color=pop_col,
        color_continuous_scale="Viridis",
        title="지역별 인구 분포 지도",
    )
    fig4.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig4, use_container_width=True)
except Exception as e:
    st.info("지도를 표시할 수 없습니다. (행정구역 이름이 매칭되지 않을 수 있음)")

# -------------------------------
# 마무리
# -------------------------------
st.markdown("---")
st.markdown("✅ **Tip:** 좌측 상단의 ‘재실행’ 버튼으로 데이터를 다시 불러올 수 있습니다.")
