import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="주민등록 인구 및 세대 현황", page_icon="🏙️", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("202509_202509_주민등록인구및세대현황_월간.csv", encoding="cp949")

    # 🔹 숫자형 컬럼 자동 정리: 쉼표/공백 제거 후 float로 변환
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

# 주요 컬럼 탐색
region_col = next((c for c in df.columns if "행정구역" in c), df.columns[0])
pop_col = next((c for c in df.columns if "인구" in c and "총" in c), df.columns[-1])
house_col = next((c for c in df.columns if "세대" in c), None)

# 필터 설정
regions = df[region_col].unique()
selected_regions = st.sidebar.multiselect("📍 행정구역 선택", options=regions, default=regions[:10])
filtered_df = df[df[region_col].isin(selected_regions)]

# ✅ 숫자형 보정 (혹시 object 남아있을 경우 대비)
filtered_df[pop_col] = pd.to_numeric(filtered_df[pop_col], errors="coerce").fillna(0)
if house_col:
    filtered_df[house_col] = pd.to_numeric(filtered_df[house_col], errors="coerce").fillna(0)

# 요약 통계
st.subheader("📋 주요 통계 요약")
total_pop = int(filtered_df[pop_col].sum())
total_house = int(filtered_df[house_col].sum()) if house_col else 0

col1, col2 = st.columns(2)
col1.metric("총 인구 수", f"{total_pop:,} 명")
if house_col:
    col2.metric("총 세대 수", f"{total_house:,} 세대")

# 시각화 (아래 부분은 그대로)
st.markdown("### 👨‍👩‍👧‍👦 지역별 인구 수 비교")
fig_bar = px.bar(filtered_df, x=region_col, y=pop_col, color=region_col, text=pop_col)
fig_bar.update_traces(texttemplate="%{text:,}", textposition="outside")
st.plotly_chart(fig_bar, use_container_width=True)

