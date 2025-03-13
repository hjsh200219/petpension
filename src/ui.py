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
                "확인", 
                key=f"{key}_button", 
                use_container_width=True,
                on_click=on_change_callback
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
        
        # 그룹 행의 체크박스 제거 및 선택 방지를 위한 고급 설정
        grid_options['groupCheckboxSelection'] = False
        grid_options['groupSelectsChildren'] = False
        grid_options['suppressGroupSelectParent'] = True
        
        # 그룹 행에는 체크박스를 표시하지 않고 데이터 행에만 표시하는 함수
        js_code = """
        function(params) {
            return !params.node.group;
        }
        """
        grid_options['isRowSelectable'] = js_code
        
        # 그룹 행의 체크박스를 완전히 제거
        if 'defaultColDef' not in grid_options:
            grid_options['defaultColDef'] = {}
        grid_options['defaultColDef']['headerCheckboxSelection'] = False
        
        if 'groupRowRendererParams' not in grid_options:
            grid_options['groupRowRendererParams'] = {}
        grid_options['groupRowRendererParams']['checkbox'] = False
        grid_options['groupRowRendererParams']['suppressCount'] = False
        
        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            enable_enterprise_modules=True,
            height=500,
            width='100%',
            fit_columns_on_grid_load=True
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
        col1, col2, col3 = st.columns((1, 1, 3))
        
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
                use_container_width=False
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

    def extract_birth_year(self, age_string):
        try:
            if pd.isna(age_string) or not isinstance(age_string, str):
                return None
                
            # 괄호 앞의 숫자 추출 (예: "2017(년생)" -> "2017")
            match = re.search(r'^(\d{4})(?:\s*\(|$)', age_string.strip())
            if match:
                year = int(match.group(1))
                # 유효한 연도 범위 확인 (1990년부터 현재 연도까지)
                current_year = datetime.now().year
                if 1990 <= year <= current_year + 1:  # +1은 내년 출생 표기도 허용
                    return year
            return None
        except Exception:
            return None
        
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
    
    def show_pet_detail(self, grid_response):
        selected = grid_response.get('selected_rows', [])
        if selected is None or len(selected) == 0:
            return
            
        # selected의 타입에 따라 처리
        import pandas as pd
        
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

        kindCd = selected_pet['kindCd'].iloc[0]
        kindCd = kindCd.replace('[개]', '').replace('[고양이]', '').replace('[기타품종]', '').strip()
        with st.expander(f"{kindCd} 상세 정보", expanded=True):
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

            tab1, tab2, tab3, tab4 = st.tabs(["Fmaily Life", "Physical", "Social", "Personality"])
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
        selected_breed = self.breed_info[self.breed_info['breed_name_kor'] == breed_name]
        height,weight,life_expectancy = selected_breed['height_k'],selected_breed['weight_k'],selected_breed['life_expectancy_k']
        
        return height,weight,life_expectancy
    
    def show_breed_trait(self, breed_name):
        selected_breed = self.breed_info[self.breed_info['breed_name_kor'] == breed_name]
        AffectionateWithFamily = selected_breed['Affectionate With Family']
        GoodWithYoungChildren = selected_breed['Good With Young Children']
        GoodWithOtherDogs = selected_breed['Good With Other Dogs']
        SheddingLevel = selected_breed['Shedding Level']
        CoatGroomingFrequency = selected_breed['Coat Grooming Frequency']
        DroolingLevel = selected_breed['Drooling Level']
        OpennessToStrangers = selected_breed['Openness To Strangers']
        PlayfulnessLevel = selected_breed['Playfulness Level']
        WatchdogProtectiveNature = selected_breed['Watchdog/Protective Nature']
        AdaptabilityLevel = selected_breed['Adaptability Level']
        TrainabilityLevel = selected_breed['Trainability Level']
        EnergyLevel = selected_breed['Energy Level']
        BarkingLevel = selected_breed['Barking Level']
        MentalStimulationNeeds = selected_breed['Mental Stimulation Needs']
        CoatType = selected_breed['Coat Type']
        CoatLength = selected_breed['Coat Length']
        return CoatType, CoatLength
    
    def show_breed_trait_5scale(self, breed_name, trait):
        score = self.breed_info.loc[self.breed_info['breed_name_kor'] == breed_name, trait].values[0]
        trait_desc = self.trait_info.loc[self.trait_info['trait'] == trait, 'trait_desc'].values[0]
        score_low = self.trait_info.loc[self.trait_info['trait'] == trait, 'score_low'].values[0]
        score_high = self.trait_info.loc[self.trait_info['trait'] == trait, 'score_high'].values[0]
        average_score = self.trait_averages.loc[self.trait_averages['trait'] == trait, 'average_score'].values[0]

        col1, col2 = st.columns([1.5, 1])
        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=score,
                title={'text': trait},
                gauge={
                'axis': {'range': [1, 5],
                         'tickmode': "array",
                         "tickvals": [1, 2, 3, 4, 5],
                         "ticktext": ["", "", "", "", ""]},
                'bar': {'color': "blue"},
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                        'value': average_score
                    }
                },
            ))

            # 차트 레이아웃 설정 - 높이와 마진을 일정하게 조정
            fig.update_layout(
                height=200,
                margin=dict(t=60, b=10, l=10, r=10),
                autosize=True,
                font=dict(size=12)
            )

            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.write(trait_desc)

    def show_breed_trait_hair(self, breed_name, trait=None):
        """품종의 털 타입과 털 길이를 체크박스 형태로 표시합니다."""
        selected_breed = self.breed_info[self.breed_info['breed_name_kor'] == breed_name]
        coat_type = selected_breed['Coat Type'].values[0]
        coat_type_desc = self.trait_info.loc[self.trait_info['trait'] == 'Coat Type', 'trait_desc'].values[0]
        coat_length = selected_breed['Coat Length'].values[0]
        coat_length_desc = self.trait_info.loc[self.trait_info['trait'] == 'Coat Length', 'trait_desc'].values[0]
        
        # 문자열 형태에서 리스트로 변환 (필요한 경우)
        if isinstance(coat_type, str):
            coat_type = eval(coat_type)
        if isinstance(coat_length, str):
            coat_length = eval(coat_length)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            # 털 타입 옵션
            st.subheader("털 유형")
            coat_type_options = ["Wiry", "Hairless", "Smooth", "Rough", "Corded", "Curly", "Wavy", "Double", "Silky"]
            
            # 각 행에 3개씩 배치
            rows = [coat_type_options[i:i+3] for i in range(0, len(coat_type_options), 3)]
            
            for row in rows:
                cols = st.columns(3)
                for i, option in enumerate(row):
                    with cols[i]:
                        # 해당 옵션이 선택된 경우 파란색, 아닌 경우 회색으로 표시
                        if option in coat_type:
                            st.markdown(f"""
                            <div style="display: flex; align-items: center;">
                                <div style="color: #4F7CAC; font-size: 24px; margin-right: 10px;">✓</div>
                                <div style="color: #4F7CAC;">{option}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="display: flex; align-items: center;">
                                <div style="color: #CCCCCC; font-size: 24px; margin-right: 10px;">✗</div>
                                <div style="color: #CCCCCC;">{option}</div>
                            </div>
                            """, unsafe_allow_html=True)
        with col2:
            st.write(coat_type_desc)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            # 털 길이 옵션
            st.subheader("털 길이")
            coat_length_options = ["Short", "Medium", "Long"]
            
            cols = st.columns(3)
            for i, option in enumerate(coat_length_options):
                with cols[i]:
                    # 해당 옵션이 선택된 경우 파란색, 아닌 경우 회색으로 표시
                    if option in coat_length:
                        st.markdown(f"""
                        <div style="display: flex; align-items: center;">
                            <div style="color: #4F7CAC; font-size: 24px; margin-right: 10px;">✓</div>
                            <div style="color: #4F7CAC;">{option}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="display: flex; align-items: center;">
                            <div style="color: #CCCCCC; font-size: 24px; margin-right: 10px;">✗</div>
                            <div style="color: #CCCCCC;">{option}</div>
                        </div>
                        """, unsafe_allow_html=True)
        with col2:
            st.write(coat_length_desc)
            
        return coat_type, coat_length
        
        
        
        
        
        
