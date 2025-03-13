import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
from src.data import Naver
from src.ui import UI
from src.settings import verify_password
import json
from threading import Thread, Lock
import time

# 개발 모드에서만 캐싱 설정 비활성화
if os.environ.get('STREAMLIT_DEVELOPMENT', 'false').lower() == 'true':
    st.cache_data.clear()
    st.cache_resource.clear()

def verify_user_password():
    """사용자 비밀번호 검증 처리"""
    # 비밀번호 검증 상태 초기화
    if 'password_verified' not in st.session_state:
        st.session_state.password_verified = False
    
    if 'password_error' not in st.session_state:
        st.session_state.password_error = False
    
    # 비밀번호 검증 함수
    def check_password():
        password = st.session_state.statistics_password_input
        if verify_password(password):
            st.session_state.password_verified = True
            st.session_state.password_error = False
        else:
            st.session_state.password_error = True
    
    # 비밀번호 검증이 필요한 경우
    if not st.session_state.password_verified:
        st.subheader("🔒 관리자 로그인")
        
        # UI 컴포넌트 사용하여 비밀번호 입력 폼 생성
        UI().create_password_input(
            on_change_callback=check_password,
            has_error=st.session_state.password_error,
            key="statistics_password_input"
        )
        return False
    
    return True

def initialize_session_state():
    """세션 상태 초기화"""
    if 'analyzed' not in st.session_state:
        st.session_state.analyzed = False
    if 'selected_data' not in st.session_state:
        st.session_state.selected_data = None
    if 'cafe_ian_categories' not in st.session_state:
        st.session_state.cafe_ian_categories = []
    if 'category_avg_price' not in st.session_state:
        st.session_state.category_avg_price = None
    if 'schedule_data' not in st.session_state:
        st.session_state.schedule_data = None

def load_pension_data():
    """펜션 정보 데이터 로드"""
    csv_path = './static/database/pension_info.csv'
    if not os.path.exists(csv_path):
        st.error("펜션 정보가 없습니다. 펜션 추가/관리 메뉴에서 펜션을 추가해주세요.")
        return None
    
    return pd.read_csv(csv_path)

def get_region_from_address(address):
    """주소에서 지역 정보 추출"""
    if pd.isna(address):
        return "미분류"
    
    regions = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
               "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
    
    for region in regions:
        if region in address:
            return region
    
    return "기타"

def get_available_regions(pension_info):
    """펜션 정보에서 사용 가능한 지역 목록 추출"""
    regions = ["전체"] + sorted([
        get_region_from_address(addr) for addr in pension_info['addressNew'].dropna().unique()
    ])
    return list(dict.fromkeys(regions))  # 중복 제거

def create_date_region_selection(pension_info):
    """날짜 및 지역 선택 UI 생성"""
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        default_start_date = datetime.now().date()
        start_date = st.date_input("시작일", default_start_date, key="start_date")
    
    with col2:
        default_end_date = (datetime.now() + timedelta(days=30)).date()
        end_date = st.date_input("종료일", default_end_date, key="end_date")
    
    # 지역 필터 정의
    regions = get_available_regions(pension_info)
    
    with col3:
        selected_region = st.selectbox("지역 선택", regions, key="region")
    
    return start_date, end_date, selected_region

