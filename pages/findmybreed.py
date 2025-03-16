import streamlit as st
from src.data import Public, Common
from src.ui import UI, BreedInfo
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.graph_objects as go
from src.data import Public, Common
import pydeck as pdk
import pandas as pd

def show_findmybreed_page():
    st.subheader("🔍 나의 반려동물 찾기")

    # 변수 초기화
    selected_breed = None

    # 반려동물 종류 입력 위젯
    col1, col2, col3 = st.columns((2,1,4))
    with col1:
        breed_input = st.text_input(
            "강아지 종류를 입력하세요",
            placeholder="반려동물 종류를 입력하세요",
            key="breed_input",
            label_visibility="collapsed"
        )
    with col2:
        search_breed = st.button(
            "나의 반려동물 찾기",
            key="search_breed",
            use_container_width=True,
            type="primary"
            )


    if breed_input:
        breed_info = BreedInfo().search_breed(breed_input)
        if (breed_info is not None and 
            isinstance(breed_info, pd.DataFrame) and 
            not breed_info.empty and 
            '품종' in breed_info.columns and 
            len(breed_info['품종']) > 0):
            
            if len(breed_info) > 1:
                st.info("검색 결과가 여러 개 있습니다. 품종을 선택해주세요.")
                selected_breed = st.radio(
                    "품종 선택", 
                    options=breed_info['품종'].tolist(),
                    horizontal=True
                )
            else:
                try:
                    selected_breed = breed_info['품종'].iloc[0]
                except Exception as e:
                    st.error(f"품종 정보를 가져오는 중 오류가 발생했습니다: {str(e)}")
        elif breed_info is not None:
            st.info("검색 결과가 없습니다. 다른 키워드로 검색해보세요.")

        if selected_breed:
            BreedInfo().show_breed_info(selected_breed, expandedoption=True)
            st.warning("임시보호소에서 보호 중인 검색한 품종을 찾아보세요.")
            col1, col2, col3 = st.columns((1,1,1))
            with col2:
                search_shelter = st.button(
                    "임시보호소에서 찾기",
                    key="search_shelter",
                    use_container_width=True
                )
            if search_shelter:
                upkind = '417000'
                petinshelter = Public().show_petinshelter(upkind, data_key = None, refresh_button = None)
                petinshelter = petinshelter[petinshelter['kindCd'] == selected_breed]
                st.write(petinshelter)
        

