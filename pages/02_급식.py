import streamlit as st
import requests
import datetime
import re
import pytz

API_URL = "https://open.neis.go.kr/hub/mealServiceDietInfo"
KEY = st.secrets['API_KEY']
education_office_code = "J10"
school_code = "7531050"

# 한국 시간대 (KST, UTC+9) 설정
kst = pytz.timezone('Asia/Seoul')
now = datetime.datetime.now(kst)
current_time = now.time()
today_str = now.strftime("%Y%m%d")
# 한국어 요일 리스트
days_korean = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']

# 현재 요일 계산
current_day_korean = days_korean[now.weekday()]

# 오후 2시 이후 체크
is_after_2pm = current_time >= datetime.time(14, 0, 0)

if is_after_2pm:
    tomorrow = now + datetime.timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y%m%d")
else:
    tomorrow_str = today_str

meal_code = "2"  # 중식

st.title("🍴 오늘의 급식")
# 현재 시각과 요일 출력
st.write(f"현재 시각 : {now.strftime('%Y년 %m월 %d일')} ({current_day_korean}) {now.strftime('%H:%M')}")

def get_meal_data(date_str):
    params = {
        "KEY": KEY,
        "Type": "json",
        "ATPT_OFCDC_SC_CODE": education_office_code,
        "SD_SCHUL_CODE": school_code,
        "MLSV_YMD": date_str,
        "MMEAL_SC_CODE": meal_code
    }
    try:
        response = requests.get(API_URL, params=params)
        if response.status_code != 200:
            st.error(f"API 요청 실패: {response.status_code}")
            return None
        data = response.json()
        if "mealServiceDietInfo" in data:
            meal_data = data["mealServiceDietInfo"][1]["row"]
            for meal in meal_data:
                if meal.get("MLSV_YMD") == date_str:
                    meal_items = re.sub(r'\(.*?\)', '', meal.get("DDISH_NM", ""))
                    return meal_items.replace('<br/>', '\n')
            return "급식 정보가 없습니다."
        return "API 요청 오류: 데이터 구조가 예상과 다릅니다."
    except Exception as e:
        st.error(f"오류 발생: {e}")
        return None

meal_info = get_meal_data(tomorrow_str if is_after_2pm else today_str)

if meal_info:
    st.markdown("<h2 style='font-size: 36px; font-weight: bold;'>🍽️   M  E  N  U   🍱</h2>", unsafe_allow_html=True)

    # 다크모드와 라이트모드를 위한 CSS 추가
    st.markdown(
        """
        <style>
        .meal-item {
            background-color: #f0f0f0;
            color: black;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
        }
        @media (prefers-color-scheme: dark) {
            .meal-item {
                background-color: #333333;
                color: white;
            }
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

    # 급식 항목 출력
    meal_items = meal_info.split('\n')
    heart_emoji = "❤️ "
    for item in meal_items:
        st.markdown(f"<div class='meal-item'>{heart_emoji}{item}</div>", unsafe_allow_html=True)
else:
    st.error("급식 정보를 불러올 수 없습니다.")

st.write("made by 시래기T")
