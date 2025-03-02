import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from src.common import Naver, UI
from pathlib import Path

# 개발 모드에서만 캐싱 설정 비활성화
if os.environ.get('STREAMLIT_DEVELOPMENT', 'false').lower() == 'true':
    st.cache_data.clear()
    st.cache_resource.clear()

def show_schedule_page():
    # Naver 객체 생성
    st.subheader("🐾 반려동물 동반 숙박시설 조회")
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
        
    # 위젯에 대한 세션 상태 초기화
    if '숙박업소_filter_widget' not in st.session_state:
        st.session_state.숙박업소_filter_widget = "전체"
    
    if '숙박상품_filter_widget' not in st.session_state:
        st.session_state.숙박상품_filter_widget = "전체"
        
    if '지역_filter_widget' not in st.session_state:
        st.session_state.지역_filter_widget = "전체"
    
    # UI 컴포넌트 사용하여 날짜 선택기 표시
    start_date, end_date, search_button = UI.show_date_range_selector(
        search_button_label="일정 조회"
    )

    # CSV 파일에서 데이터 읽기
    pension_info = pd.read_csv('./static/pension_info.csv')

    # 검색 버튼 클릭 시 데이터 로드
    if search_button:  
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
            
            # schedule_data가 None인 경우 건너뜀
            if schedule_data is None:
                st.warning(
                    f"{row.businessName} - {row.bizItemName}의 일정을 가져오는데 실패했습니다."
                )
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

        st.session_state.result = result
        
        # 주소에서 지역 정보 추출
        def get_region_from_address(address):
            if pd.isna(address):
                return "미분류"
            
            regions = [
                "서울", "부산", "대구", "인천", "광주", 
                "대전", "울산", "세종", "경기", "강원", 
                "충북", "충남", "전북", "전남", "경북", 
                "경남", "제주"
            ]
            
            for region in regions:
                if region in address:
                    return region
            
            return "기타"
        
        # 지역 정보 추가
        if not result.empty and '주소' in result.columns:
            result['지역'] = result['주소'].apply(get_region_from_address)
            st.session_state.result = result
            
        # 검색 결과 저장 후 필터링된 결과도 초기화
        st.session_state.filtered_result = result
        # 필터값 초기화
        st.session_state.business_name_filter = "전체"
        st.session_state.biz_item_name_filter = "전체"
        st.session_state.region_filter = "전체"

        # 검색 결과를 CSV 파일로 저장 (통계 분석용)
        if not result.empty:
            # static 폴더가 없으면 생성
            static_dir = Path('./static')
            static_dir.mkdir(exist_ok=True)
            
            # 결과를 CSV 파일로 저장
            result.to_csv('./static/schedule_data.csv', index=False)

    # 필터링 함수 정의
    def apply_filters():
        filtered_data = st.session_state.result.copy()
        
        if st.session_state.business_name_filter != "전체":
            filtered_data = filtered_data[
                filtered_data['숙박업소'] == st.session_state.business_name_filter
            ]
            
        if st.session_state.biz_item_name_filter != "전체":
            filtered_data = filtered_data[
                filtered_data['숙박상품'] == st.session_state.biz_item_name_filter
            ]
            
        if st.session_state.region_filter != "전체":
            filtered_data = filtered_data[
                filtered_data['지역'] == st.session_state.region_filter
            ]
            
        st.session_state.filtered_result = filtered_data

    # 필터 변경 콜백 함수
    def on_business_filter_change():
        if st.session_state.business_name_filter != st.session_state.숙박업소_filter_widget:
            st.session_state.biz_item_name_filter = "전체"
        
        st.session_state.business_name_filter = st.session_state.숙박업소_filter_widget
        apply_filters()
        
    def on_item_filter_change():
        st.session_state.biz_item_name_filter = st.session_state.숙박상품_filter_widget
        apply_filters()
        
    def on_region_filter_change():
        st.session_state.region_filter = st.session_state.지역_filter_widget
        apply_filters()

    # 결과 표시 (검색 결과가 있는 경우)
    if not st.session_state.result.empty:
        st.success("일정 조회가 완료되었습니다.")
        
        # 필터 설정
        filter_values = {
            '숙박업소': st.session_state.business_name_filter,
            '숙박상품': st.session_state.biz_item_name_filter,
            '지역': st.session_state.region_filter
        }
        
        # 필터 콜백 함수
        filter_callbacks = {
            '숙박업소': on_business_filter_change,
            '숙박상품': on_item_filter_change,
            '지역': on_region_filter_change
        }
        
        # 컬럼 매핑
        column_mapping = {
            '숙박업소': '숙박업소',
            '숙박상품': '숙박상품',
            '지역': '지역'
        }
        
        # UI 컴포넌트 사용하여 필터링 UI 생성
        UI.create_filter_ui(
            data=st.session_state.result,
            filter_values=filter_values,
            on_change_callbacks=filter_callbacks,
            column_names=column_mapping
        )

        # 처음 로드 시 필터 적용
        if search_button:
            apply_filters()
            
        # 필터링된 결과 표시
        UI.show_dataframe_with_info(st.session_state.filtered_result)
        
        # 필터링된 결과 다운로드 버튼
        if not st.session_state.filtered_result.empty:
            csv = st.session_state.filtered_result.to_csv(index=False)
            st.download_button(
                label="CSV로 다운로드",
                data=csv,
                file_name="pension_schedule.csv",
                mime="text/csv",
            )
        
    elif search_button:
        st.warning("조회된 일정이 없습니다.")

if __name__ == "__main__":
    show_schedule_page() 