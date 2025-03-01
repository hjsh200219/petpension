import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.common import Naver

naver = Naver()

# 페이지 설정
st.set_page_config(
    page_title="Pet Companion",
    page_icon="🐾",
    layout="wide"
)

# 메인 타이틀
st.title("🐾반려동물 숙박시설")

# 날짜 선택
col1, col2, col3 = st.columns((1,1,3))
with col1:
    start_date = st.date_input(
        "시작 날짜", 
        datetime.now(), 
        label_visibility="collapsed"
    )
with col2:
    end_date = st.date_input(
        "종료 날짜", 
        datetime.now() + timedelta(days=30), 
        label_visibility="collapsed")
with col3:
    search_button = st.button("일정 조회", key="unique_schedule_button", use_container_width=False)

# CSV 파일에서 데이터 읽기
pension_info = pd.read_csv('./static/pension_info.csv')

# 선택된 날짜와 bizItemId로 get_schedule 실행
if 'result' not in st.session_state:
    st.session_state.result = pd.DataFrame()

if search_button:  # 고유 키 추가
    result = pd.DataFrame()
    for row in pension_info.itertuples(index=False):
        businessId = str(row.businessId).strip()
        biz_item_id = str(row.bizItemId).strip()

        schedule_data = naver.get_schedule(
            businessId, 
            biz_item_id, 
            start_date.strftime("%Y-%m-%d"), 
            end_date.strftime("%Y-%m-%d")
        )
        schedule_data['businessName'] = row.businessName
        schedule_data['bizItemName'] = row.bizItemName
        schedule_data['address'] = row.address_new
        print(schedule_data)
        
        # 결과를 필터링하고 필요한 열만 선택
        filtered_schedule_data = schedule_data[schedule_data['isSaleDay'] == True]
        filtered_schedule_data = filtered_schedule_data[['businessName', 'bizItemName', 'date', 'prices', 'address']].rename(columns={
            'businessName': '숙박업소', 
            'bizItemName': '숙박상품', 
            'date': '날짜', 
            'prices': '가격',
            'address': '주소'
        })
        
        result = pd.concat([result, filtered_schedule_data], ignore_index=True)  # 결과를 누적 저장

    st.session_state.result = pd.concat([st.session_state.result, result], ignore_index=True)

    if not st.session_state.result.empty:
        st.success("일정 조회가 완료되었습니다.")
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            business_name_filter = st.selectbox("숙박업소 선택", options=["전체"] + list(st.session_state.result['숙박업소'].unique()))
            if business_name_filter != "전체":
                filtered_result = st.session_state.result[st.session_state.result['숙박업소'] == business_name_filter]
            else:
                filtered_result = st.session_state.result

        with filter_col2:
            biz_item_name_filter = st.selectbox("숙박상품 선택", options=["전체"] + list(st.session_state.result['숙박상품'].unique()))
            if biz_item_name_filter != "전체":
                filtered_result = filtered_result[filtered_result['숙박상품'] == biz_item_name_filter]
        
        st.dataframe(
            filtered_result, 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("조회된 일정이 없습니다.")

# streamlit run app.py