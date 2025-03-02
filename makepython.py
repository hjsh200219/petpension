from src.common import Naver
from datetime import datetime, timedelta
import pandas as pd
naver = Naver()

# data = naver._waiting_status("1010023")
# print(data)


# start_date = datetime.now().strftime("%Y-%m-%d")
# end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

# data = naver.get_schedule("630736", "4739353", "2025-03-01", "2025-03-31")
# print(data)


# business_name = '펜션숲'
# business_id = '630736'
# result = naver.get_booking_list(business_id)

# result['businessName'] = business_name
# result['businessId'] = business_id

# print(result)

# naver.insert_pension_info('펜션숲', '630736')

# result = naver.get_pension_info('13414710')

naver.insert_pension_info('1223109', '1306861767')

# result = naver.get_rating('1306861767')
# print(result)
