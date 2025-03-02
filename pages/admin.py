import streamlit as st
import pandas as pd
import os
from pathlib import Path
from src.common import Naver

naver = Naver()

def show_admin_page():
    if 'password_verified' not in st.session_state:
        st.session_state.password_verified = False
    
    if 'password_error' not in st.session_state:
        st.session_state.password_error = False

    # 비밀번호 검증 함수
    def verify_password():
        password = st.session_state.password_input
        if password == "200219":
            st.session_state.password_verified = True
            st.session_state.password_error = False
        else:
            st.session_state.password_error = True

    if not st.session_state.password_verified:
        st.subheader("🔒 관리자 로그인")
        
        # 자동 포커스를 위한 JavaScript 코드 추가
        st.components.v1.html("""
        <script>
        // 페이지 로드 후 일정 시간 후에 포커스 시도
        setTimeout(function() {
            const inputs = parent.document.querySelectorAll('input[type="password"]');
            if (inputs.length > 0) {
                inputs[0].focus();
            }
        }, 800);
        </script>
        """, height=0)
        
        # 비밀번호가 틀렸을 때 에러 메시지 표시
        if st.session_state.password_error:
            st.error("비밀번호가 틀렸습니다. 다시 시도해주세요.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input(
                "비밀번호를 입력하세요", 
                type="password", 
                key="password_input", 
                label_visibility="collapsed", 
                on_change=verify_password
            )
        with col2:
            st.button(
                "확인", 
                key="password_button", 
                use_container_width=False,
                on_click=verify_password
            )
        return

    st.subheader("🐾관리자 메뉴")
    
    # 기존 펜션 정보 파일 로드
    csv_path = './static/pension_info.csv'
    if os.path.exists(csv_path):
        pension_info = pd.read_csv(csv_path)
        
        # 현재 펜션 정보 표시
        st.subheader("현재 등록된 펜션 정보")
        pension_info['businessId'] = pension_info['businessId'].astype(str)
        pension_info['bizItemId'] = pension_info['bizItemId'].astype(str)
        st.dataframe(pension_info, use_container_width=True, hide_index=True)
        
        # 펜션 정보 수정/삭제 기능
        st.subheader("펜션 정보 수정/삭제")
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
            if selected_business:
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
                
                if not selected_pension.empty:
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
                    col1, col2 = st.columns(2)
                    address = st.text_input(
                        "주소", 
                        value=selected_pension['address_new']
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
                            pension_info.loc[idx, 'address_new'] = address
                            
                            # 변경된 정보 저장
                            pension_info.to_csv(csv_path, index=False)
                            st.success(f"{selected_business} - {selected_item} 정보가 수정되었습니다.")
                            st.rerun()  # 페이지 새로고침
                else:
                    st.error("선택한 펜션 정보가 없습니다.")
        
        # 펜션 삭제 기능
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
                    pension_info = pension_info[
                        pension_info['businessName'] != selected_business_to_delete
                    ]
                    st.success(f"{selected_business_to_delete}의 모든 정보가 삭제되었습니다.")
                else:
                    # 선택한 펜션의 특정 상품만 삭제
                    pension_info = pension_info[
                        ~((pension_info['businessName'] == selected_business_to_delete) & 
                          (pension_info['bizItemName'] == selected_item_to_delete))
                    ]
                    st.success(f"{selected_business_to_delete} - {selected_item_to_delete} 정보가 삭제되었습니다.")
                
                # 변경된 정보 저장
                pension_info.to_csv(csv_path, index=False)
                st.dataframe(
                    pension_info, 
                    use_container_width=True, 
                    hide_index=True
                )  # 삭제 후 데이터프레임 갱신
                st.rerun()  # 페이지 새로고침
    
    # 새 펜션 추가 기능
    st.subheader("새 펜션 추가")
    with st.form("add_pension_form"):
        col1, col2 = st.columns((1, 1))
        with col1:
            new_business_name = st.text_input("펜션 이름")
        with col2:
            new_business_id = st.text_input("업체 ID")
        col1, col2 = st.columns((1, 1))
        with col1:
            new_address_old = st.text_input("신주소")
        with col2:
            new_address_new = st.text_input("구주소")
        
        # 추가 버튼
        button_add = st.form_submit_button("펜션 추가")
        if button_add:
            naver.insert_pension_info(
                new_business_name, 
                new_business_id, 
                new_address_old, 
                new_address_new
            )
            st.success("펜션 추가 완료")

    # 로그아웃 버튼
    if st.button("로그아웃", key="logout", type="primary"):
        st.session_state.password_verified = False
        st.rerun()

if __name__ == "__main__":
    show_admin_page() 