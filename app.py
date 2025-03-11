import streamlit as st
import importlib
from src.ui import UI
from pages.schedule import show_schedule_page
from pages.admin import show_admin_page
from pages.petshelter import show_petshelter_page
# 직접 import 방식 변경
from pages import schedule, add_pension, price_analysis, admin, review_analysis, petshelter

# 페이지 모듈 재로드 함수
def reload_modules():
    import pages.price_analysis as price_analysis
    import pages.review_analysis as review_analysis
    import pages.add_pension as add_pension
    import pages.schedule as schedule
    import pages.petshelter as petshelter
    # 모듈 다시 로드
    importlib.reload(price_analysis)
    importlib.reload(review_analysis)
    importlib.reload(add_pension)
    importlib.reload(schedule)
    importlib.reload(admin)
    importlib.reload(petshelter)
    return price_analysis, review_analysis, add_pension, schedule, petshelter

# 페이지 설정
st.set_page_config(
    page_title="Pet Pension",
    page_icon="🐾",
    layout="wide"
)

# 모듈 재로드
price_analysis, review_analysis, add_pension, schedule, petshelter = reload_modules()

# 탭 추가 (수정: 두 개의 탭으로 변경)
tab1, tab2, tab3 = st.tabs(["임시보호소 현황","숙박시설 조회", "관리자 메뉴"])

# 일정 조회 탭
with tab1:
    show_petshelter_page()
with tab2:
    show_schedule_page()
with tab3:
    show_admin_page()

# CSS 로드 및 배너, 푸터 표시
UI.load_css()

UI.display_banner()
UI.display_footer()

# streamlit run app.py