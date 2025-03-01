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
            # 수정할 펜션 선택
            pension_to_edit = st.selectbox(
                "수정할 펜션 선택", 
                options=pension_info.apply(lambda row: f"{row['businessName']} - {row['bizItemName']}", axis=1).tolist(),
                key="edit_pension"
            )
            
            # 선택한 펜션 정보 가져오기
            selected_pension = pension_info[pension_info.apply(lambda row: f"{row['businessName']} - {row['bizItemName']}", axis=1) == pension_to_edit]
            if not selected_pension.empty:
                selected_pension = selected_pension.iloc[0]
                
                # 수정 양식
                col1, col2 = st.columns((2,1))
                with col1:
                    business_name = st.text_input("펜션 이름", value=selected_pension['businessName'])
                with col2:
                    business_id = st.text_input("업체 ID", value=selected_pension['businessId'])
                col1, col2 = st.columns((2,1))
                with col1:
                    biz_item_name = st.text_input("객실 이름", value=selected_pension['bizItemName'])
                with col2:
                    biz_item_id = st.text_input("객실 ID", value=selected_pension['bizItemId'])
                col1, col2 = st.columns(2)
                address = st.text_input("주소", value=selected_pension['address_new'])
                
                # 수정 버튼
                if st.button("수정 저장", key="save_edit"):
                    # 선택한 펜션 정보 업데이트
                    pension_info.loc[pension_info['businessName'] == selected_pension['businessName'], 'businessName'] = business_name
                    pension_info.loc[pension_info['businessName'] == selected_pension['businessName'], 'businessId'] = business_id
                    pension_info.loc[pension_info['businessName'] == selected_pension['businessName'], 'bizItemName'] = biz_item_name
                    pension_info.loc[pension_info['businessName'] == selected_pension['businessName'], 'bizItemId'] = biz_item_id
                    pension_info.loc[pension_info['businessName'] == selected_pension['businessName'], 'address_new'] = address
                    
                    # 변경된 정보 저장
                    pension_info.to_csv(csv_path, index=False)
                    st.success(f"{pension_to_edit} 정보가 수정되었습니다.")
                    st.rerun()  # 페이지 새로고침
            else:
                st.error("선택한 펜션 정보가 없습니다.")
        
        # 펜션 삭제 기능
        with st.expander("펜션 정보 삭제"):
            # 삭제할 펜션 선택 (중복 없이 펜션 이름만 표시)
            pension_to_delete = st.selectbox(
                "삭제할 펜션 선택", 
                options=pension_info['businessName'].drop_duplicates().tolist(),
                key="delete_pension"
            )
            
            # 삭제 버튼
            if st.button("펜션 삭제", key="confirm_delete"):
                # 선택한 펜션 정보 삭제
                pension_info = pension_info[pension_info['businessName'] != pension_to_delete]
                
                # 변경된 정보 저장
                pension_info.to_csv(csv_path, index=False)
                st.success(f"{pension_to_delete} 정보가 삭제되었습니다.")
                st.dataframe(pension_info, use_container_width=True, hide_index=True)  # 삭제 후 데이터프레임 갱신
                st.rerun()  # 페이지 새로고침
    
    # 새 펜션 추가 기능
    st.subheader("새 펜션 추가")
    with st.form("add_pension_form"):
        col1, col2 = st.columns((2,1))
        with col1:
            new_business_name = st.text_input("펜션 이름")
        with col2:
            new_business_id = st.text_input("업체 ID")
        
        # 추가 버튼
        button_add = st.form_submit_button("펜션 추가")
        if button_add:
            naver.insert_pension_info(new_business_name, new_business_id)
            st.success("펜션 추가 완료")

    # 로그아웃 버튼
    if st.button("로그아웃", key="logout", type="primary"):
        st.session_state.password_verified = False
        st.rerun()

if __name__ == "__main__":
    show_admin_page() 