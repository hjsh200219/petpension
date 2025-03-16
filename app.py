import streamlit as st
import importlib
from src.ui import UI
from pages import schedule, add_pension, price_analysis, admin, review_analysis, petshelter, findmybreed, update_shelter

# 페이지 모듈 재로드 함수
def reload_modules():
    # 모듈 다시 로드
    importlib.reload(price_analysis)
    importlib.reload(review_analysis)
    importlib.reload(add_pension)
    importlib.reload(schedule)
    importlib.reload(petshelter)
    importlib.reload(findmybreed)
    importlib.reload(update_shelter)
    return price_analysis, review_analysis, add_pension, schedule, petshelter, findmybreed, update_shelter

# 페이지 설정
st.set_page_config(
    page_title="Pet Pension",
    page_icon="🐾",
    layout="wide"
)

# 모듈 재로드
price_analysis, review_analysis, add_pension, schedule, petshelter, findmybreed, update_shelter = reload_modules()

# 탭 추가 (수정: 두 개의 탭으로 변경)
tab1, tab2, tab3, tab4 = st.tabs(["임시보호소 현황", "나의 반려동물 찾기", "숙박시설 조회", "관리자 메뉴"])

# 일정 조회 탭
with tab1:
    petshelter.show_petshelter_page()
with tab2:
    findmybreed.show_findmybreed_page()
with tab3:
    schedule.show_schedule_page()
with tab4:
    admin.show_admin_page()

# CSS 로드 및 배너, 푸터 표시
UI().load_css()
UI().display_banner()
UI().display_footer()