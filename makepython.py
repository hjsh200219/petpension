from src.data import Naver, Public, AKC, Common
from src.ui import UI, BreedInfo
from datetime import datetime, timedelta
import pandas as pd
from tqdm import tqdm
from pathlib import Path

naver = Naver()
akc = AKC()
ui = UI()
breed_info = BreedInfo()
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


# pension_info = pd.read_csv('./static/database/pension_info.csv')[['businessName', 'channelId']].drop_duplicates()
# rating_data = pd.DataFrame()
# for index, row in tqdm(pension_info.iterrows(), total=len(pension_info)):
#     result = naver._get_rating(row['channelId'])
#     result['businessName'] = row['businessName']
#     result['channelId'] = row['channelId']
#     rating_data = pd.concat([rating_data, result], ignore_index=True)
# print(rating_data)
# rating_data.to_csv('./static/database/rating_data.csv', index=False)

# rating_data = pd.read_csv('./static/database/rating_data.csv')

# rating_data = naver.get_photo('1306861767')
# print(rating_data)


# Public 클래스의 인스턴스 생성
# public = Public()

# file_dir = Path('./static/database')

# public.update_shelter_info()

# result = public.find_pet()
# print(result)

# desertion_no = int('448536202500200')
# petinshelter = pd.read_csv('./static/database/petinshelter.csv')
# selected_pet = petinshelter[petinshelter['desertionNo'] == desertion_no]
# print(selected_pet)


# result = akc.get_breed_info('korean-jindo-dog')
# print(result)
# result = akc.get_breed_info('german-spitz')
# print(result)

# result = akc.get_breed_info_all()
# result.to_csv('./static/database/akcBreedInfo.csv', index=False)


# result = pd.read_csv('./static/database/akcBreedInfo.csv')
# result = result.drop_duplicates(subset=['breed_name'])
# result.to_csv('./static/database/akcBreedInfo.csv', index=False)

# result = breed_info.show_breed_info_basic('진도견')

# CoatType, CoatLength = breed_info.show_breed_trait('진도견')
# print(CoatType, CoatLength)

result = Common().convert_pension_geo()
print(result)