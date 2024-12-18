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

# 현재 날짜 및 시간 가져오기 (한국 시각 기준)
now = datetime.datetime.now(kst)
current_time = now.time()
year = now.year
month = str(now.month).zfill(2)  # 월을 두 자리로 포맷팅
day = str(now.day).zfill(2)  # 일을 두 자리로 포맷팅
today_str = f"{year}{month}{day}"  # YYYYMMDD 형식으로 현재 날짜 생성
week_days = ["월", "화", "수", "목", "금", "토", "일"]
day_of_week = now.weekday()  # 현재 요일 번호 (0: 월요일, 6: 일요일)

# 오후 2시 이후 체크
is_after_2pm = current_time >= datetime.time(14, 0, 0)

# 내일 날짜 계산
if is_after_2pm:
    tomorrow = now + datetime.timedelta(days=1)
    tomorrow_str = f"{tomorrow.year}{str(tomorrow.month).zfill(2)}{str(tomorrow.day).zfill(2)}"
    date_str = f"{str(tomorrow.month).zfill(2)}/{str(tomorrow.day).zfill(2)} ({week_days[tomorrow.weekday()]})"
else:
    tomorrow_str = today_str
    date_str = f"{month}/{day} ({week_days[day_of_week]})"

# 식사 코드 (중식)
meal_code = "2"  # 2는 "중식"을 의미

# Streamlit UI 설정
st.title("✨ 오늘의 급식")

# st.write(f"현재 시각 : {now.strftime('%Y-%m-%d %H:%M:%S')} ({week_days[day_of_week]})")  # 한국어 요일 추가

# 급식 정보 가져오기 함수
def get_meal_data(date_str):
    params = {
        "KEY": KEY,
        "Type": "json",
        "ATPT_OFCDC_SC_CODE": education_office_code,  # 시도교육청 코드
        "SD_SCHUL_CODE": school_code,  # 행정표준코드
        "MM": month,  # 월
        "DD": day,  # 일
        "YY": year,  # 년
        "MLSV_YMD": date_str,  # 날짜 (MLSV_YMD) 추가
        "MMEAL_SC_CODE": meal_code  # 식사 코드
    }

    try:
        # API 호출
        response = requests.get(API_URL, params=params)
        
        # 응답 상태 코드 체크
        if response.status_code != 200:
            st.error(f"API 요청에 실패했습니다. 상태 코드: {response.status_code}")
            return None
        
        # 응답 데이터 확인
        data = response.json()

        # 급식 정보가 정상적으로 반환되었는지 확인
        if "mealServiceDietInfo" in data:
            meal_data = data["mealServiceDietInfo"][1]["row"]
            if meal_data:
                # 급식 날짜에 해당하는 요리명만 추출
                for meal in meal_data:
                    meal_date = meal.get("MLSV_YMD")  # 급식 정보의 날짜
                    if meal_date == date_str:  # 날짜와 비교
                        meal_name = meal.get("DDISH_NM", "요리명 정보 없음")

                        # 1. <br/> 태그를 기준으로 나누고, 괄호 안 숫자 제거
                        meal_items = meal_name.split('<br/>')
                        clean_meal_items = []

                        for item in meal_items:
                            # 괄호와 그 안의 숫자 제거하는 정규 표현식
                            cleaned_item = re.sub(r'\(.*?\)', '', item).strip()  # 괄호 안의 숫자 삭제
                            clean_meal_items.append(cleaned_item)

                        # 2. 보기 좋은 형태로 나열
                        return '\n'.join(clean_meal_items)  # 각 항목을 새 줄로 구분해서 반환
                return "급식 정보가 없습니다."
            else:
                return "급식 정보가 없습니다."
        else:
            return "API 요청에 오류가 발생했습니다. 응답 데이터 구조가 예상과 다릅니다."
    except Exception as e:
        # 예외 처리
        st.error(f"오류 발생: {e}")
        return None

# 급식 정보 출력
if is_after_2pm:
    st.write("오늘 급식은 끝났으니 내일의 급식 정보를 보여드립니다 :D")
    meal_info = get_meal_data(tomorrow_str)
else:
    st.write("오늘의 급식입니다. 맛점 :D")
    meal_info = get_meal_data(today_str)

# 하트 이모지 리스트
heart_emoji_list = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎"]

# 다크모드와 라이트모드를 위한 CSS 추가
st.markdown(
    """
    <style>
    .meal-item {
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 5px;
        text-align: center;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    /* 기본 라이트 모드 스타일 */
    body {
        background-color: #ffffff;
        color: black;
    }
    /* 다크 모드 스타일 */
    @media (prefers-color-scheme: dark) {
        body {
            background-color: #121212;
            color: white;
        }
        .meal-item {
            background-color: #333333;
            color: white;
        }
    }
    /* 라이트 모드에서의 meal-item 스타일 */
    @media (prefers-color-scheme: light) {
        .meal-item {
            background-color: #f0f0f0;
            color: black;
        }
    }
    </style>
    """, 
    unsafe_allow_html=True
)

if meal_info:
    st.markdown(
        f"<h2 style='font-size: 36px; font-weight: bold; text-align: center;'>🍴   {date_str}   🍱</h2>", 
        unsafe_allow_html=True
    )
    # 급식 항목 출력
    meal_items = meal_info.split('\n')

    # 하트 이모지와 함께 급식 항목을 출력
    for i, item in enumerate(meal_items):
        heart_emoji = heart_emoji_list[i % len(heart_emoji_list)]  # 리스트 길이에 맞게 순서대로 하트 이모지 선택
        st.markdown(
            f"<div class='meal-item'>"
            f"<span>{heart_emoji}</span><span>{item}</span><span>{heart_emoji}</span>"
            f"</div>", 
            unsafe_allow_html=True
        )

st.markdown(
    "<p style='color: grey; font-style: italic; margin-top: 10px; text-align: right;'>made by 시래기T</p>",
    unsafe_allow_html=True
)

