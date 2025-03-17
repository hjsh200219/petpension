import streamlit as st
from src.data import Public, Common
from src.ui import UI, BreedInfo
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.graph_objects as go
from src.data import Public, Common
import pydeck as pdk
import pandas as pd

def show_findmybreed(upkind):
    if upkind != '417000':
        st.warning(f"{upkind} 페이지는 준비중입니다.")
        return
    
    data_key = f"petinshelter_{upkind}"
    petinshelter = st.session_state.get(data_key, None)

    # 변수 초기화
    selected_breed = None

    # 반려동물 종류 입력 위젯
    col1, col2, col3 = st.columns((2,1,4))
    with col1:
        breed_input = st.text_input(
            "반려동물 종류를 입력하세요",
            placeholder="반려동물 종류를 입력하세요",
            key=f"{data_key}_breed_input",
            label_visibility="collapsed"
        )
    with col2:
        search_breed = st.button(
            "나의 반려동물 찾기",
            use_container_width=True,
            key=f"{data_key}_search_breed",
            type="secondary"
            )

    if breed_input or search_breed:
        breed_info = BreedInfo().search_breed(breed_input)
        if not breed_info.empty:
            if len(breed_info) > 1:
                st.info("검색 결과가 여러 개 있습니다. 품종을 선택해주세요.")
                selected_breed = st.radio(
                    "품종 선택", 
                    options=breed_info['품종'].tolist(),
                    horizontal=True,
                    label_visibility="collapsed"
                )
            else:
                selected_breed = breed_info['품종'].iloc[0]
        elif breed_info is not None:
            st.info("검색 결과가 없습니다. 다른 키워드로 검색해보세요.")
        
        if selected_breed:
            BreedInfo().show_breed_info(selected_breed, expandedoption=True)
            st.warning("임시보호소에서 보호 중인 검색한 품종을 찾아보세요.")
            show_breed_in_shelter(upkind, selected_breed)

def show_breed_in_shelter(upkind, selected_breed):
    col1, col2, col3 = st.columns((1,1,1))
    with col2:
        search_shelter = st.button(
            "임시보호소에서 찾기",
            key="search_shelter",
            use_container_width=True,
            type="primary"
        )
    if search_shelter:
        petinshelter = Public().show_petinshelter(upkind, data_key = None, refresh_button = None)
        petinshelter = petinshelter[petinshelter['kindCd'] == selected_breed]
        with st.expander("지도 보기", expanded=True):
            BreedInfo().show_map(petinshelter, radius=500)
        grid_response = BreedInfo().show_shelter_detail(petinshelter)            
        st.write(grid_response)
        BreedInfo().show_pet_detail(grid_response)

def show_findmybreed_page():
    st.subheader("🔍 나의 반려동물 찾기")

    tab1, tab2, tab3 = st.tabs(["강아지","고양이","기타"])
    with tab1:
        show_findmybreed(upkind='417000')

    with tab2:
        show_findmybreed(upkind='422400')

    with tab3:
        show_findmybreed(upkind='429900')
