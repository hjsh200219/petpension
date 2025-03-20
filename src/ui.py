import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Callable, Optional, Union, Tuple
from src.settings import verify_password
from pathlib import Path
from src.data import Public
import time, random, string, re
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.graph_objects as go
from src.data import Public, Common
import pydeck as pdk
import pandas as pd
from streamlit_javascript import st_javascript

class UI:
    def __init__(self) -> None:
        pass
    
    def load_css(self):
        css_path = Path("./static/css/style.css")
        with open(css_path) as f:
            st.markdown(
                f'<style>{f.read()}</style>', 
                unsafe_allow_html=True
            )
        
    def is_mobile(self):        
        random_str = ''.join(random.choice(string.ascii_letters) for _ in range(8))
        unique_key = f"mobile_check_{random_str}_{time.time()}"
        
        if "is_mobile" not in st.session_state:
            width = st_javascript("window.innerWidth", key=unique_key)
            if width is None or width < 768:
                st.session_state.is_mobile = True
            else:
                st.session_state.is_mobile = False
        
        return st.session_state.is_mobile

    def display_banner(self):
        st.markdown(
            """
             <div class="banner">
                    <iframe 
                        src="https://ads-partners.coupang.com/widgets.html?id=842740&template=carousel&trackingCode=AF6451134&subId=&width=680&height=140&tsource=" 
                        frameborder="0" 
                        scrolling="no" 
                        referrerpolicy="unsafe-url" 
                        browsingtopics>
                    </iframe>
                </div>
            """,
            unsafe_allow_html=True
        )

    def display_footer(self):
        current_year = datetime.now().year
        st.markdown(
            f"""
            <div class="footer">
                <p>© {current_year} SH Consulting. All rights reserved.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    def add_input_focus_js(self, selector="input[type='password']", delay=800):
        js_code = f"""
        <script>
        setTimeout(function() {{
            const inputs = parent.document.querySelectorAll('{selector}');
            if (inputs.length > 0) {{
                inputs[0].focus();
            }}
        }}, {delay});
        </script>
        """
        st.components.v1.html(js_code, height=0)

    def create_password_input(self, on_change_callback: Callable, 
                            error_message: str = "비밀번호가 틀렸습니다. 다시 시도해주세요.",
                            has_error: bool = False,
                            placeholder: str = "비밀번호를 입력하세요",
                            key: str = "password_input"):
        self.add_input_focus_js()
        
        if has_error:
            st.error(error_message)
        
        col1, col2, col3 = st.columns((2,1,6))
        with col1:
            password = st.text_input(
                placeholder, 
                type="password", 
                key=key, 
                label_visibility="collapsed", 
                on_change=on_change_callback
            )
        with col2:
            st.button(
                "로그인", 
                key=f"{key}_button", 
                use_container_width=True,
                on_click=on_change_callback,
                type="primary"
            )
        
        return password

    def create_filter_ui(self, data: pd.DataFrame, 
                        filter_values: Dict[str, str], 
                        on_change_callbacks: Dict[str, Callable],
                        column_names: Dict[str, str]) -> None:
        filter_cols = st.columns(len(filter_values))
        
        for i, (filter_key, current_value) in enumerate(filter_values.items()):
            if filter_key not in column_names:
                continue
                
            display_name = column_names[filter_key]
            column_name = column_names[filter_key]
            
            options = ["전체"]
            if filter_key in data.columns:
                options.extend(list(data[filter_key].unique()))
            
            selected_index = 0
            if current_value in options:
                selected_index = options.index(current_value)
                
            with filter_cols[i]:
                st.selectbox(
                    f"{display_name} 선택",
                    options=options,
                    key=f"{filter_key}_filter_widget",
                    index=selected_index,
                    on_change=on_change_callbacks.get(filter_key, None)
                )

    def show_dataframe_with_info(self, df: pd.DataFrame, 
                                hide_index: bool = True, 
                                use_container_width: bool = True) -> None:

        if '가격' in df.columns:
            df['가격'] = df['가격'].apply(lambda x: "{:,.0f}".format(x) if pd.notnull(x) and isinstance(x, (int, float)) else x)

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_selection(selection_mode="single", use_checkbox=True)

        gb.configure_column("숙박업소", headerName="숙박업소", rowGroup=True, hide=True, checkboxSelection=False)
        grid_options = gb.build()
        
        grid_response = AgGrid(
                df,
                gridOptions=grid_options,
                enable_enterprise_modules=True,
            height=500,
                width='100%',
            fit_columns_on_grid_load=True,
            use_container_width = True
            )
        
        st.info(f"총 {len(df)}개의 결과가 있습니다.")

    def show_date_range_selector(self, default_start_date=None, 
                                default_end_date=None, 
                                search_button_label="검색") -> Tuple:
        if default_start_date is None:
            default_start_date = (datetime.now() + timedelta(days=1)).date()
            
        if default_end_date is None:
            default_end_date = (datetime.now() + timedelta(days=7)).date()
        
        col1, col2, col3, col4 = st.columns((1, 1, 1, 4))
        
        with col1:
            start_date = st.date_input(
                "시작 날짜", 
                default_start_date, 
                label_visibility="collapsed"
            )
            
        with col2:
            end_date = st.date_input(
                "종료 날짜", 
                default_end_date, 
                label_visibility="collapsed"
            )
            
        with col3:
            search_button = st.button(
                search_button_label, 
                use_container_width=True,
                type="primary"
            )
        
        return start_date, end_date, search_button
    
    def display_success_message(self, message=None):
        if message:
            st.success(message)
        elif st.session_state.get('success_message'):
            st.success(st.session_state.success_message)
            st.session_state.success_message = None
    
    def display_error_message(self, message):
        st.error(message)
    
    def create_date_region_selection(self):
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            default_start_date = datetime.now().date()
            start_date = st.date_input("시작일", default_start_date, key="start_date")
        
        with col2:
            default_end_date = (datetime.now() + timedelta(days=30)).date()
            end_date = st.date_input("종료일", default_end_date, key="end_date")
        
        with col3:
            selected_region = st.selectbox("지역 선택", ["전체"], key="region")
        
        return start_date, end_date, selected_region
    
    def create_pension_selection(self, pensions, default=None, key="selected_pensions"):
        st.write("비교할 펜션 선택 (복수 선택 가능)")
        selected_pensions = st.multiselect(
            "펜션 선택",
            options=pensions,
            default=default if default is not None else pensions,
            key=key
        )
        return selected_pensions
    
    def create_chart_type_selection(self, current_type="bar"):
        chart_type = st.radio(
            "차트 유형 선택:",
            options=["바 차트", "히트맵", "레이더 차트"],
            index=0 if current_type == "bar" else 
                  1 if current_type == "heatmap" else 2,
            horizontal=True,
            key="chart_type_radio"
        )
        
        if chart_type == "바 차트":
            return "bar"
        elif chart_type == "히트맵":
            return "heatmap"
        else:
            return "radar"
    
    def create_logout_button(self, key="logout"):
        if st.button("로그아웃", key=key, type="primary"):
            st.session_state.password_verified = False
            st.rerun()
    
    def verify_user_password(self, password_field_key="password_input", session_key="password_verified", error_key="password_error", password_verify_function=None):
        st.session_state.setdefault(session_key, False)
        st.session_state.setdefault(error_key, False)
        
        def check_password():
            password = st.session_state[password_field_key]
            if password_verify_function:
                verified = password_verify_function(password)
            else:
                verified = (password == "1234")
            
            st.session_state[session_key] = verified
            st.session_state[error_key] = not verified
        
        if st.session_state[session_key]:
            return True
        
        st.subheader("🔒 로그인")
        UI().create_password_input(
            on_change_callback=check_password,
            has_error=st.session_state[error_key],
            key=password_field_key
        )
        
        return st.session_state[session_key]
    
    def create_progress_bar(self):
        return st.progress(0)
    
    def create_analysis_button(self):
        return st.button("분석 시작", use_container_width=True, key="analyze_button")
    
    def create_expandable_detail_section(self, title, dataframe, columns=None):
        with st.expander(title):
            if columns:
                st.dataframe(dataframe[columns], use_container_width=True, hide_index=True)
            else:
                st.dataframe(dataframe, use_container_width=True, hide_index=True)
    
    def display_detailed_data(self, data, display_columns, title="상세 데이터 보기", sort_by=None):
        with st.expander(title):
            if sort_by:
                sorted_data = data.sort_values(sort_by)
            else:
                sorted_data = data
            
            st.dataframe(
                sorted_data[display_columns], 
                use_container_width=True, 
                hide_index=True
            )

    def total_count(self, upkind):
        total_count = Public().totalCount(upkind=upkind)
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
    
    def show_preview(self):
        with st.expander("필터 옵션 보기", expanded=False):
            st.write("검색 후 필터 옵션을 보고 조건을 선택해 검색 결과를 조정할 수 있습니다.", unsafe_allow_html=False)
        st.info("조회 결과가 없습니다.")
        BreedInfo().show_map_null()
        with st.expander("상세 정보 보기", expanded=False):
            st.write("검색 결과를 상세하게 표시합니다.", unsafe_allow_html=False)
        with st.expander("공고 정보", expanded=False):
            st.write("공고 정보를 확인할 수 있습니다.", unsafe_allow_html=False)
        with st.expander("품종 상세 정보", expanded=False):
            st.write("품종 상세 정보를 확인할 수 있습니다.", unsafe_allow_html=False)
        with st.expander("보호소 정보", expanded=False):
            st.write("보호소 정보를 확인할 수 있습니다.", unsafe_allow_html=False)

    def show_petinshelter(self, upkind, data_key = None, refresh_button = None):
        with st.spinner("보호소 정보를 가져오고 있습니다..."):
            try:
                petinshelter = Public().find_pet(upkind=upkind)
                petinshelter.to_csv('./static/database/petinshelter.csv', index=False)
                if petinshelter is not None and not petinshelter.empty:
                    petinshelter = petinshelter[
                        petinshelter['processState'].isin(["보호중", "공고중"])
                    ]
                    petinshelter = petinshelter[['desertionNo', 'happenDt', 'kindCd', 'age', 'sexCd', 'careNm']].copy()
                    
                    petinshelter['happenDt'] = pd.to_datetime(petinshelter['happenDt'], errors='coerce').dt.strftime('%Y-%m-%d')
                    petinshelter = petinshelter.dropna(subset=['happenDt'])
                    
                    petinshelter['kindCd'] = petinshelter['kindCd'].str.replace('[개]', '').str.replace('[고양이]', '').str.replace('[기타축종] ', '').str.strip()
                    
                    if not Public().shelter_to_sido:
                        st.warning("시도 매핑 정보가 비어 있습니다. 시도 정보를 '정보 없음'으로 설정합니다.")
                        petinshelter['시도'] = '정보 없음'
                    else:
                        petinshelter['시도'] = petinshelter['careNm'].map(Public().shelter_to_sido)
                        
                        missing_sido = petinshelter['시도'].isna().sum()
                        if missing_sido > 0:
                            st.warning(f"{missing_sido}개의 보호소에 시도 정보가 매핑되지 않았습니다.")
                            
                            missing_shelters = petinshelter.loc[petinshelter['시도'].isna(), 'careNm'].unique()
                            if len(missing_shelters) > 0:
                                sample_missing = missing_shelters[:min(5, len(missing_shelters))]
                                st.warning(f"매핑되지 않은 보호소 예시: {', '.join(sample_missing)}")
                                
                                for shelter_name in sample_missing:
                                    similar_names = [name for name in Public().shelter_to_sido.keys() 
                                                    if shelter_name in name or name in shelter_name]
                                    if similar_names:
                                        st.info(f"'{shelter_name}'와(과) 비슷한 이름: {', '.join(similar_names[:3])}")
                        
                        petinshelter['시도'] = petinshelter['시도'].fillna('정보 없음')
                    
                    if not Public().shelter_to_sigungu:
                        petinshelter['시군구'] = '정보 없음'
                    else:
                        petinshelter['시군구'] = petinshelter['careNm'].map(Public().shelter_to_sigungu).fillna('정보 없음')                  
                    
                    petinshelter['출생년도'] = petinshelter['age'].apply(Public().extract_birth_year)
                    petinshelter['년생'] = petinshelter.apply(
                        lambda row: f"{int(row['출생년도'])}년생" if pd.notna(row['출생년도']) else "", 
                        axis=1
                    )
                    st.session_state[data_key] = petinshelter
                    
                    if refresh_button:
                        filter_state_key = f"filter_state_{upkind}"
                        st.session_state[filter_state_key] = False
                        st.rerun()
                else:
                    st.error("데이터를 가져오는 데 실패했습니다.")
                    if data_key not in st.session_state:
                        st.session_state[data_key] = pd.DataFrame()
            except Exception as e:
                st.error(f"데이터 처리 중 오류가 발생했습니다: {str(e)}")
                if data_key not in st.session_state:
                    st.session_state[data_key] = pd.DataFrame()
        return petinshelter

    def apply_filters(self, data, upkind):
        filter_state_key = f"filter_state_{upkind}"
        
        if filter_state_key not in st.session_state:
            st.session_state[filter_state_key] = False
        
        def set_filter_active():
            st.session_state[filter_state_key] = True
        
        with st.expander("🔍 필터 옵션 보기", expanded=False):
            all_kinds = sorted(data['kindCd'].unique().tolist())
            
            birth_years = []
            if '출생년도' in data.columns:
                for year in data['출생년도'].dropna().unique():
                    if pd.notna(year) and str(year).isdigit() and len(str(int(year))) == 4:
                        birth_years.append(int(year))
            
            all_birth_years = sorted([f"{y}년생" for y in birth_years], reverse=True) if birth_years else []
            
            all_sexes = sorted([s for s in data['sexCd'].unique().tolist() if s and s != ' '])
            all_sidos = sorted([s for s in data['시도'].unique().tolist() if s != '정보 없음'])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                min_date = pd.to_datetime(data['happenDt'].min()).date().strftime('%Y-%m-%d')
                max_date = pd.to_datetime(data['happenDt'].max()).date().strftime('%Y-%m-%d')
                
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
                    key=f"btn_filter_{upkind}",  
                    on_click=set_filter_active)  
        
        if not st.session_state[filter_state_key]:
            return data
        
        filtered_data = data.copy()
        
        filtered_data['happenDt'] = pd.to_datetime(filtered_data['happenDt'], errors='coerce')

        filtered_data = filtered_data[
            (filtered_data['happenDt'].dt.date >= date_from) & 
            (filtered_data['happenDt'].dt.date <= date_to)
        ]
        
        if selected_kind != "모든 품종":
            filtered_data = filtered_data[filtered_data['kindCd'] == selected_kind]
        
        if selected_birth_year != "모든 년도" and '출생년도' in filtered_data.columns:
            try:
                year_only = selected_birth_year.replace('년생', '').strip()
                if year_only.isdigit():
                    year_value = int(year_only)
                    filtered_data = filtered_data[filtered_data['출생년도'] == year_value]
            except Exception as e:
                st.error(f"출생년도 필터링 중 오류 발생: {str(e)}")
        
        if selected_sex != "모두":
            filtered_data = filtered_data[filtered_data['sexCd'] == selected_sex]
        
        if selected_sido != "모든 지역":
            filtered_data = filtered_data[filtered_data['시도'] == selected_sido]
            
            if selected_sigungu != "모든 시군구":
                filtered_data = filtered_data[filtered_data['시군구'] == selected_sigungu]
        
        filtered_data['happenDt'] = filtered_data['happenDt'].dt.strftime('%Y-%m-%d')
        
        return filtered_data
    
class BreedInfo:
    def __init__(self) -> None:
        self.breed_info = pd.read_csv('./static/database/akcBreedInfo.csv')
        self.trait_info = pd.read_csv('./static/database/akcTraits.csv')
        self.trait_averages = pd.read_csv('./static/database/trait_averages.csv')

    def display_text_input(self, label, value, col):
        with col:
            unique_key = f"breed_info_{label}_{id(self)}_{id(col)}"
            st.text_input(label, disabled=True, value=value, key=unique_key)
    
    def show_shelter_detail(self, filtered_data, breed = None):
        display_columns = ['시도', 'careNm', '시군구', 'desertionNo', 'happenDt', 'kindCd', 'age', 'sexCd']
        if breed:
            filtered_data = filtered_data[filtered_data['kindCd'].str.contains(breed)]
        display_data = filtered_data[display_columns].copy()

        display_data = display_data.sort_values(by='시도', ascending=True)

        gb = GridOptionsBuilder.from_dataframe(display_data)
        gb.configure_selection(selection_mode="single", use_checkbox=True)


        if st.session_state.is_mobile == False:
            gb.configure_column("시도", headerName="시도", use_checkbox=True)
            gb.configure_column("시군구", headerName="시군구", use_checkbox=True)
            gb.configure_column("desertionNo", headerName="유기번호", use_checkbox=True)
            gb.configure_column("happenDt", headerName="발견일", use_checkbox=True)
            gb.configure_column("kindCd", headerName="품종", use_checkbox=True)
            gb.configure_column("age", headerName="나이", use_checkbox=True)
            gb.configure_column("sexCd", headerName="성별", use_checkbox=True)
            gb.configure_column("careNm", headerName="보호소", use_checkbox=True)
        else:
            gb.configure_column("시도", headerName="시도", use_checkbox=True)
            gb.configure_column("시군구", headerName="시군구", use_checkbox=True, hide=True)
            gb.configure_column("desertionNo", headerName="유기번호", use_checkbox=True, hide = True)
            gb.configure_column("happenDt", headerName="발견일", use_checkbox=True, hide = True)
            gb.configure_column("kindCd", headerName="품종", use_checkbox=True)
            gb.configure_column("age", headerName="나이", use_checkbox=True, hide = True)
            gb.configure_column("sexCd", headerName="성별", use_checkbox=True, hide=True)
            gb.configure_column("careNm", headerName="보호소", use_checkbox=True)

        grid_options = gb.build()

        grid_response = AgGrid(
            display_data,
            gridOptions=grid_options,
            enable_enterprise_modules=False,
            height=600,
            width='100%',
            fit_columns_on_grid_load=True,
            use_container_width = True
        )

        return grid_response
    
    def show_map(self, petinshelter, radius=30):
        shelterlist = pd.read_csv('./static/database/보호소코드.csv')
        shelterlist = shelterlist[shelterlist['주소'].notna()]

        shelterlist['count_pet'] = shelterlist['보호소명'].map(petinshelter['careNm'].value_counts())

        with st.spinner("보호소의 위경도 정보를 업데이트 중입니다..."):
            for index, row in shelterlist.iterrows():
                if pd.isna(row['lat']) or pd.isna(row['lon']):
                    lat, lon = Common().convert_gps(row['주소'])
                    shelterlist.loc[index, 'lat'] = lat
                    shelterlist.loc[index, 'lon'] = lon

        shelterlist.to_csv('./static/database/보호소코드.csv', index=False)
        
        shelterlist_status = shelterlist[['보호소명', 'count_pet', '주소', 'lat', 'lon']]
        shelterlist_status = shelterlist_status.dropna(subset=['count_pet'])
        
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=shelterlist_status,
            get_position='[lon, lat]',
            get_fill_color='[255, 0, 0, 160]',
            get_radius=f'count_pet * {radius}',
            pickable=True,
        )
        
        view_state = pdk.ViewState(
            latitude=37.515586, 
            longitude=127.056992,
            zoom=9,
            pitch=0,
        )
        
        tooltip = {
            "html": "<b>보호소:</b> {보호소명} <br/><b>보호 중:</b> {count_pet}<br/><b>보호 중:</b> {주소}",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }
        
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip
        )
        
        st.pydeck_chart(deck)

    def show_map_null(self):
        map_df = pd.DataFrame()

        with st.expander("지도 보기", expanded=False):
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=map_df,
                get_position='[lon, lat]',
                get_fill_color='[255, 0, 0, 160]',
                get_radius='cc_name_count * 100',
                pickable=True,
            )
            
            view_state = pdk.ViewState(
                latitude=37.5, 
                longitude=126.9,
                zoom=8,
                pitch=0,
            )
            
            deck = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
            )
            
            st.pydeck_chart(deck)

    def show_pet_detail(self, grid_response):
        selected = grid_response.get('selected_rows', [])
        if selected is None or len(selected) == 0:
            return
        
        try:
            if isinstance(selected, pd.DataFrame):
                if len(selected) == 0:
                    return
                first_row = selected.iloc[0].to_dict()
            else:
                if len(selected) == 0:
                    return
                first_row = selected[0]
                
            if 'desertionNo' not in first_row:
                st.warning("개별 유기번호를 선택해주세요.")
                return
                
            desertion_no = int(first_row['desertionNo'])
            petinshelter = pd.read_csv('./static/database/petinshelter.csv')
            selected_pet = petinshelter[petinshelter['desertionNo'] == desertion_no]
    
            if len(selected_pet) == 0:
                st.warning(f"유기번호 {desertion_no}에 해당하는 데이터를 찾을 수 없습니다.")
                return
                
        except Exception as e:
            st.error(f"데이터 처리 중 오류가 발생했습니다: {str(e)}")
            st.write("selected 타입:", type(selected))
            if hasattr(selected, 'shape'):
                st.write("selected 형태:", selected.shape)
            return

        self.show_notice_info(selected_pet)
        self.show_pet_info(selected_pet)

        if 'kindCd' in selected_pet.columns:
            kindCd = selected_pet['kindCd'].iloc[0]
            if isinstance(kindCd, str):
                kindCd = kindCd.replace("[개]", "").replace("[고양이]", "").replace("[기타축종]", "").strip()
            kindCd = self.kindCd_mapping(kindCd)
            self.show_breed_info(kindCd)
        else:
            st.warning("품종 정보를 찾을 수 없습니다.")

        self.show_shelter_info(selected_pet)
    
    def show_pet_info(self, selected_pet):
        with st.expander("보호동물 상세 정보", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.image(selected_pet['popfile'].iloc[0], use_container_width=True)
                st.markdown('<style>img { max-height: 500px; }</style>', unsafe_allow_html=True)
                st.markdown('<style>img { object-fit: contain; }</style>', unsafe_allow_html=True)
                self.display_text_input('나이', selected_pet['age'].iloc[0], col2)
                self.display_text_input('체중', selected_pet['weight'].iloc[0], col2)
                self.display_text_input('성별', selected_pet['sexCd'].iloc[0], col2)
                self.display_text_input('색상', selected_pet['colorCd'].iloc[0], col3)
                self.display_text_input('중성화 여부', selected_pet['neuterYn'].iloc[0], col3)
                self.display_text_input('특징', selected_pet['specialMark'].iloc[0], col3)
            
    def show_notice_info(self, selected_pet):
        with st.expander("공고정보", expanded=False):
            col1, col2, col3 = st.columns((1, 1, 2))
            self.display_text_input('유기번호', str(selected_pet['desertionNo'].iloc[0]), col1)
            self.display_text_input('접수일', selected_pet['happenDt'].iloc[0], col2)
            self.display_text_input('발견장소', selected_pet['happenPlace'].iloc[0], col3)
            
            col1, col2, col3, col4 = st.columns((1, 1, 1, 1))
            self.display_text_input('공고번호', selected_pet['noticeNo'].iloc[0], col1)
            self.display_text_input('공고시작일', selected_pet['noticeSdt'].iloc[0], col2)
            self.display_text_input('공고종료일', selected_pet['noticeEdt'].iloc[0], col3)
            self.display_text_input('상태', selected_pet['processState'].iloc[0], col4)
            
    def kindCd_mapping(self, kindCd):
        if kindCd is None or not isinstance(kindCd, str) or kindCd.strip() == '':
            return ""
            
        kindCd_mapping = {
            "푸들": "스탠다드 푸들"
        }
        
        kindCd = kindCd_mapping.get(kindCd, kindCd)
        kindCd = kindCd.replace("믹스", "").replace("잡종", "").strip()
        return kindCd

    def show_breed_info(self, kindCd, expandedoption=True, matching_score=False):
        if kindCd is None or kindCd == "":
            st.info("품종 정보가 없습니다.")
            return
            
        with st.expander(f"{kindCd} 상세 정보", expanded=expandedoption):
            if matching_score:
                
                col1, col2 = st.columns([2, 6])
                with col1:
                    st.subheader(kindCd)
                with col2:
                    st.subheader(f"매칭 점수: {matching_score:.1f}%")

            col2, col3, col4 = st.columns([1, 1, 1])            
            if kindCd in self.breed_info['breed_name_kor'].values:
                height, weight, life_expectancy = self.get_breed_info_basic(kindCd)
                
                if isinstance(height, pd.Series):
                    height = [str(h) for h in height]
                    height = ', '.join(height) if height else ""
                elif height is not None:
                    height = str(height)
                else:
                    height = ""
                    
                if isinstance(weight, pd.Series):
                    weight = [str(w) for w in weight]
                    weight = ', '.join(weight) if weight else ""
                elif weight is not None:
                    weight = str(weight)
                else:
                    weight = ""
                    
                if isinstance(life_expectancy, pd.Series):
                    life_expectancy = [str(le) for le in life_expectancy]
                    life_expectancy = ', '.join(life_expectancy) if life_expectancy else ""
                elif life_expectancy is not None:
                    life_expectancy = str(life_expectancy)
                else:
                    life_expectancy = ""

                self.display_text_input('키', height, col2)
                self.display_text_input('체중', weight, col3)
                self.display_text_input('기대수명', life_expectancy, col4)
            else:
                self.display_text_input('키', "", col2)
                self.display_text_input('체중', "", col3)
                self.display_text_input('기대수명', "", col4)

            tab0, tab1, tab2, tab3, tab4 = st.tabs(["How to read", "Fmaily Life", "Physical", "Social", "Personality"])
            with tab0:
                self.show_breed_trait_5scale_example()
                
            with tab1:
                col1, col2 = st.columns([1, 1])
                with col1:
                    self.show_breed_trait_5scale(kindCd, 'Affectionate With Family')
                with col2:
                    self.show_breed_trait_5scale(kindCd, 'Good With Young Children')
                with col1:
                        self.show_breed_trait_5scale(kindCd, 'Good With Other Dogs')
            
            with tab2:
                col1, col2 = st.columns([1, 1])
                with col1:
                    self.show_breed_trait_5scale(kindCd, 'Shedding Level')
                with col2:
                    self.show_breed_trait_5scale(kindCd, 'Coat Grooming Frequency')
                with col1:
                    self.show_breed_trait_5scale(kindCd, 'Drooling Level')
                self.show_breed_trait_hair(kindCd)
            
            with tab3:
                col1, col2 = st.columns([1, 1])
                with col1:
                    self.show_breed_trait_5scale(kindCd, 'Openness To Strangers')
                with col2:
                    self.show_breed_trait_5scale(kindCd, 'Playfulness Level')
                with col1:
                    self.show_breed_trait_5scale(kindCd, 'Watchdog/Protective Nature')
                with col2:
                    self.show_breed_trait_5scale(kindCd, 'Adaptability Level')

            with tab4:
                col1, col2 = st.columns([1, 1])
                with col1:
                    self.show_breed_trait_5scale(kindCd, 'Trainability Level')
                with col2:
                    self.show_breed_trait_5scale(kindCd, 'Energy Level')
                with col1:
                    self.show_breed_trait_5scale(kindCd, 'Barking Level')
                with col2:
                    self.show_breed_trait_5scale(kindCd, 'Mental Stimulation Needs')

    def show_shelter_info(self, selected_pet):
        with st.expander("보호소 정보", expanded=False):
            col1, col2, col3 = st.columns((1, 1, 2))
            self.display_text_input('보호소', selected_pet['careNm'].iloc[0], col1)
            self.display_text_input('보호소 전화번호', selected_pet['careTel'].iloc[0], col2)
            self.display_text_input('보호소 주소', selected_pet['careAddr'].iloc[0], col3)

            col1, col2, col3, col4 = st.columns((1, 1, 1, 1))
            self.display_text_input('관할기관', selected_pet['orgNm'].iloc[0], col1)
            self.display_text_input('담당자', selected_pet['chargeNm'].iloc[0], col2)
            self.display_text_input('담당자연락처', selected_pet['officetel'].iloc[0], col3)

    def get_breed_info_basic(self, breed_name):
        if breed_name not in self.breed_info['breed_name_kor'].values:
            return "", "", ""
            
        selected_breed = self.breed_info[self.breed_info['breed_name_kor'] == breed_name]
        
        if selected_breed.empty:
            return "", "", ""
            
        try:
            height = selected_breed['height_k']
            weight = selected_breed['weight_k']
            life_expectancy = selected_breed['life_expectancy_k']
            
            return height, weight, life_expectancy
        except Exception as e:
            st.error(f"기본 정보 조회 중 오류 발생: {str(e)}")
            return "", "", ""
    
    def show_breed_trait_5scale_example(self):
        st.write("##### 속성 점수를 이해하는 방법")
        scores = [2, 4]
        average_scores = [4.5, 2.5]
        trait_desc = """속성에 대한 설명이 이 영역에 표시됩니다. 
        ex. 훈련에 얼마나 잘 반응하며 새로운 것을 배우려는 의지가 어느 정도인지를 나타냅니다.
        일부 품종은 주인을 기쁘게 하려고 노력하지만, 다른 품종은 자기 주장이 강해 스스로 원하는 대로 행동합니다."""
        score_low = "낮은 점수의 의미"
        score_high = "높은 점수의 의미"
        traits = ["속성 이름(1)", "속성 이름(2)"]
        is_mobile = UI().is_mobile()

        def column_1(i, traits, score_low, score_high, scores):
            st.write(f"<span style='color:gray;'>{traits[i]}</span>", unsafe_allow_html=True)
            st.write(f"<span style='color:gray;'>{score_low}</span>", unsafe_allow_html=True)
            st.write(f"<span style='color:gray;'>{score_high}</span>", unsafe_allow_html=True)
            st.write(f"<span style='color:gray;'>{scores[i]}</span>", unsafe_allow_html=True)
            delta = scores[i] - average_scores[i]
            color = 'red' if delta < 0 else 'green'
            st.markdown(f"<span style='color:{color};'>&#9660; {delta}</span> ", unsafe_allow_html=True)
            st.write("<span style='color:red;'>|</span>", unsafe_allow_html=True)
            st.write(f"<span style='color:gray;'>{trait_desc[:9]}...</span>", unsafe_allow_html=True)

        def column_2_mobile(score_low, score_high, scores, average_scores):
            st.write(f"{traits[i]}<code>속성 이름</code>", unsafe_allow_html=True)
            st.write(f"{score_low}<code>속성의 점수가 낮을 때의 품종이 어떤 성향을 가지는지 설명</code>", unsafe_allow_html=True)
            st.write(f"{score_high}<code>속성의 점수가 높을 때의 품종이 어떤 성향을 가지는지 설명</code>", unsafe_allow_html=True)
            st.write(f"{scores[i]}<code>해당 품종의 속성 점수</code>", unsafe_allow_html=True)
            delta = scores[i] - average_scores[i]
            color = 'red' if delta < 0 else 'green'
            st.markdown(f"<span style='color:{color};'>&#9660; {delta}</span><code>다른 품종의 평균 대비 상대 점수</code>", unsafe_allow_html=True)
            st.write(f"<span style='color:red;'>|</span><code>다른 품종의 평균 점수를 그래프에 표시</code>", unsafe_allow_html=True)
            st.write(f"{trait_desc[:9]}...<code>품종의 특성에 대한 설명</code>", unsafe_allow_html=True)
        
        def column_2():
            st.write("<code>속성 이름</code>", unsafe_allow_html=True)
            st.write("<code>속성의 점수가 낮을 때의 품종이 어떤 성향을 가지는지 설명</code>", unsafe_allow_html=True)
            st.write("<code>속성의 점수가 높을 때의 품종이 어떤 성향을 가지는지 설명</code>", unsafe_allow_html=True)
            st.write("<code>해당 품종의 속성 점수</code>", unsafe_allow_html=True)
            st.write("<code>다른 품종의 평균 대비 상대 점수</code>", unsafe_allow_html=True)
            st.write("<code>다른 품종의 평균 점수를 그래프에 표시</code>", unsafe_allow_html=True)
            st.write("<code>품종의 특성에 대한 설명</code>", unsafe_allow_html=True)

        def figure(i, traits, score_low, score_high, scores, average_scores):
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=scores[i],
                title={'text': traits[i]},
                gauge={
                    'axis': {'range': [1, 5],
                            'tickmode': "array",
                            "tickvals": [1, 2, 3, 4, 5],
                            "ticktext": [f"{score_low}", "", "", "", f"{score_high}"]},
                    'bar': {'color': "blue"},
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': average_scores[i]
                    }
                },
                delta={'reference': average_scores[i]}
            ))

            fig.update_layout(
                height=200,
                margin=dict(t=60, b=10, l=10, r=10),
                autosize=False,
                font=dict(size=16, color="gray")
            )

            unique_key = f"example_plot_{i}_{id(self)}_{id(col1)}"
            st.plotly_chart(fig, use_container_width=True, key=unique_key)
            st.write(f"<span style='color:gray;'>{trait_desc}</span>", unsafe_allow_html=True)

        if is_mobile == False:
            for i in range(2):
                col1, col2 = st.columns([1, 1])
                with col1:
                    figure(i, traits, score_low, score_high, scores, average_scores)

                with col2:
                    col2_1, col2_2 = st.columns([1, 3])
                    with col2_1:
                        column_1(i, traits, score_low, score_high, scores)
                    with col2_2:
                        column_2()

                if i != len(scores) - 1:
                    st.divider()
        else:
            for i in range(1):
                col1, col2 = st.columns([1, 1])
                with col1:
                    figure(i, traits, score_low, score_high, scores, average_scores)
                with col2:
                    column_2_mobile(score_low, score_high, scores, average_scores)

    def show_breed_trait_5scale(self, breed_name, trait):
        if breed_name not in self.breed_info['breed_name_kor'].values:
            st.info(f"{breed_name} 품종에 대한 정보가 없습니다.")
            return
        
        filtered_data = self.breed_info.loc[self.breed_info['breed_name_kor'] == breed_name, trait]
        trait_name = self.trait_info.loc[self.trait_info['trait'] == trait, 'trait_ko'].values[0]
        
        if filtered_data.empty:
            st.info(f"{breed_name} 품종의 '{trait_name}' 속성 정보가 없습니다.")
            return
        
        score = filtered_data.values[0]
        trait_desc = self.trait_info.loc[self.trait_info['trait'] == trait, 'trait_desc_ko'].values[0]
        score_low = self.trait_info.loc[self.trait_info['trait'] == trait, 'score_low_ko'].values[0]
        score_high = self.trait_info.loc[self.trait_info['trait'] == trait, 'score_high_ko'].values[0]
        average_score = self.trait_averages.loc[self.trait_averages['trait'] == trait, 'average_score'].values[0]

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            title={'text': trait_name},
            gauge={
            'axis': {'range': [1, 5],
                        'tickmode': "array",
                        "tickvals": [1, 2, 3, 4, 5],
                        "ticktext": [f"{score_low}", "", "", "", f"{score_high}"]},
            'bar': {'color': "blue"},
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                    'value': average_score
                }
            },
            delta={'reference': average_score}
        ))

        fig.update_layout(
            height=200,
            margin=dict(t=60, b=10, l=10, r=10),
            autosize=False,
            font=dict(size=16)
        )

        unique_key = f"trait_chart_{breed_name}_{trait}_{id(self)}_{id(fig)}".replace(" ", "_").replace("/", "_")
        st.plotly_chart(fig, use_container_width=True, key=unique_key)
        st.write(trait_desc)

    def show_breed_trait_hair(self, breed_name, trait=None):
        if breed_name not in self.breed_info['breed_name_kor'].values:
            st.info(f"{breed_name} 품종에 대한 털 정보가 없습니다.")
            return
            
        selected_breed = self.breed_info[self.breed_info['breed_name_kor'] == breed_name]
        
        if selected_breed.empty:
            st.info(f"{breed_name} 품종 정보를 찾을 수 없습니다.")
            return
            
        try:
            coat_type = selected_breed['Coat Type'].values[0]
            trait_name_type = self.trait_info.loc[self.trait_info['trait'] == 'Coat Type', 'trait_ko'].values[0]
            coat_type_desc = self.trait_info.loc[self.trait_info['trait'] == 'Coat Type', 'trait_desc_ko'].values[0]
            
            coat_length = selected_breed['Coat Length'].values[0]
            trait_name_length = self.trait_info.loc[self.trait_info['trait'] == 'Coat Length', 'trait_ko'].values[0]
            coat_length_desc = self.trait_info.loc[self.trait_info['trait'] == 'Coat Length', 'trait_desc_ko'].values[0]
            
            if isinstance(coat_type, str):
                coat_types = [t.strip() for t in coat_type.split(',')]
            else:
                coat_types = []
                
            if isinstance(coat_length, str):
                coat_lengths = [l.strip() for l in coat_length.split(',')]
            else:
                coat_lengths = []
                
            col1, col2 = st.columns(2)
            def create_coat_type_figure(coat_types, preset_color, height=410):
                for type in coat_types:
                    key = type[0] if isinstance(type, list) else type
                    key = key.replace("'", "").replace("[", "").replace("]", "").strip()
                    
                    if key in preset_color:
                        preset_color[key]['color'] = 'blue'

                fig = go.Figure()
                for coat_type, data in preset_color.items():
                    fig.add_trace(go.Scatter(
                        x=[data['bubbleX']],
                        y=[data['bubbleY']],
                        name=coat_type,
                        text=data['text'],
                        marker=dict(size=110, color=data['color']),
                        mode='markers+text',
                        textposition='middle center',
                    ))
                
                fig.update_layout(
                    height=height,
                    width=300,
                    xaxis=dict(showgrid=False, zeroline=False, visible=False),
                    yaxis=dict(showgrid=False, zeroline=False, visible=False),
                    showlegend=False,
                    margin=dict(t=1, b=1, l=10, r=10),
                    font=dict(size=18)
                )
                return fig

            with col1:
                st.write(f"##### {trait_name_type}")
                preset_color = {
                    'Double': {'bubbleX': 1, 'bubbleY': 1, 'text': 'Double', 'color': 'gray'},
                    'Wavy': {'bubbleX': 1, 'bubbleY': 2, 'text': 'Wavy', 'color': 'gray'},
                    'Corded': {'bubbleX': 1, 'bubbleY': 3, 'text': 'Corded', 'color': 'gray'},
                    'Wiry': {'bubbleX': 2, 'bubbleY': 1, 'text': 'Wiry', 'color': 'gray'},
                    'Curly': {'bubbleX': 2, 'bubbleY': 2, 'text': 'Curly', 'color': 'gray'},
                    'Hairless': {'bubbleX': 2, 'bubbleY': 3, 'text': 'Hairless', 'color': 'gray'},
                    'Silky': {'bubbleX': 3, 'bubbleY': 1, 'text': 'Silky', 'color': 'gray'},
                    'Smooth': {'bubbleX': 3, 'bubbleY': 2, 'text': 'Smooth', 'color': 'gray'},
                    'Rough': {'bubbleX': 3, 'bubbleY': 3, 'text': 'Rough', 'color': 'gray'}
                }
                fig = create_coat_type_figure(coat_types, preset_color, height=410)
                coat_type_key = f"coat_type_chart_{breed_name}_{id(self)}_{id(fig)}".replace(" ", "_")
                st.plotly_chart(fig, use_container_width=True, key=coat_type_key)
                st.write(coat_type_desc)

            with col2:
                st.write(f"##### {trait_name_length}")
                preset_length = {
                    'Short': {'bubbleX': 1, 'bubbleY': 1, 'text': 'Short', 'color': 'gray'},
                    'Medium': {'bubbleX': 2, 'bubbleY': 1, 'text': 'Medium', 'color': 'gray'},
                    'Long': {'bubbleX': 3, 'bubbleY': 1, 'text': 'Long', 'color': 'gray'},
                }
                fig = create_coat_type_figure(coat_lengths, preset_length, height=180)
                coat_length_key = f"coat_length_chart_{breed_name}_{id(self)}_{id(fig)}".replace(" ", "_")
                st.plotly_chart(fig, use_container_width=True, key=coat_length_key)
                st.write(coat_length_desc)

        except Exception as e:
            st.error(f"털 정보 표시 중 오류가 발생했습니다: {str(e)}")
            return

    def search_breed(self, breed_name):
        search_result = self.breed_info[self.breed_info['breed_name_kor'].str.contains(breed_name)]
        if search_result.empty:
            search_result = self.breed_info[self.breed_info['breed_name'].str.contains(breed_name)]
            if search_result.empty:
                st.info(f"{breed_name} 품종에 대한 정보가 없습니다.")
                return None
            else:
                return pd.DataFrame({'품종': search_result['breed_name_kor'].values, '품종_영문': search_result['breed_name'].values})
        else:
            return pd.DataFrame({'품종': search_result['breed_name_kor'].values, '품종_영문': search_result['breed_name'].values})
    

    def match_breed(self, upkind, breed_name):
        data_key = f"match_breed_data_{upkind}_{breed_name.replace(' ', '_')}"
        grid_key = f"match_breed_grid_{upkind}_{breed_name.replace(' ', '_')}"
        button_key = f"match_breed_button_{upkind}_{breed_name.replace(' ', '_')}"
        
        
        col1, col2, col3 = st.columns((1,1,1))
        with col2:
            search_shelter = st.button(
                f"[{breed_name}] 입양하기",
                key=button_key,
                use_container_width=True,
                type="primary"
            )
            
        if search_shelter:
            petinshelter = UI().show_petinshelter(upkind)
            
            if petinshelter is None or petinshelter.empty:
                st.error("보호소 데이터를 가져오지 못했습니다.")
                return
            
            search_keywords = breed_name.split()
            main_keyword = search_keywords[0] if search_keywords else breed_name
            
            filtered_data = petinshelter[petinshelter['kindCd'].str.contains(main_keyword, na=False, case=False)]
            
            if filtered_data.empty and len(search_keywords) > 1:
                main_keyword = search_keywords[1]
                filtered_data = petinshelter[petinshelter['kindCd'].str.contains(main_keyword, na=False, case=False)]
            
            if filtered_data.empty:
                st.warning(f"'{breed_name}' 품종을 찾을 수 없습니다. 다른 검색어로 시도해보세요.")
            
            st.session_state[data_key] = filtered_data
        
        if data_key in st.session_state:
            filtered_data = st.session_state[data_key]
            
            if filtered_data is not None and not filtered_data.empty:                
                with st.expander("지도 보기", expanded=True):
                    self.show_map(filtered_data, radius=500)
                
                grid_response = self.show_shelter_detail(filtered_data)
                st.session_state[grid_key] = grid_response
                
                self.show_pet_detail(grid_response)
            else:
                st.warning(f"보호소에서 {breed_name} 품종을 찾을 수 없습니다.")