import sys
import os
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from src.data import Naver, Public, AKC, Common
# 순환 참조 방지: UI와 BreedInfo는 필요한 함수 내에서 import
# from src.ui import UI, BreedInfo
from datetime import datetime, timedelta
import pandas as pd
from tqdm import tqdm

def test_naver_waiting_status():
    """네이버 대기 상태 테스트"""
    naver = Naver()
    data = naver._waiting_status("1010023")
    print(data)

def test_naver_schedule():
    """네이버 일정 가져오기 테스트"""
    naver = Naver()
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    data = naver.get_schedule("630736", "4739353", "2025-03-01", "2025-03-31")
    print(data)

def test_naver_booking_list():
    """네이버 예약 목록 테스트"""
    naver = Naver()
    business_name = '펜션숲'
    business_id = '630736'
    result = naver.get_booking_list(business_id)
    result['businessName'] = business_name
    result['businessId'] = business_id
    print(result)

def test_naver_pension_info():
    """네이버 펜션 정보 테스트"""
    naver = Naver()
    # 펜션 정보 삽입 테스트
    # naver.insert_pension_info('펜션숲', '630736')
    # 펜션 정보 가져오기 테스트
    result = naver.get_pension_info('13414710')
    print(result)
    # 또 다른 펜션 정보 삽입 테스트
    # naver.insert_pension_info('1223109', '1306861767')

def test_naver_rating():
    """네이버 평점 정보 테스트"""
    naver = Naver()
    result = naver._get_rating('1110323563')
    print(result)

def test_naver_rating_all():
    """모든 펜션의 네이버 평점 정보 수집 테스트"""
    naver = Naver()
    pension_info = pd.read_csv('./static/database/pension_info.csv')[['businessName', 'channelId']].drop_duplicates()
    rating_data = pd.DataFrame()
    for index, row in tqdm(pension_info.iterrows(), total=len(pension_info)):
        result = naver._get_rating(row['channelId'])
        result['businessName'] = row['businessName']
        result['channelId'] = row['channelId']
        rating_data = pd.concat([rating_data, result], ignore_index=True)
    print(rating_data)
    rating_data.to_csv('./static/database/rating_data.csv', index=False)

def test_naver_photo():
    """네이버 사진 정보 테스트"""
    naver = Naver()
    rating_data = naver.get_photo('1306861767')
    print(rating_data)

def test_public_shelter_info():
    """공공 데이터 - 보호소 정보 업데이트 테스트"""
    public = Public()
    public.update_shelter_info()

def test_public_find_pet():
    """공공 데이터 - 유기동물 찾기 테스트"""
    public = Public()
    result = public.find_pet()
    print(result)

def test_public_pet_info():
    """공공 데이터 - 특정 유기동물 정보 테스트"""
    desertion_no = int('448536202500200')
    petinshelter = pd.read_csv('./static/database/petinshelter.csv')
    selected_pet = petinshelter[petinshelter['desertionNo'] == desertion_no]
    print(selected_pet)

def test_akc_breed_info():
    """AKC 견종 정보 테스트"""
    akc = AKC()
    result = akc.get_breed_info('korean-jindo-dog')
    print(result)
    result = akc.get_breed_info('german-spitz')
    print(result)

def test_akc_breed_info_all():
    """모든 AKC 견종 정보 수집 테스트"""
    akc = AKC()
    result = akc.get_breed_info_all()
    result.to_csv('./static/database/akcBreedInfo.csv', index=False)

def test_akc_breed_info_deduplicate():
    """AKC 견종 정보 중복 제거 테스트"""
    result = pd.read_csv('./static/database/akcBreedInfo.csv')
    result = result.drop_duplicates(subset=['breed_name'])
    result.to_csv('./static/database/akcBreedInfo.csv', index=False)

def test_breed_info_basic():
    """견종 기본 정보 표시 테스트"""
    # 지연 import로 순환 참조 방지
    from src.ui import BreedInfo
    breed_info = BreedInfo()
    result = breed_info.get_breed_info_basic('진도견')
    print(result)

def test_breed_trait():
    """견종 특성 정보 표시 테스트"""
    # 지연 import로 순환 참조 방지
    from src.ui import BreedInfo
    breed_info = BreedInfo()
    CoatType, CoatLength = breed_info.show_breed_trait('진도견')
    print(CoatType, CoatLength)

def test_pension_geo():
    """펜션 지리 정보 변환 테스트"""
    common = Common()
    result = common.convert_pension_geo()
    print(result)

def test_coat_type_extraction():
    """코트 타입 추출 테스트"""
    result = pd.read_csv('./static/database/akcBreedInfo.csv')
    result = result['Coat Length'].drop_duplicates()
    coat_type_list = []
    for coat_types in tqdm(result, total=len(result)):
        coat_type = coat_types.split(',')
        for coat_type in coat_type:
            coat_type = coat_type.replace("'", "").replace("[", "").replace("]", "")
            coat_type = coat_type.strip()
            coat_type_list.append(coat_type)

    coat_type_list = list(set(coat_type_list))
    print(coat_type_list)

def test_akc_breed_info_display():
    """AKC 견종 정보 확인 테스트"""
    result = pd.read_csv('./static/database/akcBreedInfo.csv')
    print(result.head())
    print(f"Total breeds: {len(result)}")
    print(f"Columns: {result.columns.tolist()}")

def list_functions():
    """사용 가능한 함수 목록 출력"""
    functions = [name for name in globals() if name.startswith('test_')]
    print("사용 가능한 테스트 함수:")
    for i, func in enumerate(functions, 1):
        doc = globals()[func].__doc__ or "설명 없음"
        print(f"{i}. {func}: {doc}")
    return functions

def main():
    """메인 함수"""
    if len(sys.argv) > 1:
        func_name = sys.argv[1]
        if func_name in globals() and func_name.startswith('test_'):
            print(f"Running {func_name}...")
            globals()[func_name]()
        else:
            print(f"Unknown function: {func_name}")
            functions = list_functions()
    else:
        print("테스트할 함수를 지정하세요. 예: python makepython.py test_akc_breed_info_display")
        functions = list_functions()

if __name__ == "__main__":
    main() 