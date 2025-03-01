import streamlit as st
from pathlib import Path
from src.ui import load_css, display_footer, display_banner
from pages.schedule import show_schedule_page
from pages.admin import show_admin_page

# 페이지 설정
st.set_page_config(
    page_title="Pet Companion",
    page_icon="🐾",
    layout="wide"
)

# 탭 추가
tab1, tab2 = st.tabs(["숙박시설 조회", "관리자 메뉴"])

# 일정 조회 탭
with tab1:
    show_schedule_page()

# 관리자 메뉴 탭
with tab2:
    show_admin_page()

# CSS 로드 및 배너, 푸터 표시
css_path = Path(__file__).parent / "static" / "css" / "style.css"
load_css(str(css_path))

display_banner()
display_footer()

# streamlit run app.py