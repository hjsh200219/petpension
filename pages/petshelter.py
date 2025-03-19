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
    data_key = f"pet_data_{upkind}"
    refresh_key = f"refresh_data_{upkind}"

    col1, col2, col3 = st.columns(3)
    with col2:
        refresh_button = st.button("임시보호소 현황조회", key=refresh_key, use_container_width=True, type="primary")
    
    if refresh_button:
        ui.show_petinshelter(upkind, data_key, refresh_button)
    elif data_key not in st.session_state or st.session_state[data_key].empty:
        ui.show_preview()
    
    if data_key in st.session_state and not st.session_state[data_key].empty:
        petinshelter = st.session_state[data_key]
    
        filtered_data = UI().apply_filters(petinshelter, upkind)
        
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
