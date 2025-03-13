import streamlit as st
import pandas as pd
import os
import numpy as np
from src.ui import UI
from datetime import datetime, timedelta
from src.settings import verify_password
from src.data import Naver
from src.chart import Chart
from threading import Thread, Lock
import time

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
        UI().create_password_input(
            on_change_callback=check_password,
            has_error=st.session_state.password_error,
            key="review_password_input"
        )
        return False
    return True

def load_pension_data():
    """펜션 기본 정보 로드"""
    pension_info = pd.read_csv('./static/database/pension_info.csv')
    pension_info = pension_info[['businessName', 'channelId', 'addressNew']].drop_duplicates()
    pension_info['channelId'] = pension_info['channelId'].astype(str)
    return pension_info

def fetch_rating_data_threaded(pension_info_filtered):
    """멀티스레드를 사용하여 리뷰 데이터를 가져오는 함수"""
    # Naver 객체 생성
    naver = Naver()
    
    # 로딩 상태 표시
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    # 결과 저장용 리스트 및 락
    all_results = []
    results_lock = Lock()
    
    # 진행 상황 추적용 변수
    total_pensions = len(pension_info_filtered)
    completed_count = 0
    completed_lock = Lock()
    
    # 스레드로 실행될 함수
    def fetch_rating_worker(row):
        nonlocal completed_count
        
        channel_id = row.channelId
        business_name = row.businessName
        
        try:
            # 리뷰 데이터 가져오기
            result = naver._get_rating_playwright(channel_id)
            
            # 결과가 데이터프레임인 경우 처리
            if isinstance(result, pd.DataFrame):
                result['businessName'] = business_name
                result['channelId'] = channel_id
                
                # 락을 사용하여 결과에 안전하게 추가
                with results_lock:
                    all_results.append(result)
            else:
                print(f"오류: {business_name}의 리뷰 데이터 형식이 올바르지 않음")
        except Exception as e:
            print(f"오류 발생: {business_name} - {str(e)}")
        
        # 진행 상황 업데이트
        with completed_lock:
            completed_count += 1
            progress = completed_count / total_pensions
            progress_bar.progress(progress)
            status_text.text(f"리뷰 데이터 수집 중... ({completed_count}/{total_pensions})")
    
    # 스레드 생성 및 실행
    threads = []
    max_workers = min(5, total_pensions)  # 최대 5개 스레드로 제한
    
    for row in pension_info_filtered.itertuples(index=False):
        t = Thread(target=fetch_rating_worker, args=(row,))
        threads.append(t)
        t.start()
        
        # 최대 동시 실행 스레드 수 제한
        active_threads = sum(1 for t in threads if t.is_alive())
        while active_threads >= max_workers:
            time.sleep(0.1)  # 잠시 대기
            active_threads = sum(1 for t in threads if t.is_alive())
    
    # 모든 스레드 완료 대기
    for t in threads:
        t.join()
    
    # 진행 상황 바 및 상태 텍스트 제거
    progress_bar.empty()
    status_text.empty()
    
    # 결과 병합
    rating_data = pd.DataFrame()
    if all_results:
        rating_data = pd.concat(all_results, ignore_index=True)
        
        # CSV로 저장
        rating_data.to_csv('./static/database/rating_data.csv', index=False)
    
    return rating_data

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
        
        # 리뷰 데이터 가져오기
        with st.spinner("리뷰 데이터 수집중..."):
            try:
                # 스레드를 사용하여 리뷰 데이터 가져오기
                rating_data = fetch_rating_data_threaded(pension_info_filtered)
                
                # 수집된 데이터가 없거나 비어있는 경우 처리
                if rating_data is None or rating_data.empty:
                    st.error("리뷰 데이터를 가져오는데 실패했습니다.")
                    return
                
                # 세션 상태에 데이터 저장
                st.session_state.rating_data = rating_data
                st.session_state.pension_info_filtered = pension_info_filtered
            except Exception as e:
                st.error(f"데이터 수집 중 오류가 발생했습니다: {str(e)}")
                return
        
        # 데이터 분석
        with st.spinner("리뷰 데이터 분석중..."):
            rating_average, pension_col = process_rating_data(rating_data, pension_info_filtered)
            
            # 분석 결과 저장
            st.session_state.rating_average = rating_average
            st.session_state.pension_col = pension_col
            st.session_state.has_analysis_result = True
            
            # 카테고리 순서 정의
            st.session_state.category_order = rating_average['review_item'].unique().tolist()
    
    # 분석 결과 표시
    if st.session_state.has_analysis_result:
        rating_average = st.session_state.rating_average
        pension_col = st.session_state.pension_col
        
        # 카페이안을 최상위로 정렬
        rating_average, pension_order = prioritize_cafeian(rating_average, pension_col)
        
        # 분석 결과 시각화
        Chart.show_rating_charts(rating_average, pension_col, st.session_state.category_order)

if __name__ == "__main__":
    show_review_analysis_page() 