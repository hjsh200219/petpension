import streamlit as st
import pandas as pd
import os
from pathlib import Path
from src.data import Naver
from src.ui import UI
from src.settings import verify_password

# 개발 모드에서만 캐싱 설정 비활성화
if os.environ.get('STREAMLIT_DEVELOPMENT', 'false').lower() == 'true':
    st.cache_data.clear()
    st.cache_resource.clear()

naver = Naver()

def initialize_session_state():
    """세션 상태 초기화"""
    if 'password_verified' not in st.session_state:
        st.session_state.password_verified = False
    
    if 'password_error' not in st.session_state:
        st.session_state.password_error = False
        
    # 성공 메시지를 위한 세션 상태 변수
    if 'success_message' not in st.session_state:
        st.session_state.success_message = None

def verify_user_password():
    """사용자 비밀번호 검증 처리"""
    # 비밀번호 검증 함수
    def check_password():
        password = st.session_state.add_pension_password_input
        if verify_password(password):
            st.session_state.password_verified = True
            st.session_state.password_error = False
        else:
            st.session_state.password_error = True

    if not st.session_state.password_verified:
        st.subheader("🔒 관리자 로그인")
        
        # UI 컴포넌트 사용하여 비밀번호 입력 폼 생성
        UI().create_password_input(
            on_change_callback=check_password,
            has_error=st.session_state.password_error,
            key="add_pension_password_input"
        )
        return False
    return True

def load_pension_data():
    """펜션 정보 데이터 로드"""
    csv_path = './static/database/pension_info.csv'
    if not os.path.exists(csv_path):
        return None
    
    pension_info = pd.read_csv(csv_path)
    
    # 데이터 타입 변환
    pension_info['businessId'] = pension_info['businessId'].astype(str)
    pension_info['bizItemId'] = pension_info['bizItemId'].astype(str)
    pension_info['channelId'] = pension_info['channelId'].astype(str)
    
    # businessName 컬럼이 가장 먼저 오도록 컬럼 순서 재정렬
    pension_info = pension_info[
        ['businessName', 'channelId', 'businessId', 
         'bizItemName', 'bizItemId', 'addressNew']
    ]
    
    return pension_info

def save_pension_data(pension_info):
    """펜션 정보 저장"""
    csv_path = './static/database/pension_info.csv'
    try:
        pension_info.to_csv(csv_path, index=False)
        return True
    except Exception as e:
        st.error(f"데이터 저장 중 오류가 발생했습니다: {e}")
        return False

def display_current_pensions(pension_info):
    """현재 등록된 펜션 정보 표시"""
    st.subheader("현재 등록된 펜션 정보")
    UI().show_dataframe_with_info(pension_info)

def handle_pension_edit(pension_info):
    """펜션 정보 수정 UI 및 처리"""
    with st.expander("펜션 정보 수정"):
        # 수정할 펜션과 상품을 한 줄에 표시
        col1, col2 = st.columns(2)
        
        # 1단계: 먼저 businessName 선택
        business_names = pension_info['businessName'].drop_duplicates().tolist()
        with col1:
            selected_business = st.selectbox(
                "수정할 펜션 선택", 
                options=business_names,
                key="edit_business_name"
            )
        
        # 2단계: 선택한 펜션의 상품 표시
        if not selected_business:
            return pension_info  # 변경 없음
            
        filtered_items = pension_info[
            pension_info['businessName'] == selected_business
        ]['bizItemName'].tolist()
        
        with col2:
            selected_item = st.selectbox(
                "수정할 상품 선택",
                options=filtered_items,
                key="edit_biz_item"
            )
        
        # 선택한 펜션-상품 정보 가져오기
        selected_pension = pension_info[
            (pension_info['businessName'] == selected_business) & 
            (pension_info['bizItemName'] == selected_item)
        ]
        
        if selected_pension.empty:
            st.error("선택한 펜션 정보가 없습니다.")
            return pension_info  # 변경 없음
            
        selected_pension = selected_pension.iloc[0]
        
        # 수정 양식
        col1, col2, col3, col4 = st.columns((2, 1, 2, 1))
        with col1:
            business_name = st.text_input(
                "businessName", 
                value=selected_pension['businessName']
            )
        with col2:
            business_id = st.text_input(
                "businessId", 
                value=selected_pension['businessId']
            )
        with col3:
            biz_item_name = st.text_input(
                "bizItemName", 
                value=selected_pension['bizItemName']
            )
        with col4:
            biz_item_id = st.text_input(
                "bizItemId", 
                value=selected_pension['bizItemId']
            )
        
        address = st.text_input(
            "주소", 
            value=selected_pension['addressNew']
        )
        
        # 수정 버튼
        if st.button("수정 저장", key="save_edit"):
            # 인덱스를 찾아서 해당 행만 업데이트
            idx = pension_info[
                (pension_info['businessName'] == selected_pension['businessName']) & 
                (pension_info['bizItemName'] == selected_pension['bizItemName'])
            ].index
            
            if len(idx) > 0:
                pension_info.loc[idx, 'businessName'] = business_name
                pension_info.loc[idx, 'businessId'] = business_id
                pension_info.loc[idx, 'bizItemName'] = biz_item_name
                pension_info.loc[idx, 'bizItemId'] = biz_item_id
                pension_info.loc[idx, 'addressNew'] = address
                
                # 변경된 정보 저장
                if save_pension_data(pension_info):
                    # 성공 메시지를 세션 상태에 저장
                    st.session_state.success_message = (
                        f"{selected_business} - {selected_item} 정보가 수정되었습니다."
                    )
                    st.rerun()  # 페이지 새로고침
    
    return pension_info  # 변경 없거나 이미 저장하고 rerun한 경우

