import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from src.data import Naver
from src.ui import UI
from pathlib import Path
from threading import Thread, Lock
import time
from tqdm import tqdm

# 개발 모드에서만 캐싱 설정 비활성화
if os.environ.get('STREAMLIT_DEVELOPMENT', 'false').lower() == 'true':
    st.cache_data.clear()
    st.cache_resource.clear()

def show_schedule_page():
    # Naver 객체 생성
    st.subheader("🏠 반려동물 동반 숙박시설 조회")
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
    start_date, end_date, search_button = UI().show_date_range_selector(
        search_button_label="일정 조회"
    )

    # CSV 파일에서 데이터 읽기
    pension_info = pd.read_csv('./static/database/pension_info.csv')

    # 검색 버튼 클릭 시 데이터 로드
    if search_button:  
        # 새 검색 시 이전 결과 초기화
        st.session_state.result = pd.DataFrame()
        result = pd.DataFrame()
        
        # 스레드 결과를 저장할 리스트와 락 객체 생성
        all_results = []
        results_lock = Lock()
        
        # 스레드 진행 상황을 추적하기 위한 변수
        total_threads = len(pension_info)
        completed_threads = 0
        completed_lock = Lock()
        
        # 진행 상황 컨테이너 생성
        progress_container = st.empty()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 로딩 메시지 표시
        with st.spinner('데이터를 불러오는 중입니다. 잠시만 기다려주세요...'):
            # 스레드로 실행할 함수 정의
            def worker(row):
                nonlocal completed_threads
                
                businessId = str(row.businessId).strip()
                biz_item_id = str(row.bizItemId).strip()
                
                try:
                    schedule_data = naver.get_schedule(
                        businessId, 
                        biz_item_id, 
                        start_date.strftime("%Y-%m-%d"), 
                        end_date.strftime("%Y-%m-%d")
                    )
                    
                    # 결과가 있는 경우 리스트에 추가
                    if schedule_data is not None:
                        schedule_data['businessName'] = row.businessName
                        schedule_data['bizItemName'] = row.bizItemName
                        schedule_data['address'] = row.addressNew
                        
                        with results_lock:
                            all_results.append(schedule_data)
                    else:
                        # 메인 스레드에서 처리하도록 결과에 오류 정보 추가
                        with results_lock:
                            all_results.append({
                                'error': True,
                                'message': f"{row.businessName} - {row.bizItemName}의 일정을 가져오는데 실패했습니다.",
                                'businessName': row.businessName,
                                'bizItemName': row.bizItemName
                            })
                except Exception as e:
                    # 메인 스레드에서 처리하도록 결과에 오류 정보 추가
                    with results_lock:
                        all_results.append({
                            'error': True,
                            'message': f"{row.businessName} - {row.bizItemName}의 일정을 가져오는데 실패했습니다. 오류: {str(e)}",
                            'businessName': row.businessName,
                            'bizItemName': row.bizItemName
                        })
                
                # 진행 상황 업데이트 (직접 UI 업데이트하지 않음)
                with completed_lock:
                    completed_threads += 1
            
            # 스레드 생성 및 시작
            threads = []
            max_concurrent_threads = 10  # 최대 동시 스레드 수 제한
            active_threads = 0
            
            for row in pension_info.itertuples(index=False):
                # 최대 동시 스레드 수 제한 관리
                while active_threads >= max_concurrent_threads:
                    # 활성 스레드 수 확인
                    active_threads = sum(1 for t in threads if t.is_alive())
                    time.sleep(0.1)  # 잠시 대기
                
                # 새로운 스레드 생성 및 시작
                t = Thread(target=worker, args=(row,))
                t.start()
                threads.append(t)
                active_threads += 1
                
                # 메인 스레드에서 진행 상황 업데이트 (0.5초마다)
                if len(threads) % 5 == 0 or len(threads) == len(pension_info):
                    with completed_lock:
                        current_progress = completed_threads / total_threads
                    progress_bar.progress(current_progress)
                    status_text.text(f"처리 중: {completed_threads}/{total_threads} ({int(current_progress * 100)}%)")
                    time.sleep(0.1)  # UI 업데이트를 위한 짧은 대기
            
            # 모든 스레드가 완료될 때까지 대기하면서 진행 상황 업데이트
            while any(t.is_alive() for t in threads):
                with completed_lock:
                    current_progress = completed_threads / total_threads
                progress_bar.progress(current_progress)
                status_text.text(f"처리 중: {completed_threads}/{total_threads} ({int(current_progress * 100)}%)")
                time.sleep(0.5)  # 0.5초마다 업데이트
            
            # 모든 스레드가 완료될 때까지 대기
            for t in threads:
                t.join()
            
            # 진행 상황 완료 표시
            progress_bar.progress(1.0)
            status_text.text(f"완료: {total_threads}/{total_threads} (100%)")
            
            # 오류 메시지 표시 (메인 스레드에서)
            errors = [r for r in all_results if isinstance(r, dict) and r.get('error')]
            for error in errors:
                st.warning(error['message'], icon="⚠️")
                # 오류가 있는 항목을 all_results에서 제거
                all_results.remove(error)
            
            # 결과가 있으면 데이터프레임으로 변환
            if all_results:
                # 데이터프레임 형태의 결과만 처리
                df_results = [r for r in all_results if isinstance(r, pd.DataFrame)]
                if df_results:
                    result = pd.concat(df_results, ignore_index=True)
                    
                    # 결과를 필터링하고 필요한 열만 선택
                    filtered_result = result[
                        result['isSaleDay'] == True
                    ]
                    
                    filtered_result = filtered_result[
                        ['businessName', 'bizItemName', 'date', 'prices', 'address']
                    ].rename(columns={
                        'businessName': '숙박업소', 
                        'bizItemName': '숙박상품', 
                        'date': '날짜', 
                        'prices': '가격',
                        'address': '주소'
                    })
                    
                    result = filtered_result

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
        st.session_state.business_name_filter = st.session_state.숙박업소_filter_widget
        
        # 선택한 숙박업소가 변경되면 숙박상품 필터 초기화
        if st.session_state.business_name_filter != "전체":
            # 선택한 숙박업소에 해당하는 숙박상품만 필터링
            filtered_items = st.session_state.result[
                st.session_state.result['숙박업소'] == st.session_state.business_name_filter
            ]['숙박상품'].unique()
            
            # 세션 상태에 가능한 숙박상품 목록 저장
            st.session_state.available_items = ["전체"] + list(filtered_items)
            
            # 숙박상품 필터 초기화
            st.session_state.biz_item_name_filter = "전체"
            st.session_state.숙박상품_filter_widget = "전체"
        else:
            # 모든 숙박업소 선택 시 모든 숙박상품 표시
            st.session_state.available_items = ["전체"] + list(st.session_state.result['숙박상품'].unique())
        
        apply_filters()
        
    def on_item_filter_change():
        st.session_state.biz_item_name_filter = st.session_state.숙박상품_filter_widget
        apply_filters()
        
    def on_region_filter_change():
        st.session_state.region_filter = st.session_state.지역_filter_widget
        apply_filters()

    # 결과 표시 (검색 결과가 있는 경우)
    if not st.session_state.result.empty:
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
        
        # 처음 로드 시 가능한 숙박상품 목록 설정
        if 'available_items' not in st.session_state:
            st.session_state.available_items = ["전체"] + list(st.session_state.result['숙박상품'].unique())
        
        # 숙박업소와 지역 필터를 위한 UI 컴포넌트 생성
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 모든 숙박업소 옵션
            all_businesses = ["전체"] + list(st.session_state.result['숙박업소'].unique())
            selected_index = 0
            if st.session_state.business_name_filter in all_businesses:
                selected_index = all_businesses.index(st.session_state.business_name_filter)
                
            st.selectbox(
                "숙박업소 선택",
                options=all_businesses,
                key="숙박업소_filter_widget",
                index=selected_index,
                on_change=on_business_filter_change
            )
        
        with col2:
            # 선택한 숙박업소에 따라 필터링된 숙박상품 옵션
            available_items = st.session_state.available_items
            selected_index = 0
            if st.session_state.biz_item_name_filter in available_items:
                selected_index = available_items.index(st.session_state.biz_item_name_filter)
                
            st.selectbox(
                "숙박상품 선택",
                options=available_items,
                key="숙박상품_filter_widget",
                index=selected_index,
                on_change=on_item_filter_change
            )
        
        with col3:
            # 모든 지역 옵션
            all_regions = ["전체"] + list(st.session_state.result['지역'].unique())
            selected_index = 0
            if st.session_state.region_filter in all_regions:
                selected_index = all_regions.index(st.session_state.region_filter)
                
            st.selectbox(
                "지역 선택",
                options=all_regions,
                key="지역_filter_widget",
                index=selected_index,
                on_change=on_region_filter_change
            )

        # 처음 로드 시 필터 적용
        if search_button:
            apply_filters()

            
        # 필터링된 결과 표시
        try:
            grid_response = UI().show_dataframe_with_info(st.session_state.filtered_result)
            
            # 필터링된 결과 다운로드 버튼
            if not st.session_state.filtered_result.empty:
                csv = st.session_state.filtered_result.to_csv(index=False)
                st.download_button(
                    label="CSV로 다운로드",
                    data=csv,
                    file_name="pension_schedule.csv",
                    mime="text/csv",
                )
        except Exception as e:
            st.error(f"데이터 표시 중 오류가 발생했습니다: {str(e)}")
        
    elif search_button:
        st.warning("조회된 일정이 없습니다.")

if __name__ == "__main__":
    show_schedule_page() 