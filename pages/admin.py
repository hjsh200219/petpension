import streamlit as st
from pages.add_pension import show_add_pension_page
from pages.statistics import show_statistics_page
from pages.review_analysis import show_review_analysis_page
def show_admin_page():
    st.subheader("👑 관리자 메뉴")
    
    # 관리자 메뉴 아래 탭 구성
    tab_pension, tab_statistics, tab_review = st.tabs(["펜션 추가/관리", "통계 분석", "리뷰 분석"])
    
    # 펜션 추가/관리 탭
    with tab_pension:
        show_add_pension_page()
    
    # 통계 분석 탭
    with tab_statistics:
        show_statistics_page()

    with tab_review:
        show_review_analysis_page()