@st.cache_data(ttl=1800)  # 30분 캐시
def fetch_schedule_data(pension_info, start_date_str, end_date_str):
    """일정 데이터를 실시간으로 조회하는 함수 (스레드 병렬 처리)"""
    # Naver 객체 생성
    naver = Naver()
    
    # 결과 저장용 데이터프레임
    all_results = []
    results_lock = Lock()  # 결과 리스트 동시 접근 방지용 락
    
    # 진행 상황 관련 변수
    total_pensions = len(pension_info)
    completed_count = 0
    completed_lock = Lock()  # 진행 상황 카운터용 락
    
    # 진행 상황 표시
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 스레드로 실행할 함수 정의
    def worker(row):
        nonlocal completed_count
        
        businessId = str(row.businessId).strip()
        biz_item_id = str(row.bizItemId).strip()
        
        try:
            schedule_data = naver.get_schedule(
                businessId, 
                biz_item_id, 
                start_date_str, 
                end_date_str
            )
            
            # schedule_data가 None이 아닌 경우 처리
            if schedule_data is not None:
                schedule_data['businessName'] = row.businessName
                schedule_data['bizItemName'] = row.bizItemName
                schedule_data['address'] = row.addressNew
                
                # 결과를 필터링하고 필요한 열만 선택
                filtered_schedule_data = schedule_data[
                    schedule_data['isSaleDay'] == True
                ]
                
                filtered_schedule_data = filtered_schedule_data[
                    ['businessName', 'bizItemName', 'date', 'prices', 'address']
                ].rename(columns={
                    'businessName': '숙박업소', 
                    'bizItemName': '숙박상품', 
                    'date': '날짜', 
                    'prices': '가격',
                    'address': '주소'
                })
                
                # 락을 사용하여 결과에 안전하게 추가
                with results_lock:
                    all_results.append(filtered_schedule_data)
        except Exception as e:
            print(f"오류 발생: {row.businessName} - {e}")
        
        # 진행 상황 업데이트
        with completed_lock:
            completed_count += 1
            progress = completed_count / total_pensions
            progress_bar.progress(progress)
            status_text.text(f"처리 중... ({completed_count}/{total_pensions})")
    
    # 스레드 생성 및 실행
    threads = []
    max_workers = min(10, total_pensions)  # 최대 10개 스레드로 제한
    
    for row in pension_info.itertuples(index=False):
        t = Thread(target=worker, args=(row,))
        threads.append(t)
        t.start()
        
        # 최대 동시 실행 스레드 수 제한 (선택적)
        active_threads = sum(1 for t in threads if t.is_alive())
        while active_threads >= max_workers:
            time.sleep(0.1)  # 잠시 대기
            active_threads = sum(1 for t in threads if t.is_alive())
    
    # 모든 스레드 완료 대기
    for t in threads:
        t.join()
    
    # 결과 병합
    result = pd.DataFrame()
    if all_results:
        result = pd.concat(all_results, ignore_index=True)
    
    # 주소에서 지역 정보 추출
    if not result.empty and '주소' in result.columns:
        result['지역'] = result['주소'].apply(get_region_from_address)
    
    # 진행 상황 바 완료 표시
    progress_bar.empty()
    status_text.empty()
    
    # CSV 파일로 저장 (통계 분석용)
    if not result.empty:
        static_dir = Path('./static')
        static_dir.mkdir(exist_ok=True)
        result.to_csv('./static/database/schedule_data.csv', index=False)
    
    return result

def process_schedule_data(schedule_data, start_date, end_date, selected_region):
    """일정 데이터 처리 및 필터링"""
    if schedule_data.empty:
        return pd.DataFrame()
        
    # 날짜 형식 변환 (필요한 경우)
    if not pd.api.types.is_datetime64_any_dtype(schedule_data['날짜']):
        schedule_data['날짜'] = pd.to_datetime(schedule_data['날짜'])
    
    # 필터링된 데이터
    filtered_data = schedule_data.copy()
    
    # 날짜 필터링
    filtered_data = filtered_data[
        (filtered_data['날짜'] >= pd.Timestamp(start_date)) & 
        (filtered_data['날짜'] <= pd.Timestamp(end_date))
    ]
    
    # 지역 필터링
    if selected_region != "전체":
        filtered_data = filtered_data[filtered_data['지역'] == selected_region]
    
    # 카테고리 정보 추가
    filtered_data['카테고리'] = '기타'
    
    # 카페이안 펜션 분류
    cafe_ian_mask = filtered_data['숙박업소'].str.contains('카페이안|카페 이안', case=False, na=False)
    
    # 카페이안 상품별로 카테고리 설정 (펜션명 + 객실타입)
    for idx, row in filtered_data[cafe_ian_mask].iterrows():
        # 상품명 단순화
        product_name = row['숙박상품']
        simplified_name = "숙박"  # 기본값
        
        # 상품명에 따라 간소화된 이름 설정
        if "대관" in product_name or "통대관" in product_name:
            simplified_name = "대관"
        elif "숙박" in product_name:
            simplified_name = "숙박"
        else:
            # 그 외의 경우 원래 상품명 사용 (단, 너무 길면 줄임)
            simplified_name = product_name[:10] + "..." if len(product_name) > 10 else product_name
            
        filtered_data.loc[idx, '카테고리'] = f"카페이안-{simplified_name}"
    
    return filtered_data

def get_other_pensions(filtered_data):
    """카페이안 외 다른 펜션 목록 추출"""
    if filtered_data.empty:
        return []
    return filtered_data[filtered_data['카테고리'] == '기타']['숙박업소'].unique().tolist()