def handle_pension_delete(pension_info):
    """펜션 정보 삭제 UI 및 처리"""
    with st.expander("펜션 정보 삭제"):
        delete_col1, delete_col2 = st.columns(2)
        
        # 삭제할 펜션 선택 (먼저 businessName 선택)
        business_names_for_delete = pension_info['businessName'].drop_duplicates().tolist()
        with delete_col1:
            selected_business_to_delete = st.selectbox(
                "삭제할 펜션 선택", 
                options=business_names_for_delete,
                key="delete_business_name"
            )
        
        # 선택한 펜션의 상품 표시 여부 선택
        delete_entire_pension = st.checkbox(
            "선택한 펜션의 모든 상품 삭제", 
            value=True, 
            key="delete_all_items"
        )
        
        selected_item_to_delete = None
        if not delete_entire_pension:
            # 특정 상품만 삭제하는 경우
            filtered_items_for_delete = pension_info[
                pension_info['businessName'] == selected_business_to_delete
            ]['bizItemName'].tolist()
            
            with delete_col2:
                selected_item_to_delete = st.selectbox(
                    "삭제할 상품 선택",
                    options=filtered_items_for_delete,
                    key="delete_biz_item"
                )
        
        # 삭제 버튼
        if st.button("삭제 실행", key="confirm_delete"):
            if delete_entire_pension:
                # 선택한 펜션의 모든 정보 삭제
                new_pension_info = pension_info[
                    pension_info['businessName'] != selected_business_to_delete
                ]
                message = f"{selected_business_to_delete}가 삭제되었습니다."
            else:
                # 선택한 펜션의 특정 상품만 삭제
                new_pension_info = pension_info[
                    ~((pension_info['businessName'] == selected_business_to_delete) & 
                      (pension_info['bizItemName'] == selected_item_to_delete))
                ]
                message = f"{selected_business_to_delete} - {selected_item_to_delete} 정보가 삭제되었습니다."
            
            # 변경된 정보 저장
            if save_pension_data(new_pension_info):
                # 성공 메시지를 세션 상태에 저장
                st.session_state.success_message = message
                st.rerun()  # 페이지 새로고침
    
    return pension_info  # 변경 없거나 이미 저장하고 rerun한 경우

def handle_add_new_pension():
    """새 펜션 추가 UI 및 처리"""
    st.subheader("새 펜션 추가")
    
    with st.form("add_pension_form"):
        col1, col2 = st.columns((1, 1))
        with col1:
            new_channel_id = st.text_input("channelId")
        with col2:
            new_business_id = st.text_input("business_id")
        
        # 추가 버튼
        button_add = st.form_submit_button("펜션 추가")
        
        if button_add:
            if not new_channel_id or not new_business_id:
                st.error("channelId와 business_id를 모두 입력해주세요.")
                return
                
            try:
                # 펜션 정보 추가
                naver.insert_pension_info(
                    new_business_id,
                    new_channel_id, 
                )
                
                # 펜션 이름 가져오기
                pension_name, _, _ = naver.get_pension_info(new_channel_id)
                
                # 성공 메시지를 세션 상태에 저장
                st.session_state.success_message = f"{pension_name} 추가 완료"
                st.rerun()  # 페이지 새로고침하여 pension_info를 다시 로드
            except Exception as e:
                st.error(f"펜션 추가 중 오류가 발생했습니다: {e}")

def handle_logout():
    """로그아웃 처리"""
    if st.button("로그아웃", key="logout", type="secondary"):
        st.session_state.password_verified = False
        st.rerun()

def display_success_message():
    """성공 메시지 표시"""
    if st.session_state.success_message:
        st.success(st.session_state.success_message)
        # 메시지를 표시한 후 초기화
        st.session_state.success_message = None

def show_add_pension_page():
    """펜션 추가/관리 페이지 메인 함수"""
    # 세션 상태 초기화
    initialize_session_state()
    
    # 비밀번호 검증
    if not verify_user_password():
        return
    
    # 페이지 제목 & 로그아웃 버튼
    col1, col2 = st.columns([5, 1])
    with col1:
        st.subheader("🏡 펜션 추가/관리")
    with col2:
        handle_logout()
    
    # 성공 메시지 표시
    display_success_message()
    
    # 펜션 정보 로드
    pension_info = load_pension_data()
    
    # 현재 펜션 정보가 있으면 표시 및 관리 기능 제공
    if pension_info is not None:
        # 현재 등록된 펜션 정보 표시
        display_current_pensions(pension_info)
        
        # 펜션 정보 수정/삭제 기능
        st.subheader("펜션 정보 수정/삭제")
        
        # 펜션 수정 처리
        pension_info = handle_pension_edit(pension_info)
        
        # 펜션 삭제 처리
        pension_info = handle_pension_delete(pension_info)
    
    # 새 펜션 추가 기능
    handle_add_new_pension()

if __name__ == "__main__":
    show_add_pension_page() 