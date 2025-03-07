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
        UI.create_password_input(
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
    csv_path = './static/pension_info.csv'
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
    """일정 데이터를 실시간으로 조회하는 함수"""
    # Naver 객체 생성
    naver = Naver()
    
    # 결과 저장용 데이터프레임
    result = pd.DataFrame()
    
    # 진행 상황 표시
    progress_bar = st.progress(0)
    total_pensions = len(pension_info)
    
    for i, row in enumerate(pension_info.itertuples(index=False)):
        businessId = str(row.businessId).strip()
        biz_item_id = str(row.bizItemId).strip()
        
        schedule_data = naver.get_schedule(
            businessId, 
            biz_item_id, 
            start_date_str, 
            end_date_str
        )
        
        # schedule_data가 None인 경우 건너뜀
        if schedule_data is None:
            continue
            
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
        
        result = pd.concat(
            [result, filtered_schedule_data], 
            ignore_index=True
        )
        
        # 진행 상황 업데이트
        progress_bar.progress((i + 1) / total_pensions)
    
    # 주소에서 지역 정보 추출
    if not result.empty and '주소' in result.columns:
        result['지역'] = result['주소'].apply(get_region_from_address)
    
    # 진행 상황 바 완료 표시
    progress_bar.empty()
    
    # CSV 파일로 저장 (통계 분석용)
    if not result.empty:
        static_dir = Path('./static')
        static_dir.mkdir(exist_ok=True)
        result.to_csv('./static/schedule_data.csv', index=False)
    
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
    """데이터 분석 처리"""
    # 조건이 변경되었는지 확인하기 위한 검사
    current_params = {
        'start_date': start_date.strftime("%Y-%m-%d"),
        'end_date': end_date.strftime("%Y-%m-%d"),
        'region': selected_region,
        'selected_pensions': ','.join(selected_pensions) if selected_pensions else ''
    }
    
    # 새로운 검색 시작
    with st.spinner("일정 데이터를 조회 중입니다..."):
        # 1. 데이터 조회 (캐시 활용)
        schedule_data = fetch_schedule_data(
            pension_info,
            start_date.strftime("%Y-%m-%d"), 
            end_date.strftime("%Y-%m-%d")
        )
        
        if schedule_data.empty:
            st.warning("조회된 일정이 없습니다.")
            return False
        
        # 날짜 형식 변환
        schedule_data['날짜'] = pd.to_datetime(schedule_data['날짜'])
        
        # 세션 상태에 저장
        st.session_state.schedule_data = schedule_data
        
        # 2. 데이터 필터링 처리
        filtered_data = process_schedule_data(
            schedule_data, 
            start_date, 
            end_date, 
            selected_region
        )
        
        if filtered_data.empty:
            st.warning("필터 조건에 맞는 데이터가 없습니다.")
            return False
            
        # 3. 분석 시작
        st.session_state.analyzed = True
        
        # 카페이안 카테고리 목록
        cafe_ian_categories = [cat for cat in filtered_data['카테고리'].unique() if cat.startswith('카페이안-')]
        st.session_state.cafe_ian_categories = cafe_ian_categories
        
        # 선택된 펜션만 필터링 (카페이안 모든 상품 포함)
        if not selected_pensions:
            # 선택된 펜션이 없으면 모든 펜션 포함
            other_pensions = get_other_pensions(filtered_data)
            selected_pensions = other_pensions
        
        # 분석에 사용된 펜션 목록을 다른 키에 저장 (위젯 키와 충돌 방지)
        st.session_state.analyzed_pensions = selected_pensions.copy()
            
        # 각 펜션을 개별 카테고리로 설정 (기타 카테고리 대신 펜션명 사용)
        for pension in selected_pensions:
            pension_mask = filtered_data['숙박업소'] == pension
            filtered_data.loc[pension_mask, '카테고리'] = pension
            
        # 선택된 펜션만 필터링 (카페이안 모든 상품 + 선택된 펜션)
        selected_data = filtered_data[
            (filtered_data['카테고리'].isin(cafe_ian_categories)) | 
            (filtered_data['카테고리'].isin(selected_pensions))
        ]
        
        # 데이터 세션 저장
        st.session_state.selected_data = selected_data
        
        # 카테고리별 평균 가격 계산
        category_avg_price = selected_data.groupby('카테고리')['가격'].agg(['mean', 'min', 'max', 'count']).reset_index()
        category_avg_price.columns = ['펜션/상품', '평균 가격', '최소 가격', '최대 가격', '객실 수']
        
        # 숫자 형식 정리
        category_avg_price['평균 가격'] = category_avg_price['평균 가격'].astype(int)
        category_avg_price['최소 가격'] = category_avg_price['최소 가격'].astype(int)
        category_avg_price['최대 가격'] = category_avg_price['최대 가격'].astype(int)
        
        # 카테고리별 평균 가격 세션 저장
        st.session_state.category_avg_price = category_avg_price
        
        # 현재 파라미터 저장 (다음 검색 조건 비교용)
        st.session_state.last_search_params = current_params
        
        # 분석 완료 메시지
        st.success("데이터 분석이 완료되었습니다.")
        return True

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
    category_order.extend(sorted(selected_pensions))
    
    return category_order

def create_avg_price_chart(category_avg_price, category_order):
    """평균 가격 막대 차트 생성"""
    fig = px.bar(
        category_avg_price,
        x='펜션/상품',
        y='평균 가격',
        color='펜션/상품',
        title='펜션/상품별 평균 가격 비교',
        text_auto=True,
        category_orders={'펜션/상품': category_order}
    )
    
    fig.update_layout(
        xaxis_title='펜션/상품',
        yaxis_title='평균 가격 (원)',
        yaxis=dict(tickformat=',d', range=[0, None])
    )
    
    return fig

def create_price_box_chart(selected_data, category_order):
    """가격 범위 상자 그림 생성"""
    # 카테고리 순서를 위한 매핑 생성
    category_order_map = {cat: i for i, cat in enumerate(category_order)}
    
    # 정렬을 위한 임시 열 추가
    selected_data['카테고리_순서'] = selected_data['카테고리'].map(
        lambda x: category_order_map.get(x, len(category_order))
    )
    
    # 카테고리 순서로 데이터 정렬
    selected_data_sorted = selected_data.sort_values('카테고리_순서')
    
    fig = px.box(
        selected_data_sorted,
        x='카테고리',
        y='가격',
        color='카테고리',
        title='펜션/상품별 가격 분포',
        category_orders={'카테고리': category_order}
    )
    
    fig.update_layout(
        xaxis_title='펜션/상품',
        yaxis_title='가격 (원)',
        yaxis=dict(tickformat=',d', range=[0, None])
    )
    
    return fig

def create_daily_price_chart(selected_data, category_order):
    """날짜별 가격 추이 차트 생성"""
    # 날짜별 평균 가격
    date_avg_price = selected_data.groupby(['날짜', '카테고리'])['가격'].mean().reset_index()
    
    # 날짜별 가격 추이 차트
    fig = px.line(
        date_avg_price,
        x='날짜',
        y='가격',
        color='카테고리',
        title='날짜별 펜션/상품 평균 가격 추이',
        markers=True,
        category_orders={'카테고리': category_order}
    )
    
    fig.update_layout(
        xaxis_title='날짜',
        yaxis_title='평균 가격 (원)',
        yaxis=dict(tickformat=',d', range=[0, None]),
        legend={'traceorder': 'normal'}
    )
    
    return fig

def create_weekday_price_chart(selected_data, category_order):
    """요일별 가격 차트 생성"""
    # 요일 추가
    selected_data['요일'] = selected_data['날짜'].dt.day_name()
    
    # 요일 순서 정렬
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # 한글 요일로 변환
    day_korean = {
        'Monday': '월요일',
        'Tuesday': '화요일',
        'Wednesday': '수요일',
        'Thursday': '목요일',
        'Friday': '금요일',
        'Saturday': '토요일',
        'Sunday': '일요일'
    }
    
    selected_data['요일_한글'] = selected_data['요일'].map(day_korean)
    
    # 요일별 평균 가격 계산
    day_avg_price = selected_data.groupby(['요일_한글', '카테고리'])['가격'].mean().reset_index()
    
    # 요일 순서 맞추기
    day_order_korean = [day_korean[day] for day in days_order]
    day_avg_price['요일_순서'] = day_avg_price['요일_한글'].map(lambda x: day_order_korean.index(x))
    day_avg_price = day_avg_price.sort_values('요일_순서')
    
    # 요일별 가격 차트
    fig = px.line(
        day_avg_price,
        x='요일_한글',
        y='가격',
        color='카테고리',
        title='요일별 펜션/상품 평균 가격',
        markers=True,
        category_orders={'카테고리': category_order}
    )
    
    fig.update_layout(
        xaxis={'categoryorder': 'array', 'categoryarray': day_order_korean},
        yaxis_title='평균 가격 (원)',
        yaxis=dict(tickformat=',d', range=[0, None]),
        legend={'traceorder': 'normal'}
    )
    
    return fig

def display_analysis_results():
    """분석 결과 시각화 표시"""
    selected_data = st.session_state.selected_data
    cafe_ian_categories = st.session_state.cafe_ian_categories
    category_avg_price = st.session_state.category_avg_price
    
    # 데이터가 있는지 확인
    if selected_data.empty:
        st.warning("선택한 조건에 맞는 데이터가 없습니다.")
        return
    
    # 선택된 펜션 목록 (세션에서 가져오기)
    selected_pensions = st.session_state.get('analyzed_pensions', [])
    
    # 카테고리 순서 정렬
    category_order = get_ordered_categories(cafe_ian_categories, selected_pensions)
    
    # 카테고리별 평균 가격 데이터프레임 정렬
    if not category_avg_price.empty:
        # 카테고리 순서에 따른 정렬을 위한 사용자 정의 순서 추가
        category_avg_price['order'] = category_avg_price['펜션/상품'].apply(
            lambda x: category_order.index(x) if x in category_order else len(category_order)
        )
        category_avg_price = category_avg_price.sort_values('order').drop('order', axis=1)
    
    # 2. 카페이안과 다른 펜션들의 가격 비교
    st.subheader("펜션 가격 비교 분석")
    
    # 테이블 형태로 표시
    st.dataframe(category_avg_price, use_container_width=True, hide_index=True)
    
    # 1. 평균 가격 차트
    fig1 = create_avg_price_chart(category_avg_price, category_order)
    st.plotly_chart(fig1, use_container_width=True)
    
    # 2. 가격 범위 상자 그림
    fig2 = create_price_box_chart(selected_data, category_order)
    st.plotly_chart(fig2, use_container_width=True)
    
    # 3. 날짜별 가격 추이 차트
    fig3 = create_daily_price_chart(selected_data, category_order)
    st.plotly_chart(fig3, use_container_width=True)
    
    # 4. 요일별 가격 차트
    fig4 = create_weekday_price_chart(selected_data, category_order)
    st.plotly_chart(fig4, use_container_width=True)

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