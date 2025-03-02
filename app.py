import streamlit as st
import importlib
import sys
from pathlib import Path
from src.ui import load_css, display_footer, display_banner

# 직접 import 방식 변경
from pages import schedule, admin

# 페이지 모듈 재로드 함수
def reload_modules():
    importlib.reload(schedule)
    importlib.reload(admin)
    # 하위 모듈도 필요한 경우 재로드
    if 'src.common' in sys.modules:
        import src.common
        importlib.reload(src.common)

# 페이지 설정
st.set_page_config(
    page_title="Pet Companion",
    page_icon="🐾",
    layout="wide"
)

# 모듈 재로드
reload_modules()

# 모듈에서 함수 가져오기
from pages.schedule import show_schedule_page
from pages.admin import show_admin_page

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