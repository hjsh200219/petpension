import streamlit as st
import pandas as pd
import os
import numpy as np
from src.ui import UI
from datetime import datetime, timedelta
from src.settings import verify_password
from src.data import Naver
from src.chart import Chart

naver = Naver()

# 개발 모드일 때 캐시 초기화
if os.environ.get('STREAMLIT_DEVELOPMENT', 'false').lower() == 'true':
    st.cache_data.clear()
    st.cache_resource.clear()

def verify_user_password():
    """사용자 비밀번호 검증 처리"""
    st.session_state.setdefault('password_verified', False)
    st.session_state.setdefault('password_error', False)
    
    def check_password():
        password = st.session_state.review_password_input
        st.session_state.password_verified = verify_password(password)
        st.session_state.password_error = not st.session_state.password_verified
    
    if not st.session_state.password_verified:
        st.subheader("🔒 관리자 로그인")
        UI.create_password_input(
            on_change_callback=check_password,
            has_error=st.session_state.password_error,
            key="review_password_input"
        )
        return False
    return True

def load_pension_data():
    """펜션 기본 정보 로드"""
    pension_info = pd.read_csv('./static/pension_info.csv')
    pension_info = pension_info[['businessName', 'channelId', 'addressNew']].drop_duplicates()
    pension_info['channelId'] = pension_info['channelId'].astype(str)
    return pension_info

def process_rating_data(rating_data, pension_info_filtered):
    """리뷰 데이터 처리 및 Z-score 계산"""
    # 데이터 타입 변환
    rating_data['channelId'] = rating_data['channelId'].astype(str)
    pension_info_filtered['channelId'] = pension_info_filtered['channelId'].astype(str)
    
    # 데이터 병합
    merged_data = pd.merge(
        rating_data,
        pension_info_filtered[['channelId', 'businessName']],
        on='channelId',
        how='left'
    )
    
    # 평점 데이터 전처리
    merged_data['rating'] = pd.to_numeric(merged_data['rating'], errors='coerce')
    merged_data = merged_data.dropna(subset=['rating'])
    
    # 그룹화 컬럼 결정
    group_cols = ['channelId', 'businessName', 'review_item'] if 'businessName' in merged_data.columns else ['channelId', 'review_item']
    pension_col = 'businessName' if 'businessName' in merged_data.columns else 'pension_name'
    
    if pension_col == 'pension_name':
        pension_mapping = dict(zip(
            pension_info_filtered['channelId'],
            pension_info_filtered['businessName']
        ))
        merged_data['pension_name'] = merged_data['channelId'].map(pension_mapping)
        group_cols = ['channelId', 'pension_name', 'review_item']
    
    # 평균 평점 계산
    rating_average = merged_data.groupby(group_cols)['rating'].mean().reset_index()
    pension_totals = rating_average.groupby(['channelId', pension_col])['rating'].sum().reset_index()
    pension_totals.rename(columns={'rating': 'total_rating'}, inplace=True)
    
    # 데이터 병합 및 상대값 계산
    rating_average = pd.merge(
        rating_average,
        pension_totals,
        on=['channelId', pension_col],
        how='left'
    )
    
    # 상대값 계산
    rating_average['rating_relative'] = rating_average['rating'] / rating_average['total_rating']
    rating_average['rating_relative_pct'] = rating_average['rating_relative'] * 100
    
    # Z-score 계산
    zscore_data = []
    for pension_name in rating_average[pension_col].unique():
        pension_data = rating_average[rating_average[pension_col] == pension_name].copy()
        mean_score = pension_data['rating_relative_pct'].mean()
        std_score = pension_data['rating_relative_pct'].std()
        pension_data['zscore'] = (pension_data['rating_relative_pct'] - mean_score) / std_score if std_score != 0 else 0
        zscore_data.append(pension_data)
    
    return pd.concat(zscore_data), pension_col

def prioritize_cafeian(rating_average, pension_col):
    """카페이안을 첫 번째로 하는 펜션 순서 생성 및 적용"""
    pension_order = list(rating_average[pension_col].unique())
    
    # 카페이안 펜션 식별 (카페이안 또는 카페 이안)
    cafeian_pensions = [p for p in pension_order if '카페이안' in p or '카페 이안' in p]
    
    if cafeian_pensions:
        # 카페이안 펜션들을 모두 제거하고 맨 앞에 추가
        for cafeian in cafeian_pensions:
            pension_order.remove(cafeian)
        pension_order = cafeian_pensions + sorted(pension_order)
    else:
        pension_order = sorted(pension_order)
    
    # 펜션 열을 카테고리 타입으로 변환하고 순서 지정
    rating_average[pension_col] = pd.Categorical(
        rating_average[pension_col],
        categories=pension_order,
        ordered=True
    )
    
    # 정렬된 데이터로 업데이트
    return rating_average.sort_values(pension_col), pension_order

def initialize_session_state():
    """세션 상태 초기화"""
    st.session_state.setdefault('chart_type', "radar")
    st.session_state.setdefault('has_analysis_result', False)
    st.session_state.setdefault('rating_data_dict', None)
    st.session_state.setdefault('rating_average_dict', None)
    st.session_state.setdefault('pension_col_result', None)
    st.session_state.setdefault('analyzed_pensions', [])

