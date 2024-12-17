import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib

st.title("📊 우리 동네 인구 구조 탐험하기")
st.write("CSV 파일을 기반으로 지역별 인구 구조를 분석하고 그래프로 시각화합니다!")

# CSV 파일 읽기
uploaded_file = "/mnt/data/age2411.csv"  # 업로드된 파일 경로

@st.cache
def load_data(file_path):
    return pd.read_csv(file_path, encoding="utf-8")

# 데이터 불러오기
try:
    data = load_data(uploaded_file)
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 지역 선택
st.write("아래에서 지역명을 선택하세요:")
region = st.selectbox("지역을 선택하세요", data["지역명"].unique())

if region:
    # 선택한 지역의 데이터 필터링
    region_data = data[data["지역명"] == region]

    # 인구 데이터 준비
    age_columns = [col for col in data.columns if col.startswith("연령")]
    age_data = region_data[age_columns].T
    age_data.columns = ["인구수"]
    age_data["연령대"] = age_data.index.str.extract("연령(\d+세~\d+세)").fillna("기타")
    
    # 그래프 생성
    st.write(f"### {region}의 인구 구조")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(age_data["연령대"], age_data["인구수"], color="skyblue")
    ax.set_xlabel("인구수")
    ax.set_ylabel("연령대")
    ax.set_title(f"{region}의 인구 구조")
    st.pyplot(fig)

    st.success("인구 구조 분석 완료! 원하는 지역의 다른 데이터를 확인해보세요.")
