import streamlit as st
import requests
import datetime
import re
import pytz

API_URL = "https://open.neis.go.kr/hub/mealServiceDietInfo"
KEY = st.secrets['API_KEY']
WEEK_DAYS = ["월", "화", "수", "목", "금", "토", "일"]
MEAL_CODE_LUNCH = "2"


def get_kst_now():
    """현재 한국 표준시 반환"""
    kst = pytz.timezone('Asia/Seoul')
    return datetime.datetime.now(kst)


@st.cache_data(ttl="12h")
def get_meal_data(date_str, office_code, sch_code):
    """일간 급식 조회 (12시간 캐싱)"""
    params = {
        "KEY": KEY,
        "Type": "json",
        "ATPT_OFCDC_SC_CODE": office_code,
        "SD_SCHUL_CODE": sch_code,
        "MLSV_YMD": date_str,
        "MMEAL_SC_CODE": MEAL_CODE_LUNCH,
    }
    try:
        response = requests.get(API_URL, params=params)
        if response.status_code != 200:
            return None
        data = response.json()
        if "mealServiceDietInfo" not in data:
            return None
        for meal in data["mealServiceDietInfo"][1]["row"]:
            if meal.get("MLSV_YMD") == date_str:
                meal_name = meal.get("DDISH_NM", "")
                return [
                    re.sub(r'\(.*?\)', '', item).strip()
                    for item in meal_name.split('<br/>')
                    if item.strip()
                ]
        return None
    except Exception:
        return None


@st.cache_data(ttl="12h")
def get_week_meals(mon_str, fri_str, office_code, sch_code):
    """주간 급식 조회 (12시간 캐싱)"""
    params = {
        "KEY": KEY,
        "Type": "json",
        "ATPT_OFCDC_SC_CODE": office_code,
        "SD_SCHUL_CODE": sch_code,
        "MLSV_FROM_YMD": mon_str,
        "MLSV_TO_YMD": fri_str,
        "MMEAL_SC_CODE": MEAL_CODE_LUNCH,
        "pSize": "100",
    }
    try:
        response = requests.get(API_URL, params=params)
        if response.status_code != 200:
            return {}
        data = response.json()
        if "mealServiceDietInfo" not in data:
            return {}
        meals = {}
        for meal in data["mealServiceDietInfo"][1]["row"]:
            date = meal.get("MLSV_YMD")
            meal_name = meal.get("DDISH_NM", "")
            meals[date] = [
                re.sub(r'\(.*?\)', '', item).strip()
                for item in meal_name.split('<br/>')
                if item.strip()
            ]
        return meals
    except Exception:
        return {}


def apply_custom_css():
    """공통 UI 스타일 적용"""
    st.markdown("""
    <style>
    .date-badge {
        background: linear-gradient(135deg, #2EC4B6 0%, #3A86FF 100%);
        border-radius: 50px;
        padding: 14px 32px;
        text-align: center;
        color: white;
        font-size: 22px;
        font-weight: 700;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 18px rgba(46, 196, 182, 0.35);
        margin-bottom: 20px;
    }
    .meal-row {
        display: flex;
        align-items: center;
        padding: 13px 20px;
        margin-bottom: 8px;
        border-radius: 14px;
        background: #ffffff;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border-left: 4px solid #2EC4B6;
        font-size: 15px;
    }
    .meal-name { color: #333; font-weight: 500; }
    .no-meal {
        text-align: center;
        color: #aaa;
        padding: 40px 0;
        font-size: 15px;
    }
    .week-table { width: 100%; border-collapse: collapse; margin-top: 8px; }
    .week-table td {
        border: 1px solid #e8e8e8;
        padding: 10px 8px;
        vertical-align: top;
        text-align: center;
        width: 20%;
        font-size: 13px;
        line-height: 1.7;
    }
    .week-table .day-header { font-weight: 700; font-size: 14px; margin-bottom: 6px; }
    @media (prefers-color-scheme: dark) {
        .meal-row { background: #1e1e1e; border-color: #2e2e2e; box-shadow: 0 2px 10px rgba(0,0,0,0.3); }
        .meal-name { color: #e8e8e8; }
        .week-table td { border-color: #333; color: #e0e0e0; }
        .week-table td.today { background-color: #0d2e3a !important; }
        .no-meal { color: #666; }
    }
    @media (prefers-color-scheme: light) {
        .week-table td.today { background-color: #e8faf8 !important; }
    }
    </style>
    """, unsafe_allow_html=True)


def render_meal_page(school_name, office_code, sch_code):
    """급식 페이지 공통 렌더링 함수"""
    apply_custom_css()
    
    now = get_kst_now()
    today_date_str = now.strftime("%Y%m%d")
    date_display = f"{now.strftime('%m월 %d일')} ({WEEK_DAYS[now.weekday()]})"

    st.title(f"🍱 {school_name} 급식")
    st.markdown(f"<div class='date-badge'>🗓️ {date_display}</div>", unsafe_allow_html=True)

    # 오늘의 급식
    meal_items = get_meal_data(today_date_str, office_code, sch_code)
    if meal_items:
        for item in meal_items:
            st.markdown(f"<div class='meal-row'><span class='meal-name'>{item}</span></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='no-meal'>😴 오늘은 급식 정보가 없어요</div>", unsafe_allow_html=True)

    # 주간 급식표
    st.divider()
    st.subheader("📅 이번 주 급식표")

    monday = now - datetime.timedelta(days=now.weekday())
    week_dates = [monday + datetime.timedelta(days=i) for i in range(5)]
    week_meals = get_week_meals(
        monday.strftime("%Y%m%d"),
        week_dates[4].strftime("%Y%m%d"),
        office_code,
        sch_code
    )

    cells_html = ""
    for d in week_dates:
        date_key = d.strftime("%Y%m%d")
        day_label = f"{d.strftime('%m/%d')}<br>({WEEK_DAYS[d.weekday()]})"
        items = week_meals.get(date_key, [])
        items_html = "<br>".join(items) if items else "–"
        css_class = "today" if date_key == today_date_str else ""
        cells_html += f"<td class='{css_class}'><div class='day-header'>{day_label}</div>{items_html}</td>"

    st.markdown(f"<table class='week-table'><tr>{cells_html}</tr></table>", unsafe_allow_html=True)
    st.markdown("<p style='color: grey; font-style: italic; margin-top: 16px; text-align: right;'>made by 시래기T</p>", unsafe_allow_html=True)
