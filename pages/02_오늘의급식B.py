import streamlit as st
import utils

office_code = st.secrets["school_B"]["education_office_code"]
school_code = st.secrets["school_B"]["school_code"]

utils.render_meal_page("[YG]오늘의 급식", office_code, school_code)
