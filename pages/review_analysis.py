import streamlit as st
import pandas as pd
import plotly.express as px
import os
import numpy as np
from src.common import UI
from datetime import datetime, timedelta
from src.settings import verify_password


# 개발 모드에서만 캐싱 설정 비활성화
if os.environ.get('STREAMLIT_DEVELOPMENT', 'false').lower() == 'true':
    st.cache_data.clear()
    st.cache_resource.clear()

def show_review_analysis_page():
    # 비밀번호 검증 상태 초기화
    if 'password_verified' not in st.session_state:
        st.session_state.password_verified = False
    
    if 'password_error' not in st.session_state:
        st.session_state.password_error = False
    
    # 비밀번호 검증 함수
    def check_password():
        password = st.session_state.review_password_input
        if verify_password(password):
            st.session_state.password_verified = True
            st.session_state.password_error = False
        else:
            st.session_state.password_error = True
    
    # 비밀번호 검증이 필요한 경우
    if not st.session_state.password_verified:
        st.subheader("🔍 펜션 리뷰 분석 로그인")
        
        # UI 컴포넌트 사용하여 비밀번호 입력 폼 생성
        UI.create_password_input(
            on_change_callback=check_password,
            has_error=st.session_state.password_error,
            key="review_password_input"
        )
        return
    
    st.subheader("🔍 펜션 리뷰 비교")

    pension_info = pd.read_csv('./static/pension_info.csv')
    selected_pensions = st.multiselect(
        "분석할 펜션을 선택 (최대 5개)",
        options=pension_info['businessName'].unique(),  # pension_info에서 숙박업소 목록 추출
        default=pension_info['businessName'].unique()[:5],  # 기본 선택값으로 첫 5개 펜션 설정
        key="review_selected_pensions",
        max_selections=5
    )

if __name__ == "__main__":
    show_review_analysis_page() 