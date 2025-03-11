import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime, timedelta
from src.data import Public
from src.ui import UI
from pathlib import Path
from threading import Thread, Lock
import time
from tqdm import tqdm
import re

public = Public()

def total_count(upkind):
    total_count = public.totalCount(upkind=upkind)
    count_placeholder = st.empty()
    
    filter_state_key = f"filter_state_{upkind}"
    is_filter_applied = st.session_state.get(filter_state_key, False)
    
    if is_filter_applied:
        count_placeholder.subheader(f"🏠 전국에는 {total_count:,}마리가 보호 중입니다.")
    else:
        update_interval = max(1, total_count // 500)
        for i in range(0, total_count + 1, update_interval):
            time.sleep(0.001)
            count_placeholder.subheader(f"🏠 전국에는 {i:,}마리가 보호 중입니다.")

def apply_filters(data, upkind):
    """
    데이터에 필터를 적용하는 함수
    
    Parameters:
    - data: 필터링할 원본 데이터프레임
    - upkind: 동물 유형 코드(위젯 키를 고유하게 만들기 위해 사용)
    
    Returns:
    - filtered_data: 필터링된 데이터프레임
    """
    # 세션 상태 키 (위젯과 다른 키 사용)
    filter_state_key = f"filter_state_{upkind}"
    
    # 세션 상태 초기화
    if filter_state_key not in st.session_state:
        st.session_state[filter_state_key] = False
    
    # 필터 적용 버튼의 콜백 함수
    def set_filter_active():
        st.session_state[filter_state_key] = True
    
    # 필터 섹션을 숨김 처리된 expander로 생성
    with st.expander("🔍 필터 옵션 보기", expanded=False):
        # 필터 적용을 위한 데이터 준비
        all_kinds = sorted(data['kindCd'].unique().tolist())
        
        # 출생년도 처리 - 괄호 앞의 4자리 숫자 추출
        birth_years = []
        for year in data['출생년도'].dropna().unique():
            if year and str(year).isdigit() and len(str(year)) == 4:
                birth_years.append(year)
        all_birth_years = sorted([f"{int(y)}년생" for y in birth_years], reverse=True)
        
        all_sexes = sorted([s for s in data['sexCd'].unique().tolist() if s and s != ' '])
        all_sidos = sorted([s for s in data['시도'].unique().tolist() if s != '정보 없음'])
        
        # 날짜 필터 UI
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            min_date = data['happenDt'].min().date()
            max_date = data['happenDt'].max().date()
            
            date_from = st.date_input("발견일 시작", 
                                    value=min_date,
                                    min_value=min_date, 
                                    max_value=max_date,
                                    key=f"date_from_{upkind}")
        
        with col2:
            date_to = st.date_input("발견일 종료", 
                                   value=max_date,
                                   min_value=min_date, 
                                   max_value=max_date,
                                   key=f"date_to_{upkind}")
        
        with col3:
            selected_sido = st.selectbox("시도", 
                                       ["모든 지역"] + all_sidos,
                                       key=f"sido_{upkind}")
        
        with col4:
            if selected_sido != "모든 지역":
                filtered_sigungu = sorted(data[data['시도'] == selected_sido]['시군구'].unique().tolist())
                selected_sigungu = st.selectbox("시군구", 
                                              ["모든 시군구"] + filtered_sigungu,
                                              key=f"sigungu_{upkind}")
            else:
                selected_sigungu = "모든 시군구"

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            selected_kind = st.selectbox("품종", 
                                        ["모든 품종"] + all_kinds,
                                        key=f"kind_{upkind}")
        with col2:
            selected_birth_year = st.selectbox("출생년도", 
                                             ["모든 년도"] + all_birth_years,
                                             key=f"birth_year_{upkind}")
        with col3:
            selected_sex = st.selectbox("성별", 
                                      ["모두", "M", "F"],
                                      key=f"sex_{upkind}")
        
        col1, col2, col3 = st.columns(3)
        with col2:
            st.button("필터 적용", 
                     type="primary", 
                     use_container_width=True,
                 key=f"btn_filter_{upkind}",  # 버튼 위젯용 키 (세션 상태 키와 다름)
                 on_click=set_filter_active)  # 클릭 시 콜백 함수 호출
    
    # 필터가 활성화되지 않았다면 모든 데이터 반환
    if not st.session_state[filter_state_key]:
        return data
    
    # 필터 적용
    filtered_data = data.copy()
    
    # 날짜 필터 적용
    filtered_data = filtered_data[
        (filtered_data['happenDt'].dt.date >= date_from) & 
        (filtered_data['happenDt'].dt.date <= date_to)
    ]
    
    # 품종 필터 적용
    if selected_kind != "모든 품종":
        filtered_data = filtered_data[filtered_data['kindCd'] == selected_kind]
    
    # 년생 필터 적용
    if selected_birth_year != "모든 년도":
        # "년생" 텍스트 제거하고 숫자만 추출
        year_only = selected_birth_year.split('(')[0]
        filtered_data = filtered_data[filtered_data['출생년도'] == int(year_only)]
    
    # 성별 필터 적용
    if selected_sex != "모두":
        filtered_data = filtered_data[filtered_data['sexCd'] == selected_sex]
    
    # 시도 필터 적용
    if selected_sido != "모든 지역":
        filtered_data = filtered_data[filtered_data['시도'] == selected_sido]
        
        # 시군구 필터 적용
        if selected_sigungu != "모든 시군구":
            filtered_data = filtered_data[filtered_data['시군구'] == selected_sigungu]
    
    return filtered_data

def show_pet_list(upkind): 
    shelter_data_path = './static/database/보호소코드.csv'
    if os.path.exists(shelter_data_path):
        shelter_data = pd.read_csv(shelter_data_path, header=None, 
                                  names=['보호소코드', '보호소명', '시도코드', '시도명', '시군구코드', '시군구명'])
        shelter_data = shelter_data.drop_duplicates(subset=['보호소명'])
        shelter_to_sido = dict(zip(shelter_data['보호소명'], shelter_data['시도명']))
        shelter_to_sigungu = dict(zip(shelter_data['보호소명'], shelter_data['시군구명']))
    else:
        st.warning("보호소 코드 데이터를 찾을 수 없습니다.")
        shelter_to_sido = {}
        shelter_to_sigungu = {}
        
    with st.spinner("임시보호소 정보를 가져오고 있습니다..."):    
        petinshelter = public.find_pet(upkind=upkind)
        petinshelter = petinshelter[
            petinshelter['processState'].isin(["보호중", "공고중"])
        ]
        petinshelter = petinshelter[['happenDt', 'kindCd', 'age', 'sexCd', 'careNm']]
        
        petinshelter['happenDt'] = pd.to_datetime(
            petinshelter['happenDt']
        )
        petinshelter['happenDt_display'] = petinshelter['happenDt'].dt.strftime(
            '%Y-%m-%d'
        )
        petinshelter['kindCd'] = petinshelter['kindCd'].str.replace(
            '[개]', ''
        ).str.replace(
            '[고양이]', ''
        ).str.replace(
            '[기타축종] ', ''
        ).str.strip()
        
        petinshelter['시도'] = petinshelter['careNm'].map(shelter_to_sido).fillna('정보 없음')
        petinshelter['시군구'] = petinshelter['careNm'].map(shelter_to_sigungu).fillna('정보 없음')
        
        # 출생년도 추출 개선: 괄호 앞의 4자리 숫자 추출
        def extract_birth_year(age_string):
            if pd.isna(age_string) or not isinstance(age_string, str):
                return None
                
            # 연도 형식 추출을 위한 정규식 (연도가 문자열 시작에 위치)
            match = re.search(r'^(\d{4})', age_string.strip())
            if match:
                year = int(match.group(1))
                # 유효한 연도 범위 확인 (1990년부터 현재 연도까지)
                current_year = datetime.now().year
                if 1990 <= year <= current_year:
                    return year
            return None
        
        # 출생년도 추출 및 년생 표시 생성
        petinshelter['출생년도'] = petinshelter['age'].apply(extract_birth_year)
        petinshelter['년생'] = petinshelter['출생년도'].apply(lambda x: f"{int(x)}년생" if pd.notna(x) else "")
        
        filtered_data = apply_filters(petinshelter, upkind)
        
        filter_state_key = f"filter_state_{upkind}"
        if st.session_state.get(filter_state_key, False):
            st.subheader(f"🐾 검색 결과 ({len(filtered_data)}마리)")
        else:
            st.subheader(f"🐾 전체 목록 ({len(filtered_data):,}마리)")
        
        if filtered_data.empty:
            st.info("검색 조건에 맞는 동물이 없습니다.")
        else:
            display_data = filtered_data[['happenDt_display', 'kindCd', 'age', 'sexCd', 'careNm', '시도', '시군구']].copy()
            display_data.rename(columns={'happenDt_display': 'happenDt'}, inplace=True)
            
            st.dataframe(
                display_data, 
                hide_index=True, 
                use_container_width=True,
                column_config={
                    "happenDt": "발견일",
                    "kindCd": "품종",
                    "age": "출생년도",
                    "sexCd": "성별",
                    "careNm": "보호소",
                    "시도": "시도",
                    "시군구": "시군구",
                },
                column_order=['happenDt', 'kindCd', 'age', 'sexCd', 'careNm', '시도', '시군구']
            )

def show_petshelter_page():
    tab1, tab2, tab3 = st.tabs(["강아지","고양이","기타"])
    with tab1:
        show_pet_list(upkind='417000')

    with tab2:
        show_pet_list(upkind='422400')

    with tab3:
        show_pet_list(upkind='429900')




