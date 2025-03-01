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
start_date = st.date_input("시작 날짜", datetime.now())
end_date = st.date_input("종료 날짜", datetime.now() + timedelta(days=30))

# CSV 파일에서 데이터 읽기
pension_info = pd.read_csv('./static/pension_info.csv')

# 선택된 날짜와 bizItemId로 get_schedule 실행
if st.button("일정 조회"):
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
        schedule_data['businessId'] = row.businessName
        schedule_data['bizItemId'] = row.bizItemName
        schedule_data['address'] = row.address_new
        result = pd.concat([result, schedule_data])
        result = result[result['isSaleDay'] == True]  # 수정된 부분
        result = result[['businessId', 'bizItemId', 'date', 'prices', 'address']].rename(columns={
                        'businessId': '숙박업소', 
                        'bizItemId': '숙박상품', 
                        'date': '날짜', 
                        'prices': '가격',
                        'address': '주소'
                    })

    if not result.empty:
        st.success("일정 조회가 완료되었습니다.")
        st.dataframe(
            result, 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("조회된 일정이 없습니다.")

# streamlit run app.py