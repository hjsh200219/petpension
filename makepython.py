from src.common import Naver
from datetime import datetime, timedelta
import pandas as pd
from tqdm import tqdm
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

# naver.insert_pension_info('1223109', '1306861767')

# result = naver._get_rating('1110323563')
# print(result)


# pension_info = pd.read_csv('./static/pension_info.csv')[['businessName', 'channelId']].drop_duplicates()
# rating_data = pd.DataFrame()
# for index, row in tqdm(pension_info.iterrows(), total=len(pension_info)):
#     result = naver._get_rating(row['channelId'])
#     result['businessName'] = row['businessName']
#     result['channelId'] = row['channelId']
#     rating_data = pd.concat([rating_data, result], ignore_index=True)
# print(rating_data)
# rating_data.to_csv('./static/rating_data.csv', index=False)

rating_data = pd.read_csv('./static/rating_data.csv')