def create_pension_selection(other_pensions):
    """비교할 펜션 선택 UI 생성"""
    selected_pensions = st.multiselect(
        "비교할 펜션 선택 (복수 선택 가능)",
        options=other_pensions,
        default=other_pensions,  # 모든 펜션이 기본적으로 선택되도록 설정
        key="selected_pensions"
    )
    return selected_pensions

def analyze_data(start_date, end_date, selected_region, selected_pensions, pension_info):
    """가격 데이터 분석 함수 (스레드 병렬 처리)"""
    
    st.session_state.analyzing = True
    
    with st.spinner("데이터 분석 중..."):
        # 모든 데이터 가져오기
        schedule_data = fetch_schedule_data(pension_info, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        
        # 데이터가 비어있는 경우 처리
        if schedule_data.empty:
            st.error("가격 정보를 가져오는데 실패했습니다. 다시 시도해주세요.")
            st.session_state.analyzing = False
            return
        
        # 데이터 필터링 및 처리
        filtered_data = process_schedule_data(schedule_data, start_date, end_date, selected_region)
        
        # 데이터가 비어있는 경우 처리
        if filtered_data.empty:
            st.warning(f"선택한 지역 '{selected_region}'에서 가격 정보를 찾을 수 없습니다.")
            st.session_state.analyzing = False
            return
        
        # 카페이안 데이터와 선택된 펜션 데이터 분리
        cafe_ian_data = filtered_data[filtered_data['숙박업소'].str.contains('카페이안|카페 이안')]
        
        # 선택된 펜션 데이터 필터링
        other_pension_data = filtered_data[filtered_data['숙박업소'].isin(selected_pensions)]
        
        # 날짜 정보 추출 (요일 계산용)
        filtered_data['날짜_datetime'] = pd.to_datetime(filtered_data['날짜'])
        filtered_data['요일'] = filtered_data['날짜_datetime'].dt.dayofweek
        filtered_data['월'] = filtered_data['날짜_datetime'].dt.month
        filtered_data['일'] = filtered_data['날짜_datetime'].dt.day
        
        # 주말/평일 구분
        weekend_days = [4, 5]  # 금요일(4), 토요일(5)
        filtered_data['주말여부'] = filtered_data['요일'].isin(weekend_days)
        
        # 최종 결과 데이터프레임 생성
        final_data = []
        
        # 카페이안 데이터 처리 - 각 숙박상품을 카테고리로 설정
        cafe_ian_categories = []
        
        for product in cafe_ian_data['숙박상품'].unique():
            # 카페이안 숙박상품을 카테고리로 지정
            category = f"카페이안-{product}"
            cafe_ian_categories.append(category)
            
            # 해당 숙박상품에 대한 카페이안 데이터
            product_data = cafe_ian_data[cafe_ian_data['숙박상품'] == product].copy()
            product_data['카테고리'] = category
            
            final_data.append(product_data)
        
        # 다른 펜션 데이터 처리 - 각 펜션을 별도 카테고리로 설정
        for pension in selected_pensions:
            # 해당 펜션의 모든 데이터
            pension_data = other_pension_data[other_pension_data['숙박업소'] == pension].copy()
            
            if not pension_data.empty:
                # 펜션 이름을 카테고리로 설정
                pension_data['카테고리'] = pension
                final_data.append(pension_data)
        
        # 데이터 병합
        if final_data:
            final_df = pd.concat(final_data, ignore_index=True)
        else:
            final_df = pd.DataFrame(columns=['숙박업소', '숙박상품', '날짜', '가격', '주소', '카테고리'])
        
        # 카테고리 순서 설정 - 카페이안 카테고리 다음에 선택된 펜션들
        category_order = cafe_ian_categories + selected_pensions
        
        # 카테고리별 평균 가격 계산
        category_avg_price = final_df.groupby(['카테고리', '숙박업소'])['가격'].mean().reset_index()
        
        # 세션 상태 저장
        st.session_state.final_data = final_df
        st.session_state.category_avg_price = category_avg_price
        st.session_state.category_order = category_order
        st.session_state.analyzed = True
        st.session_state.analyzing = False
        st.session_state.analyzed_pensions = selected_pensions
        
        return

def get_ordered_categories(cafe_ian_categories, selected_pensions):
    """카테고리 정렬 순서 설정"""
    category_order = []
    
    # 카페이안-숙박이 가장 먼저
    if "카페이안-숙박" in cafe_ian_categories:
        category_order.append("카페이안-숙박")
    
    # 카페이안-대관이 그 다음
    if "카페이안-대관" in cafe_ian_categories:
        category_order.append("카페이안-대관")
        
    # 나머지 카페이안 카테고리
    for cat in cafe_ian_categories:
        if cat not in ["카페이안-숙박", "카페이안-대관"]:
            category_order.append(cat)
    
    # 선택된 다른 펜션들 (정렬하여 추가)
    # 세션 상태에서 가져오려는 경우 analyzed_pensions 키 사용
    pensions_to_use = st.session_state.get('analyzed_pensions', selected_pensions)
    category_order.extend(sorted(pensions_to_use))
    
    return category_order

def create_avg_price_chart(category_avg_price, category_order):
    """카테고리별 평균 가격 차트 생성"""
    # 데이터 검증
    if category_avg_price is None or len(category_avg_price) == 0:
        fig = go.Figure()
        fig.update_layout(
            title="데이터가 없습니다",
            xaxis=dict(title=""),
            yaxis=dict(title="")
        )
        return fig
    
    # 데이터프레임 형태 확인 및 컬럼명 맞춤
    if '카테고리' in category_avg_price.columns and '가격' in category_avg_price.columns:
        # 카테고리 순서 설정 (존재하는 항목만)
        valid_categories = [cat for cat in category_order if cat in category_avg_price['카테고리'].unique()]
        
        # 그룹 바 차트 생성
        fig = px.bar(
            category_avg_price,
            x='카테고리',
            y='가격',
            color='숙박업소',
            title="숙박상품별 평균 가격",
            text_auto=True,
            category_orders={'카테고리': valid_categories}
        )
    elif '펜션/상품' in category_avg_price.columns and '평균 가격' in category_avg_price.columns:
        # 이전 형식의 데이터프레임 (펜션/상품, 평균 가격)
        fig = px.bar(
            category_avg_price,
            x='펜션/상품',
            y='평균 가격',
            color='펜션/상품',
            title="숙박상품별 평균 가격",
            labels={'평균 가격': '평균 가격(원)'},
            height=600
        )
    else:
        # 지원되지 않는 데이터프레임 형식
        st.error("데이터프레임 형식이 지원되지 않습니다.")
        # 빈 차트 반환
        fig = go.Figure()
        fig.update_layout(
            title="데이터 형식 오류",
            annotations=[dict(
                text="데이터프레임 형식이 지원되지 않습니다.",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5
            )]
        )
        return fig
    
    # Y축 범위 설정 (최소 0부터)
    fig.update_layout(
        yaxis_range=[0, None],
        xaxis_tickangle=0,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Y축 숫자 형식 변경 - 천 단위 구분자 사용 및 소수점 이하 반올림
    fig.update_yaxes(tickformat=",d")
    
    return fig

def create_price_box_chart(selected_data, category_order):
    """가격 범위 박스 차트 생성"""
    # 데이터프레임 구조 검증
    if not isinstance(selected_data, pd.DataFrame) or selected_data.empty:
        st.error("가격 데이터가 없습니다.")
        fig = go.Figure()
        fig.update_layout(
            title="데이터 없음",
            annotations=[dict(text="데이터가 없습니다.", showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)]
        )
        return fig
    
    if '카테고리' not in selected_data.columns or '가격' not in selected_data.columns:
        st.error("데이터프레임 형식이 지원되지 않습니다.")
        fig = go.Figure()
        fig.update_layout(
            title="데이터 형식 오류",
            annotations=[dict(text="데이터프레임 형식이 올바르지 않습니다", showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)]
        )
        return fig
    
    # 카테고리 순서 설정 (존재하는 항목만)
    valid_categories = [cat for cat in category_order if cat in selected_data['카테고리'].unique()]
    
    # 박스 차트 생성
    fig = px.box(
        selected_data, 
        x='카테고리',
        y='가격',
        color='카테고리',
        title='펜션/상품별 가격 분포',
        category_orders={'카테고리': category_order}
    )
    
    # 차트 레이아웃 설정
    fig.update_layout(
        xaxis_title='펜션/상품',
        yaxis_title='가격 (원)',
        yaxis=dict(tickformat=',d', range=[0, None])
    )
    
    # Y축 숫자 형식 변경 - 천 단위 구분자 사용 및 소수점 이하 반올림
    fig.update_yaxes(tickformat=",d")
    
    return fig

def create_daily_price_chart(selected_data, category_order):
    """날짜별 가격 추이 차트 생성"""
    # 데이터프레임 구조 검증
    if not isinstance(selected_data, pd.DataFrame) or selected_data.empty:
        st.error("가격 데이터가 없습니다.")
        fig = go.Figure()
        fig.update_layout(
            title="데이터 없음",
            annotations=[dict(text="데이터가 없습니다.", showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)]
        )
        return fig
        
    if '카테고리' not in selected_data.columns or '가격' not in selected_data.columns or '날짜' not in selected_data.columns:
        st.error("데이터프레임 형식이 지원되지 않습니다.")
        fig = go.Figure()
        fig.update_layout(
            title="데이터 형식 오류",
            annotations=[dict(text="데이터프레임 형식이 올바르지 않습니다", showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)]
        )
        return fig
    
    # 날짜 형식 변환 (문자열이면 datetime으로 변환)
    if selected_data['날짜'].dtype == 'object':
        selected_data['날짜'] = pd.to_datetime(selected_data['날짜'])
    
    # 카테고리 순서 설정 (존재하는 항목만)
    valid_categories = [cat for cat in category_order if cat in selected_data['카테고리'].unique()]
    
    # 날짜별 평균 가격 계산
    daily_avg = selected_data.groupby(['날짜', '카테고리', '숙박업소'])['가격'].mean().reset_index()
    
    # 라인 차트 생성
    fig = px.line(
        daily_avg, 
        x='날짜', 
        y='가격',
        color='카테고리',
        markers=True,
        title='날짜별 가격 추이',
        category_orders={'카테고리': valid_categories}
    )
    
    # 차트 레이아웃 설정
    fig.update_layout(
        xaxis_title='날짜',
        yaxis_title='평균 가격(원)',
        yaxis_range=[0, None],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Y축 숫자 형식 변경 - 천 단위 구분자 사용 및 소수점 이하 반올림
    fig.update_yaxes(tickformat=",d")
    
    return fig

def create_weekday_price_chart(selected_data, category_order):
    """요일별 가격 차트 생성"""
    # 데이터프레임 구조 검증
    if not isinstance(selected_data, pd.DataFrame) or selected_data.empty:
        st.error("가격 데이터가 없습니다.")
        fig = go.Figure()
        fig.update_layout(
            title="데이터 없음",
            annotations=[dict(text="데이터가 없습니다.", showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)]
        )
        return fig
        
    if '카테고리' not in selected_data.columns or '가격' not in selected_data.columns:
        st.error("데이터프레임 형식이 지원되지 않습니다.")
        fig = go.Figure()
        fig.update_layout(
            title="데이터 형식 오류",
            annotations=[dict(text="데이터프레임 형식이 올바르지 않습니다", showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)]
        )
        return fig
    
    # 요일 정보 추출
    if '요일' not in selected_data.columns:
        # 날짜를 datetime으로 변환
        selected_data['날짜_datetime'] = pd.to_datetime(selected_data['날짜'])
        selected_data['요일'] = selected_data['날짜_datetime'].dt.dayofweek
    
    # 요일 이름 매핑
    weekday_names = {
        0: '월요일',
        1: '화요일',
        2: '수요일',
        3: '목요일',
        4: '금요일',
        5: '토요일',
        6: '일요일'
    }
    
    # 요일 이름 추가
    selected_data['요일명'] = selected_data['요일'].map(weekday_names)
    
    # 카테고리 순서 설정 (존재하는 항목만)
    valid_categories = [cat for cat in category_order if cat in selected_data['카테고리'].unique()]
    
    # 요일별 평균 가격 계산
    weekday_price = selected_data.groupby(['카테고리', '요일명', '요일', '숙박업소'])['가격'].mean().reset_index()
    
    # 요일 순서 정렬
    weekday_order = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    weekday_price = weekday_price.sort_values('요일')
    
    # 라인 차트 생성
    fig = px.line(
        weekday_price, 
        x='요일명', 
        y='가격',
        color='카테고리',
        markers=True,
        title='요일별 평균 가격',
        labels={'가격': '평균 가격(원)', '요일명': '요일', '카테고리': '카테고리'},
        category_orders={
            '요일명': weekday_order, 
            '카테고리': valid_categories
        },
        height=600
    )
    
    # 차트 레이아웃 설정
    fig.update_layout(
        yaxis_range=[0, None],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Y축 숫자 형식 변경 - 천 단위 구분자 사용 및 소수점 이하 반올림
    fig.update_yaxes(tickformat=",d")
    
    return fig

def display_analysis_results():
    """분석 결과 표시"""
    # 최근 선택한 펜션 목록
    selected_pensions = st.session_state.get('analyzed_pensions', [])
    
    # 카테고리 평균 가격 데이터
    category_avg_price = st.session_state.category_avg_price
    
    # 카테고리 순서
    category_order = st.session_state.category_order
    
    # 평균 가격 차트
    st.subheader("📊 카테고리별 평균 가격")
    
    # 평균 가격 차트 생성
    avg_price_fig = create_avg_price_chart(category_avg_price, category_order)
    st.plotly_chart(avg_price_fig, use_container_width=True)
    
    # 가격 분포 차트
    st.subheader("📊 가격 분포 분석")
    
    # 최종 데이터
    final_data = st.session_state.final_data
    
    # 가격 박스 플롯
    box_fig = create_price_box_chart(final_data, category_order)
    st.plotly_chart(box_fig, use_container_width=True)
    
    # 일별 가격 추이
    st.subheader("📅 일별 가격 추이")
    
    # 일별 가격 차트
    daily_fig = create_daily_price_chart(final_data, category_order)
    st.plotly_chart(daily_fig, use_container_width=True)
    
    # 요일별 가격 분석
    st.subheader("📆 요일별 가격 분석")
    
    # 요일별 가격 차트
    weekday_fig = create_weekday_price_chart(final_data, category_order)
    st.plotly_chart(weekday_fig, use_container_width=True)
    
    # 원본 데이터 표시
    with st.expander("📋 원본 데이터 확인", expanded=False):
        st.dataframe(
            final_data.sort_values(['카테고리', '날짜']), 
            use_container_width=True,
            hide_index=True
        )

def get_all_pension_names(pension_info):
    """모든 펜션 이름 목록 가져오기"""
    if pension_info is None or pension_info.empty:
        return []
    return sorted(pension_info['businessName'].unique().tolist())

def handle_logout():
    """로그아웃 처리"""
    if st.button("로그아웃", key="statistics_logout", type="secondary"):
        st.session_state.password_verified = False
        st.rerun()

def show_price_analysis_page():
    """통계 페이지 메인 함수"""
    # 비밀번호 검증
    if not verify_user_password():
        return
    
    # 페이지 제목 & 로그아웃 버튼
    col1, col2 = st.columns([5, 1])
    with col1:
        st.subheader("📊 펜션 가격 분석")
    with col2:
        handle_logout()
    
    # 세션 상태 초기화
    initialize_session_state()
    
    # 펜션 정보 불러오기
    pension_info = load_pension_data()
    if pension_info is None:
        return
    
    # 날짜 및 지역 선택 UI
    start_date, end_date, selected_region = create_date_region_selection(pension_info)
    
    # 모든 펜션 이름 가져오기 (분석 전에도 선택 가능하도록)
    all_pensions = get_all_pension_names(pension_info)
    
    # 카페이안 펜션 분리 (기본 선택되도록)
    cafeian_pensions = [p for p in all_pensions if '카페이안' in p or '카페 이안' in p]
    other_pensions = [p for p in all_pensions if p not in cafeian_pensions]
    
    # 비교할 펜션 선택 UI (분석 전에도 선택 가능)
    selected_pensions = st.multiselect(
        "펜션 선택( 최대 5개)",
        options=other_pensions,  # 카페이안을 제외한 모든 펜션
        default=other_pensions[0:5],  # 모든 펜션이 기본적으로 선택되도록 변경
        key="selected_pensions"
    )
    
    col1,col2, col3 = st.columns([1,1,1])
    with col2:
        analyze_clicked = st.button("분석 시작", use_container_width=True, key="analyze_button", type="primary")
    
    # 분석 실행
    if analyze_clicked:
        analyze_data(start_date, end_date, selected_region, selected_pensions, pension_info)
    
    # 분석 결과 표시
    if st.session_state.analyzed:
        display_analysis_results()

if __name__ == "__main__":
    show_price_analysis_page() 