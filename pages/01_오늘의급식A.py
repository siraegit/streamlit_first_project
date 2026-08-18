import streamlit as st
import utils

office_code = st.secrets["school_A"]["education_office_code"]
school_code = st.secrets["school_A"]["school_code"]

utils.render_meal_page("[BS]", office_code, school_code)
