import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.common import Naver
from pathlib import Path

def show_schedule_page():
    # Naver 객체 생성
    st.subheader("🐾반려동물 동반 숙박시설 조회")
    naver = Naver()
    
    # 세션 상태 초기화
    if 'result' not in st.session_state:
        st.session_state.result = pd.DataFrame()
    if 'filtered_result' not in st.session_state:
        st.session_state.filtered_result = pd.DataFrame()
    if 'business_name_filter' not in st.session_state:
        st.session_state.business_name_filter = "전체"
    if 'biz_item_name_filter' not in st.session_state:
        st.session_state.biz_item_name_filter = "전체"
    if 'region_filter' not in st.session_state:
        st.session_state.region_filter = "전체"
    
    # 날짜 선택
    col1, col2, col3 = st.columns((1,1,3))
    with col1:
        start_date = st.date_input(
            "시작 날짜", 
            datetime.now(), 
            label_visibility="collapsed"
        )
    with col2:
        end_date = st.date_input(
            "종료 날짜", 
            datetime.now() + timedelta(days=30), 
            label_visibility="collapsed")
    with col3:
        search_button = st.button("일정 조회", key="unique_schedule_button", use_container_width=False)

    # CSV 파일에서 데이터 읽기
    pension_info = pd.read_csv('./static/pension_info.csv')

    # 검색 버튼 클릭 시 데이터 로드
    if search_button:  # 고유 키 추가
        # 새 검색 시 이전 결과 초기화
        st.session_state.result = pd.DataFrame()
        result = pd.DataFrame()
        
        for row in pension_info.itertuples(index=False):
            businessId = str(row.businessId).strip()
            biz_item_id = str(row.bizItemId).strip()

            schedule_data = naver.get_schedule(
                businessId, 
                biz_item_id, 
                start_date.strftime("%Y-%m-%d"), 
                end_date.strftime("%Y-%m-%d")
            )
            schedule_data['businessName'] = row.businessName
            schedule_data['bizItemName'] = row.bizItemName
            schedule_data['address'] = row.address_new
            
            # 결과를 필터링하고 필요한 열만 선택
            filtered_schedule_data = schedule_data[schedule_data['isSaleDay'] == True]
            filtered_schedule_data = filtered_schedule_data[['businessName', 'bizItemName', 'date', 'prices', 'address']].rename(columns={
                'businessName': '숙박업소', 
                'bizItemName': '숙박상품', 
                'date': '날짜', 
                'prices': '가격',
                'address': '주소'
            })
            
            result = pd.concat([result, filtered_schedule_data], ignore_index=True)  # 결과를 누적 저장

        st.session_state.result = result
        # 검색 결과 저장 후 필터링된 결과도 초기화
        st.session_state.filtered_result = result
        # 필터값 초기화
        st.session_state.business_name_filter = "전체"
        st.session_state.biz_item_name_filter = "전체"
        st.session_state.region_filter = "전체"

    # 필터링 함수 정의
    def apply_filters():
        filtered_data = st.session_state.result.copy()
        
        if st.session_state.business_name_filter != "전체":
            filtered_data = filtered_data[filtered_data['숙박업소'] == st.session_state.business_name_filter]
            
        if st.session_state.biz_item_name_filter != "전체":
            filtered_data = filtered_data[filtered_data['숙박상품'] == st.session_state.biz_item_name_filter]
            
        if st.session_state.region_filter != "전체":
            region_mapping = {
                "서울": ["서울", "서울특별시"],
                "부산": ["부산", "부산광역시"],
                "대구": ["대구", "대구광역시"],
                "인천": ["인천", "인천광역시"],
                "광주": ["광주", "광주광역시"],
                "대전": ["대전", "대전광역시"],
                "울산": ["울산", "울산광역시"],
                "세종": ["세종", "세종특별자치시"],
                "경기": ["경기", "경기도"],
                "강원": ["강원", "강원도"],
                "충북": ["충북", "충청북도"],
                "충남": ["충남", "충청남도"],
                "전북": ["전북", "전라북도"],
                "전남": ["전남", "전라남도"],
                "경북": ["경북", "경상북도"],
                "경남": ["경남", "경상남도"],
                "제주": ["제주", "제주특별자치도"]
            }
            filtered_data = filtered_data[filtered_data['주소'].str.contains('|'.join(region_mapping[st.session_state.region_filter]))]
            
        st.session_state.filtered_result = filtered_data

    # 필터 변경 콜백 함수
    def on_business_filter_change():
        st.session_state.business_name_filter = st.session_state.business_filter_widget
        apply_filters()
        
    def on_item_filter_change():
        st.session_state.biz_item_name_filter = st.session_state.item_filter_widget
        apply_filters()
        
    def on_region_filter_change():
        st.session_state.region_filter = st.session_state.region_filter_widget
        apply_filters()

    # 결과 표시 (검색 결과가 있는 경우)
    if not st.session_state.result.empty:
        st.success("일정 조회가 완료되었습니다.")
        
        filter_col1, filter_col2, filter_col3 = st.columns(3)

        # 숙박업소 필터 옵션 및 인덱스 계산
        business_options = ["전체"] + list(st.session_state.result['숙박업소'].unique())
        business_index = 0  # 기본값
        if st.session_state.business_name_filter in business_options:
            business_index = business_options.index(st.session_state.business_name_filter)

        with filter_col1:
            st.selectbox(
                "숙박업소 선택", 
                options=business_options,
                key="business_filter_widget",
                index=business_index,
                on_change=on_business_filter_change
            )

        # 숙박상품 필터 옵션 및 인덱스 계산
        item_options = ["전체"] + list(st.session_state.result['숙박상품'].unique())
        item_index = 0  # 기본값
        if st.session_state.biz_item_name_filter in item_options:
            item_index = item_options.index(st.session_state.biz_item_name_filter)

        with filter_col2:
            st.selectbox(
                "숙박상품 선택", 
                options=item_options,
                key="item_filter_widget",
                index=item_index,
                on_change=on_item_filter_change
            )

        # 지역 필터 옵션 및 인덱스 계산
        region_options = ["전체", "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
        region_index = 0  # 기본값
        if st.session_state.region_filter in region_options:
            region_index = region_options.index(st.session_state.region_filter)

        with filter_col3:
            st.selectbox(
                "지역 선택", 
                options=region_options,
                key="region_filter_widget",
                index=region_index,
                on_change=on_region_filter_change
            )

        # 처음 로드 시 필터 적용
        if search_button:
            apply_filters()
            
        # 필터링된 결과 표시
        st.dataframe(
            st.session_state.filtered_result, 
            use_container_width=True,
            hide_index=True
        )
        
        # 결과 개수 표시
        st.info(f"총 {len(st.session_state.filtered_result)}개의 결과가 있습니다.")
    elif search_button:
        st.warning("조회된 일정이 없습니다.")

if __name__ == "__main__":
    show_schedule_page() 