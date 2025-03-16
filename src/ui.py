import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Callable, Optional, Union, Tuple
from src.settings import verify_password
from pathlib import Path
from src.data import Public
import time
import re
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.graph_objects as go
from src.data import Public, Common
import pydeck as pdk
import pandas as pd

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
        """
        특정 입력 필드에 자동 포커스를 추가하는 JavaScript 코드
        
        Parameters:
        -----------
        selector : str
            포커스할 HTML 요소의 CSS 선택자
        delay : int
            페이지 로드 후 포커스를 적용할 지연 시간(밀리초)
        """
        js_code = f"""
        <script>
        // 페이지 로드 후 {delay}ms 후에 포커스 시도
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
        """
        비밀번호 입력 양식을 생성합니다.
        
        Parameters:
        -----------
        on_change_callback : Callable
            비밀번호 입력 시 호출될 콜백 함수
        error_message : str
            오류 발생 시 표시할 메시지
        has_error : bool
            오류 상태 여부
        placeholder : str
            입력 필드에 표시할 안내 텍스트
        key : str
            입력 필드의 고유 키 (기본값: "password_input")
        """
        # 자동 포커스 스크립트 추가
        self.add_input_focus_js()
        
        # 오류 메시지 표시
        if has_error:
            st.error(error_message)
        
        # 비밀번호 입력 UI
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
        """
        필터링 UI를 생성합니다.
        
        Parameters:
        -----------
        data : pd.DataFrame
            필터링할 데이터
        filter_values : Dict[str, str]
            현재 필터 값 (key: 필터 이름, value: 선택된 값)
        on_change_callbacks : Dict[str, Callable]
            각 필터의 값이 변경될 때 호출할 콜백 함수
        column_names : Dict[str, str]
            컬럼 매핑 정보 (key: 내부 컬럼명, value: 표시 컬럼명)
        """
        # 컬럼 생성
        filter_cols = st.columns(len(filter_values))
        
        # 필터 값 목록 추출
        for i, (filter_key, current_value) in enumerate(filter_values.items()):
            if filter_key not in column_names:
                continue
                
            display_name = column_names[filter_key]
            column_name = column_names[filter_key]
            
            # 필터 옵션 생성
            options = ["전체"]
            if filter_key in data.columns:
                options.extend(list(data[filter_key].unique()))
            
            # 현재 선택 인덱스
            selected_index = 0
            if current_value in options:
                selected_index = options.index(current_value)
                
            # 셀렉트박스 생성
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

        # 가격 칼럼 천단위 콤마 추가
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
        
        # 결과 개수 표시
        st.info(f"총 {len(df)}개의 결과가 있습니다.")

    def show_date_range_selector(self, default_start_date=None, 
                                default_end_date=None, 
                                search_button_label="검색") -> Tuple:
        """
        날짜 범위 선택기를 표시합니다.
        
        Parameters:
        -----------
        default_start_date : datetime.date, optional
            기본 시작 날짜
        default_end_date : datetime.date, optional
            기본 종료 날짜
        search_button_label : str
            검색 버튼 라벨
            
        Returns:
        --------
        Tuple[datetime.date, datetime.date, bool]
            선택된 시작 날짜, 종료 날짜, 검색 버튼 클릭 여부
        """
        if default_start_date is None:
            default_start_date = (datetime.now() + timedelta(days=1)).date()
            
        if default_end_date is None:
            default_end_date = (datetime.now() + timedelta(days=7)).date()
        
        # 날짜 선택 레이아웃
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
        """성공 메시지 표시 (세션 상태 활용)"""
        if message:
            st.success(message)
        elif st.session_state.get('success_message'):
            st.success(st.session_state.success_message)
            st.session_state.success_message = None
    
    def display_error_message(self, message):
        """에러 메시지 표시"""
        st.error(message)
    
    def create_date_region_selection(self):
        """날짜 및 지역 선택 UI 생성"""
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            default_start_date = datetime.now().date()
            start_date = st.date_input("시작일", default_start_date, key="start_date")
        
        with col2:
            default_end_date = (datetime.now() + timedelta(days=30)).date()
            end_date = st.date_input("종료일", default_end_date, key="end_date")
        
        with col3:
            # 해당 함수에서는 regions 인자를 받아와야 함
            # 여기서는 예시로만 작성
            selected_region = st.selectbox("지역 선택", ["전체"], key="region")
        
        return start_date, end_date, selected_region
    
    def create_pension_selection(self, pensions, default=None, key="selected_pensions"):
        """펜션 선택 UI 생성"""
        st.write("비교할 펜션 선택 (복수 선택 가능)")
        selected_pensions = st.multiselect(
            "펜션 선택",
            options=pensions,
            default=default if default is not None else pensions,
            key=key
        )
        return selected_pensions
    
    def create_chart_type_selection(self, current_type="bar"):
        """차트 유형 선택 UI 생성"""
        chart_type = st.radio(
            "차트 유형 선택:",
            options=["바 차트", "히트맵", "레이더 차트"],
            index=0 if current_type == "bar" else 
                  1 if current_type == "heatmap" else 2,
            horizontal=True,
            key="chart_type_radio"
        )
        
        # 영문 차트 타입 반환
        if chart_type == "바 차트":
            return "bar"
        elif chart_type == "히트맵":
            return "heatmap"
        else:
            return "radar"
    
    def create_logout_button(self, key="logout"):
        """로그아웃 버튼 생성"""
        if st.button("로그아웃", key=key, type="primary"):
            st.session_state.password_verified = False
            st.rerun()
    
    def verify_user_password(self, password_field_key="password_input", session_key="password_verified", error_key="password_error", password_verify_function=None):
        """
        사용자 비밀번호 검증을 위한 공통 함수
        
        Parameters:
        -----------
        password_field_key : str
            비밀번호 입력 필드의 키 이름
        session_key : str
            비밀번호 검증 상태를 저장할 세션 키
        error_key : str
            오류 상태를 저장할 세션 키
        password_verify_function : callable
            비밀번호 검증 함수
        
        Returns:
        --------
        bool
            비밀번호 검증 성공 여부
        """
        # 세션 상태 초기화
        st.session_state.setdefault(session_key, False)
        st.session_state.setdefault(error_key, False)
        
        # 비밀번호 검증 콜백 함수
        def check_password():
            password = st.session_state[password_field_key]
            if password_verify_function:
                verified = password_verify_function(password)
            else:
                # 기본 검증(커스텀 함수가 제공되지 않은 경우)
                verified = (password == "1234")  # 예시 기본값
            
            st.session_state[session_key] = verified
            st.session_state[error_key] = not verified
        
        # 이미 검증된 상태면 바로 True 반환
        if st.session_state[session_key]:
            return True
        
        # 검증이 필요한 경우 UI 표시
        st.subheader("🔒 로그인")
        UI().create_password_input(
            on_change_callback=check_password,
            has_error=st.session_state[error_key],
            key=password_field_key
        )
        
        return st.session_state[session_key]
    
    def create_progress_bar(self):
        """진행 상황 표시 바 생성"""
        return st.progress(0)
    
    def create_analysis_button(self):
        """분석 버튼 생성"""
        return st.button("분석 시작", use_container_width=True, key="analyze_button")
    
    def create_expandable_detail_section(self, title, dataframe, columns=None):
        """펼칠 수 있는 상세 정보 섹션 생성"""
        with st.expander(title):
            if columns:
                st.dataframe(dataframe[columns], use_container_width=True, hide_index=True)
            else:
                st.dataframe(dataframe, use_container_width=True, hide_index=True)
    
    def display_detailed_data(self, data, display_columns, title="상세 데이터 보기", sort_by=None):
        """상세 데이터 표시 섹션"""
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

    def apply_filters(self, data, upkind):
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
            
            # 출생년도 처리 - 안전하게 추출
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
                    key=f"btn_filter_{upkind}",  # 버튼 위젯용 키 (세션 상태 키와 다름)
                    on_click=set_filter_active)  # 클릭 시 콜백 함수 호출
        
        # 필터가 활성화되지 않았다면 모든 데이터 반환
        if not st.session_state[filter_state_key]:
            return data
        
        # 필터 적용
        filtered_data = data.copy()
        
        # 날짜 필터 적용을 위해 happenDt를 datetime 형식으로 변환
        filtered_data['happenDt'] = pd.to_datetime(filtered_data['happenDt'], errors='coerce')

        # 날짜 필터 적용
        filtered_data = filtered_data[
            (filtered_data['happenDt'].dt.date >= date_from) & 
            (filtered_data['happenDt'].dt.date <= date_to)
        ]
        
        # 품종 필터 적용
        if selected_kind != "모든 품종":
            filtered_data = filtered_data[filtered_data['kindCd'] == selected_kind]
        
        # 년생 필터 적용
        if selected_birth_year != "모든 년도" and '출생년도' in filtered_data.columns:
            try:
                # "년생" 텍스트 제거하고 숫자만 추출
                year_only = selected_birth_year.replace('년생', '').strip()
                if year_only.isdigit():
                    year_value = int(year_only)
                    filtered_data = filtered_data[filtered_data['출생년도'] == year_value]
            except Exception as e:
                st.error(f"출생년도 필터링 중 오류 발생: {str(e)}")
        
        # 성별 필터 적용
        if selected_sex != "모두":
            filtered_data = filtered_data[filtered_data['sexCd'] == selected_sex]
        
        # 시도 필터 적용
        if selected_sido != "모든 지역":
            filtered_data = filtered_data[filtered_data['시도'] == selected_sido]
            
            # 시군구 필터 적용
            if selected_sigungu != "모든 시군구":
                filtered_data = filtered_data[filtered_data['시군구'] == selected_sigungu]
        
        # 날짜 형식을 "YYYY-MM-DD"로 변환
        filtered_data['happenDt'] = filtered_data['happenDt'].dt.strftime('%Y-%m-%d')
        
        return filtered_data

class BreedInfo:
    def __init__(self) -> None:
        self.breed_info = pd.read_csv('./static/database/akcBreedInfo.csv')
        self.trait_info = pd.read_csv('./static/database/akcTraits.csv')
        self.trait_averages = pd.read_csv('./static/database/trait_averages.csv')

    def display_text_input(self, label, value, col):
        with col:
            st.text_input(label, disabled=True, value=value)
    
    def show_shelter_detail(self, filtered_data, breed = None):
        display_columns = ['시군구', 'desertionNo', 'happenDt', 'kindCd', 'age', 'sexCd', 'careNm', '시도']
        if breed:
            filtered_data = filtered_data[filtered_data['kindCd'].str.contains(breed)]
        display_data = filtered_data[display_columns].copy()
        
        gb = GridOptionsBuilder.from_dataframe(display_data)
        gb.configure_selection(selection_mode="single", use_checkbox=True)

        # 컬럼 헤더 및 그룹화 설정
        gb.configure_column("시도", headerName="시도", rowGroup=True, hide=True, use_checkbox=False)
        gb.configure_column("시군구", headerName="시군구", use_checkbox=True)
        gb.configure_column("desertionNo", headerName="유기번호", use_checkbox=True)
        gb.configure_column("happenDt", headerName="발견일", use_checkbox=True)
        gb.configure_column("kindCd", headerName="품종", use_checkbox=True)
        gb.configure_column("age", headerName="나이", use_checkbox=True)
        gb.configure_column("sexCd", headerName="성별", use_checkbox=True)
        gb.configure_column("careNm", headerName="보호소", use_checkbox=True)

        grid_options = gb.build()

        # AgGrid 표시
        grid_response = AgGrid(
            display_data,
            gridOptions=grid_options,
            enable_enterprise_modules=True,
            height=400,
            width='100%',
            fit_columns_on_grid_load=True,
            use_container_width = True
        )

        return grid_response
    
    def show_map(self, petinshelter):
        shelterlist = pd.read_csv('./static/database/보호소코드.csv')
        shelterlist = shelterlist[shelterlist['주소'].notna()]

        # 보호소별 동물 수 카운트
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
        
        # pydeck의 ScatterplotLayer를 사용하여 각 보호소를 원형 마커로 표시합니다.
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=shelterlist_status,
            get_position='[lon, lat]',
            get_fill_color='[255, 0, 0, 160]',
            get_radius='count_pet * 30',
            pickable=True,
        )
        
        # 초기 지도 뷰 설정 (전체 데이터의 중심 좌표 기준)
        view_state = pdk.ViewState(
            latitude=37.515586, 
            longitude=127.056992,
            zoom=9,
            pitch=0,
        )
        
        # 툴팁 설정: 마우스 오버 시 보호소명과 count_pet 표시
        tooltip = {
            "html": "<b>보호소:</b> {보호소명} <br/><b>보호 중:</b> {count_pet}<br/><b>보호 중:</b> {주소}",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }
        
        # pydeck Deck 객체 생성
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip
        )
        
        st.pydeck_chart(deck)

    def show_map_null(self):
        map_df = pd.DataFrame()

        with st.expander("골프장 위치 지도", expanded=False):
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
        
        # 디버깅을 위해 타입 확인
        try:
            # DataFrame인 경우
            if isinstance(selected, pd.DataFrame):
                if len(selected) == 0:
                    return
                # DataFrame의 첫 번째 행을 딕셔너리로 변환
                first_row = selected.iloc[0].to_dict()
            else:
                # 리스트인 경우
                if len(selected) == 0:
                    return
                first_row = selected[0]
                
            # 'desertionNo' 키가 없는 경우 대체 키를 찾거나 오류 처리
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

        with st.expander("동물정보 상세", expanded=True):
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

        # 품종 정보 추출 및 매핑
        if 'kindCd' in selected_pet.columns:
            kindCd = selected_pet['kindCd'].iloc[0]
            # "[개]", "[고양이]" 등의 접두사 제거
            if isinstance(kindCd, str):
                kindCd = kindCd.replace("[개]", "").replace("[고양이]", "").replace("[기타축종]", "").strip()
            kindCd = self.kindCd_mapping(kindCd)
            self.show_breed_info(kindCd)
        else:
            st.warning("품종 정보를 찾을 수 없습니다.")

        self.show_shelter_info(selected_pet)

    def kindCd_mapping(self, kindCd):
        # None 또는 빈 문자열 처리
        if kindCd is None or not isinstance(kindCd, str) or kindCd.strip() == '':
            return ""
            
        kindCd_mapping = {
            "푸들": "스탠다드 푸들"
        }
        
        kindCd = kindCd_mapping.get(kindCd, kindCd)
        kindCd = kindCd.replace("믹스", "").replace("잡종", "").strip()
        return kindCd

    def show_breed_info(self, kindCd, expandedoption=True):
        # kindCd가 없거나 빈 문자열인 경우 정보 표시 스킵
        if kindCd is None or kindCd == "":
            st.info("품종 정보가 없습니다.")
            return
            
        with st.expander(f"{kindCd} 상세 정보", expanded=expandedoption):
            col2, col3, col4 = st.columns([1, 1, 1])            
            if kindCd in self.breed_info['breed_name_kor'].values:
                height, weight, life_expectancy = self.show_breed_info_basic(kindCd)
                
                height = ', '.join(height) if isinstance(height, pd.Series) and not height.empty else ""
                weight = ', '.join(weight) if isinstance(weight, pd.Series) and not weight.empty else ""
                life_expectancy = ', '.join(life_expectancy) if isinstance(life_expectancy, pd.Series) and not life_expectancy.empty else ""

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

    def show_breed_info_basic(self, breed_name):
        # 해당 품종이 breed_info에 있는지 확인
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
    
    def show_breed_trait(self, breed_name):
        # 해당 품종이 breed_info에 있는지 확인
        if breed_name not in self.breed_info['breed_name_kor'].values:
            st.info(f"{breed_name} 품종에 대한 정보가 없습니다.")
            return None, None, None, None, None, None, None, None, None, None, None, None, None
            
        selected_breed = self.breed_info[self.breed_info['breed_name_kor'] == breed_name]
        
        if selected_breed.empty:
            st.info(f"{breed_name} 품종 정보를 찾을 수 없습니다.")
            return None, None, None, None, None, None, None, None, None, None, None, None, None
            
        try:
            AffectionateWithFamily = selected_breed['Affectionate With Family'].values[0]
            GoodWithYoungChildren = selected_breed['Good With Young Children'].values[0]
            GoodWithOtherDogs = selected_breed['Good With Other Dogs'].values[0]
            SheddingLevel = selected_breed['Shedding Level'].values[0]
            CoatGroomingFrequency = selected_breed['Coat Grooming Frequency'].values[0]
            DroolingLevel = selected_breed['Drooling Level'].values[0]
            OpennessToStrangers = selected_breed['Openness To Strangers'].values[0]
            PlayfulnessLevel = selected_breed['Playfulness Level'].values[0]
            WatchdogProtectiveNature = selected_breed['Watchdog/Protective Nature'].values[0]
            AdaptabilityLevel = selected_breed['Adaptability Level'].values[0]
            TrainabilityLevel = selected_breed['Trainability Level'].values[0]
            EnergyLevel = selected_breed['Energy Level'].values[0]
            BarkingLevel = selected_breed['Barking Level'].values[0]
            MentalStimulationNeeds = selected_breed['Mental Stimulation Needs'].values[0]
            CoatType = selected_breed['Coat Type'].values[0]
            CoatLength = selected_breed['Coat Length'].values[0]
            return CoatType, CoatLength
        except Exception as e:
            st.error(f"품종 특성 정보 조회 중 오류 발생: {str(e)}")
            return None, None
    
    def show_breed_trait_5scale_example(self):
        st.write("##### 속성 점수를 이해하는 방법")
        scores = [2, 4]
        average_scores = [4.5, 2.5]
        trait_desc = "속성에 대한 설명이 이 영역에 표시됩니다. ex. 훈련에 얼마나 잘 반응하며 새로운 것을 배우려는 의지가 어느 정도인지를 나타냅니다. 일부 품종은 주인을 기쁘게 하려고 노력하지만, 다른 품종은 자기 주장이 강해 스스로 원하는 대로 행동합니다."
        score_low = "낮은 점수의 의미"
        score_high = "높은 점수의 의미"
        traits = ["속성 이름(1)", "속성 이름(2)"]

        for i in range(2):
            col1, col2 = st.columns([1, 1])
            with col1:
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
                    font=dict(size=16, color="gray")  # 폰트 색상을 gray로 변경
                )

                # 고유한 key 추가
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{traits[i]}_{i+1}")
                st.write(f"<span style='color:gray;'>{trait_desc}</span>", unsafe_allow_html=True)

            with col2:
                col2_1, col2_2 = st.columns([1, 3])
                with col2_1:
                    st.write(f"<span style='color:gray;'>{traits[i]}</span>", unsafe_allow_html=True)
                    st.write(f"<span style='color:gray;'>{score_low}</span>", unsafe_allow_html=True)
                    st.write(f"<span style='color:gray;'>{score_high}</span>", unsafe_allow_html=True)
                    st.write(f"<span style='color:gray;'>{scores[i]}</span>", unsafe_allow_html=True)
                    delta = scores[i] - average_scores[i]
                    color = 'red' if delta < 0 else 'green'
                    st.markdown(f"<span style='color:{color};'>&#9660; {delta}</span> ", unsafe_allow_html=True)
                    st.write("<span style='color:red;'>|</span>", unsafe_allow_html=True)
                    st.write(f"<span style='color:gray;'>{trait_desc[:9]}...</span>", unsafe_allow_html=True)
                with col2_2:
                    st.write("<span style='color:gray;'>속성 이름</span>", unsafe_allow_html=True)
                    st.write("<span style='color:gray;'>속성의 점수가 낮을 때의 품종이 어떤 성향을 가지는지 설명</span>", unsafe_allow_html=True)
                    st.write("<span style='color:gray;'>속성의 점수가 높을 때의 품종이 어떤 성향을 가지는지 설명</span>", unsafe_allow_html=True)
                    st.write("<span style='color:gray;'>해당 품종의 속성 점수</span>", unsafe_allow_html=True)
                    st.write("<span style='color:gray;'>다른 품종의 평균 대비 상대 점수</span>", unsafe_allow_html=True)
                    st.write("<span style='color:gray;'>다른 품종의 평균 점수를 그래프에 표시</span>", unsafe_allow_html=True)
                    st.write("<span style='color:gray;'>품종의 특성에 대한 설명</span>", unsafe_allow_html=True)

            if i != len(scores) - 1:
                st.divider()


    def show_breed_trait_5scale(self, breed_name, trait):
        # 해당 품종이 breed_info에 있는지 확인
        if breed_name not in self.breed_info['breed_name_kor'].values:
            st.info(f"{breed_name} 품종에 대한 정보가 없습니다.")
            return
        
        # 해당 품종의 데이터 필터링
        filtered_data = self.breed_info.loc[self.breed_info['breed_name_kor'] == breed_name, trait]
        trait_name = self.trait_info.loc[self.trait_info['trait'] == trait, 'trait_ko'].values[0]
        
        # 필터링된 데이터가 비어있는지 확인
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

        # 차트 레이아웃 설정 - 높이와 마진을 일정하게 조정
        fig.update_layout(
            height=200,
            margin=dict(t=60, b=10, l=10, r=10),
            autosize=False,
            font=dict(size=16)
        )

        # 고유한 key 추가
        unique_key = f"trait_chart_{breed_name}_{trait}".replace(" ", "_").replace("/", "_")
        st.plotly_chart(fig, use_container_width=True, key=unique_key)
        st.write(trait_desc)

    def show_breed_trait_hair(self, breed_name, trait=None):
        """품종의 털 타입과 털 길이를 체크박스 형태로 표시합니다."""
        # 해당 품종이 breed_info에 있는지 확인
        if breed_name not in self.breed_info['breed_name_kor'].values:
            st.info(f"{breed_name} 품종에 대한 털 정보가 없습니다.")
            return
            
        selected_breed = self.breed_info[self.breed_info['breed_name_kor'] == breed_name]
        
        # 선택된 데이터가 비어있는지 확인
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
            
            # 털 타입과 길이가 여러 개일 수 있으므로 리스트로 분리
            if isinstance(coat_type, str):
                coat_types = [t.strip() for t in coat_type.split(',')]
            else:
                coat_types = []
                
            if isinstance(coat_length, str):
                coat_lengths = [l.strip() for l in coat_length.split(',')]
            else:
                coat_lengths = []
                
            # UI에 표시
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
                # 고유한 key 추가
                coat_type_key = f"coat_type_chart_{breed_name}".replace(" ", "_")
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
                # 고유한 key 추가
                coat_length_key = f"coat_length_chart_{breed_name}".replace(" ", "_")
                st.plotly_chart(fig, use_container_width=True, key=coat_length_key)
                st.write(coat_length_desc)

        except Exception as e:
            st.error(f"털 정보 표시 중 오류가 발생했습니다: {str(e)}")
            return

    def search_breed(self, breed_name):
        search_result = self.breed_info[self.breed_info['breed_name_kor'].str.contains(breed_name)]
        if search_result.empty:
            st.info(f"{breed_name} 품종에 대한 정보가 없습니다.")
            return None
        else:
            # Series 대신 DataFrame 반환
            return pd.DataFrame({'품종': search_result['breed_name_kor'].values})
    
        
        
