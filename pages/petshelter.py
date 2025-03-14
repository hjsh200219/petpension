import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime, timedelta
from src.data import Public, Common
from src.ui import UI, BreedInfo
from pathlib import Path
from threading import Thread, Lock
import time
from tqdm import tqdm
import re
from st_aggrid import AgGrid, GridOptionsBuilder


public = Public()

def show_pet_list(upkind): 
    # 보호소 데이터 로드
    shelter_data_path = './static/database/보호소코드.csv'
    if os.path.exists(shelter_data_path):
        try:
            shelter_data = pd.read_csv(shelter_data_path, header=None, 
                                      names=['보호소코드', '보호소명', '시도코드', '시도명', '시군구코드', '시군구명', '주소', 'lat', 'lon'])
            shelter_data = shelter_data.drop_duplicates(subset=['보호소명'])
            shelter_to_sido = dict(zip(shelter_data['보호소명'], shelter_data['시도명']))
            shelter_to_sigungu = dict(zip(shelter_data['보호소명'], shelter_data['시군구명']))
        except Exception as e:
            st.warning(f"보호소 코드 데이터 로딩 중 오류: {str(e)}")
            shelter_to_sido = {}
            shelter_to_sigungu = {}
    else:
        st.warning("보호소 코드 데이터를 찾을 수 없습니다.")
        shelter_to_sido = {}
        shelter_to_sigungu = {}
    
    # 데이터 세션 상태 키
    data_key = f"pet_data_{upkind}"
    refresh_key = f"refresh_data_{upkind}"
    
    # 데이터 새로고침 버튼 처리
    col1, col2, col3 = st.columns(3)
    with col2:
        refresh_button = st.button("임시보호소 현황조회", key=refresh_key, use_container_width=True)
    
    # 데이터 가져오기 (새로고침 버튼을 누르거나 세션 상태에 데이터가 없는 경우에만)
    if refresh_button:
        with st.spinner("임시보호소 정보를 가져오고 있습니다..."):
            try:
                petinshelter = public.find_pet(upkind=upkind)
                petinshelter.to_csv('./static/database/petinshelter.csv', index=False)
                if petinshelter is not None and not petinshelter.empty:
                    petinshelter = petinshelter[
                        petinshelter['processState'].isin(["보호중", "공고중"])
                    ]
                    petinshelter = petinshelter[['desertionNo', 'happenDt', 'kindCd', 'age', 'sexCd', 'careNm']].copy()
                    
                    # 날짜 변환 및 오류 처리
                    petinshelter['happenDt'] = pd.to_datetime(petinshelter['happenDt'], errors='coerce').dt.strftime('%Y-%m-%d')
                    petinshelter = petinshelter.dropna(subset=['happenDt'])
                    
                    # 품종 정보 정리
                    petinshelter['kindCd'] = petinshelter['kindCd'].str.replace(
                        '[개]', ''
                    ).str.replace(
                        '[고양이]', ''
                    ).str.replace(
                        '[기타축종] ', ''
                    ).str.strip()
                    
                    # 보호소 이름으로 시도, 시군구 정보 추가
                    petinshelter['시도'] = petinshelter['careNm'].map(shelter_to_sido).fillna('정보 없음')
                    petinshelter['시군구'] = petinshelter['careNm'].map(shelter_to_sigungu).fillna('정보 없음')
                    
                    # 출생년도 추출 개선: 괄호 앞의 4자리 숫자 추출
                   
                    
                    # 출생년도 추출 및 년생 표시 생성
                    petinshelter['출생년도'] = petinshelter['age'].apply(UI().extract_birth_year)
                    petinshelter['년생'] = petinshelter.apply(
                        lambda row: f"{int(row['출생년도'])}년생" if pd.notna(row['출생년도']) else "", 
                        axis=1
                    )
                    
                    # 세션 상태에 데이터 저장
                    st.session_state[data_key] = petinshelter
                    
                    # 필터 상태 초기화 (새로고침 시)
                    if refresh_button:
                        filter_state_key = f"filter_state_{upkind}"
                        st.session_state[filter_state_key] = False
                        st.rerun()  # 페이지 새로고침
                else:
                    st.error("데이터를 가져오는 데 실패했습니다.")
                    # 이전 데이터가 없으면 빈 데이터프레임 생성
                    if data_key not in st.session_state:
                        st.session_state[data_key] = pd.DataFrame()
            except Exception as e:
                st.error(f"데이터 처리 중 오류가 발생했습니다: {str(e)}")
                # 이전 데이터가 없으면 빈 데이터프레임 생성
                if data_key not in st.session_state:
                    st.session_state[data_key] = pd.DataFrame()
    
    # 저장된 데이터 사용
    if data_key in st.session_state and not st.session_state[data_key].empty:
        # 저장된 데이터 가져오기
        petinshelter = st.session_state[data_key]
    
        # 필터 적용
        filtered_data = UI().apply_filters(petinshelter, upkind)
        
        # 필터링 결과 표시
        filter_state_key = f"filter_state_{upkind}"
        if st.session_state.get(filter_state_key, False):
            st.subheader(f"🐾 검색 결과 ({len(filtered_data):,}마리)")
        else:
            st.subheader(f"🐾 전체 목록 ({len(filtered_data):,}마리)")
        
        if filtered_data.empty:
            st.info("검색 조건에 맞는 동물이 없습니다.")
        else:
            with st.expander("지도 보기", expanded=True):
                BreedInfo().show_map(filtered_data)
            grid_response = BreedInfo().show_shelter_detail(filtered_data)            
            BreedInfo().show_pet_detail(grid_response)


def show_petshelter_page():
    tab1, tab2, tab3 = st.tabs(["강아지","고양이","기타"])
    with tab1:
        show_pet_list(upkind='417000')

    with tab2:
        show_pet_list(upkind='422400')

    with tab3:
        show_pet_list(upkind='429900')