def handle_logout():
    """로그아웃 처리"""
    if st.button("로그아웃", key="review_logout", type="secondary"):
        st.session_state.password_verified = False
        st.rerun()

def show_review_analysis_page():
    """리뷰 분석 페이지 메인 함수"""
    # 비밀번호 검증
    if not verify_user_password():
        return
    
    # 페이지 제목 & 로그아웃 버튼
    col1, col2 = st.columns([5, 1])
    with col1:
        st.subheader("🔍 펜션 리뷰 비교")
    with col2:
        handle_logout()
    
    # 기본 데이터 로드
    pension_info = load_pension_data()
    
    # 펜션 선택 UI (카페이안 제외)
    all_pensions = pension_info['businessName'].unique()
    
    # 카페이안 펜션 식별
    cafeian_pensions = [p for p in all_pensions if '카페이안' in p or '카페 이안' in p]
    
    # 카페이안을 제외한 다른 펜션들만 선택 옵션으로 표시
    other_pensions = [p for p in all_pensions if p not in cafeian_pensions]
    
    selected_pensions = st.multiselect(
        "펜션 선택 (최대 5개, 카페이안은 자동 포함)",
        options=other_pensions,
        default=other_pensions[:5],  # 최대 5개 기본 선택
        key="review_selected_pensions",
        max_selections=5
    )
    
    # 분석을 위해 카페이안을 선택된 펜션 목록에 추가
    analysis_pensions = cafeian_pensions + selected_pensions
    
    # 세션 상태 초기화
    initialize_session_state()
    
    col1,col2, col3 = st.columns([1,1,1])
    with col2:
        # 분석 시작 버튼
        review_button = st.button(
            "분석 시작", 
            use_container_width=True, 
            key=f"analyze_button_{st.session_state.review_selected_pensions}",
            type="primary"
        )
    
    # 분석 결과 표시 조건
    if not (review_button or st.session_state.has_analysis_result):
        return
    
    # 데이터 처리 및 분석
    if review_button:
        # 선택한 펜션 정보 표시 (카페이안 포함)
        pension_info_filtered = pension_info[pension_info['businessName'].isin(analysis_pensions)]
        st.dataframe(pension_info_filtered, use_container_width=True, hide_index=True)
        
        # 리뷰 데이터 수집
        with st.spinner("리뷰 데이터 수집중..."):
            try:
                rating_data = naver.get_rating_data(pension_info_filtered)
                
                # 수집된 데이터가 없거나 비어있는 경우 처리
                if rating_data.empty:
                    st.error("리뷰 데이터를 가져오는데 실패했습니다. 다시 시도해주세요.")
                    st.session_state.has_analysis_result = False
                    return
                
                with st.expander("리뷰 데이터 보기", expanded=False):
                    st.dataframe(rating_data, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"리뷰 데이터 수집 중 오류 발생: {str(e)}")
                st.session_state.has_analysis_result = False
                return
        
        # 데이터 분석
        with st.spinner("리뷰 데이터 분석중..."):
            rating_average, pension_col = process_rating_data(rating_data, pension_info_filtered)
            
            # 분석 결과 저장
            st.session_state.rating_data_dict = rating_data.to_dict('records')
            st.session_state.rating_average_dict = rating_average.to_dict('records')
            st.session_state.pension_col_result = pension_col
            st.session_state.has_analysis_result = True
            st.session_state.analyzed_pensions = analysis_pensions
    else:
        # 저장된 분석 결과 불러오기
        rating_data = pd.DataFrame(st.session_state.rating_data_dict)
        rating_average = pd.DataFrame(st.session_state.rating_average_dict)
        pension_col = st.session_state.pension_col_result
        
        # 현재 분석 중인 펜션 정보 표시
        st.info(f"현재 분석 중인 펜션: {', '.join(st.session_state.analyzed_pensions)}")
        st.dataframe(rating_data, use_container_width=True, hide_index=True)
    
    # 카페이안 우선 순위 적용
    rating_average, pension_order = prioritize_cafeian(rating_average, pension_col)
    
    # 차트 타입 선택
    chart_type = st.radio(
        "차트 유형 선택:",
        options=["레이더 차트", "바 차트", "히트맵"],
        index=0 if st.session_state.chart_type == "radar" else 
              1 if st.session_state.chart_type == "bar" else 2,
        horizontal=True,
        key="chart_type_radio"
    )
    
    # 선택된 차트 타입 저장
    if chart_type == "레이더 차트":
        st.session_state.chart_type = "radar"
    elif chart_type == "바 차트":
        st.session_state.chart_type = "bar"
    elif chart_type == "히트맵":
        st.session_state.chart_type = "heatmap"
    
    # 차트 유형에 따라 다른 차트 표시
    if st.session_state.chart_type == "bar":
        fig = Chart.create_bar_chart(rating_average, pension_col)
    elif st.session_state.chart_type == "heatmap":
        fig = Chart.create_heatmap(rating_average, pension_col, pension_order)
    else:  # 레이더 차트
        # 레이더 차트에는 카페이안과 선택된 다른 펜션만 표시 (카페이안은 항상 포함)
        Chart.create_radar_tabs(rating_average, pension_col, pension_order)
    
    # 바/히트맵 차트 표시
    if st.session_state.chart_type != "radar":
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    show_review_analysis_page() 