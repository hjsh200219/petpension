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
ui = UI()
breedinfo = BreedInfo()

def show_pet_list(upkind):     
    # 데이터 세션 상태 키
    data_key = f"pet_data_{upkind}"
    refresh_key = f"refresh_data_{upkind}"
    
    # 데이터 새로고침 버튼 처리
    col1, col2, col3 = st.columns(3)
    with col2:
        refresh_button = st.button("임시보호소 현황조회", key=refresh_key, use_container_width=True, type="primary")
    
    # 데이터 가져오기 (새로고침 버튼을 누르거나 세션 상태에 데이터가 없는 경우에만)
    if refresh_button:
        public.show_petinshelter(upkind, data_key, refresh_button)
    # 데이터가 없을 때만 안내 영역 표시
    elif data_key not in st.session_state or st.session_state[data_key].empty:
        with st.expander("필터 옵션 보기", expanded=False):
            st.write("검색 후 필터 옵션을 보고 조건을 선택해 검색 결과를 조정할 수 있습니다.", unsafe_allow_html=False)
        st.subheader("🐾 전체 목록")
        breedinfo.show_map_null()
        with st.expander("상세 정보 보기", expanded=False):
            st.write("검색 결과를 상세하게 표시합니다.", unsafe_allow_html=False)
        with st.expander("공고 정보", expanded=False):
            st.write("공고 정보를 확인할 수 있습니다.", unsafe_allow_html=False)
        with st.expander("품종 상세 정보", expanded=False):
            st.write("품종 상세 정보를 확인할 수 있습니다.", unsafe_allow_html=False)
        with st.expander("보호소 정보", expanded=False):
            st.write("보호소 정보를 확인할 수 있습니다.", unsafe_allow_html=False)
    
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
    st.subheader("📊 임시보호소 현황")
    tab1, tab2, tab3 = st.tabs(["강아지","고양이","기타"])
    with tab1:
        show_pet_list(upkind='417000')

    with tab2:
        show_pet_list(upkind='422400')

    with tab3:
        show_pet_list(upkind='429900')
