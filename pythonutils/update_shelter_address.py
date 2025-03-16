import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from src.data import Public

public = Public()

def update_shelter_address():
    public.update_shelter_info()
    """
    보호소코드.csv 파일에 주소 칼럼을 추가하고 petinshelter.csv 파일에서 주소 정보를 가져와 업데이트합니다.
    """
    # 파일 경로 설정
    shelter_code_path = os.path.join("static", "database", "보호소코드.csv")
    pet_in_shelter_path = os.path.join("static", "database", "petinshelter.csv")
    output_path = os.path.join("static", "database", "보호소코드.csv")
    
    # 데이터 로드
    print(f"보호소코드 파일 로드 중...")
    shelter_code_df = pd.read_csv(shelter_code_path)
    print(f"보호소코드 파일 로드 완료. 총 {len(shelter_code_df)}개 보호소 정보가 있습니다.")
    
    print(f"유기동물 데이터 파일 로드 중...")
    pet_in_shelter_df = pd.read_csv(pet_in_shelter_path)
    print(f"유기동물 데이터 파일 로드 완료. 총 {len(pet_in_shelter_df)}개 데이터가 있습니다.")
    
    # 보호소명과 주소 매핑 생성
    print("보호소명과 주소 매핑 생성 중...")
    # 중복 제거 및 NA 값 제외
    shelter_address_map = pet_in_shelter_df[['careNm', 'careAddr']].dropna().drop_duplicates()
    print(f"총 {len(shelter_address_map)}개의 고유한 보호소-주소 매핑을 찾았습니다.")
    
    # 주소 칼럼 추가
    shelter_code_df['주소'] = shelter_code_df.get('주소', '')
    
    # 매핑을 통해 주소 업데이트
    print("주소 정보 업데이트 중...")
    updated_count = 0
    
    # 모든 보호소코드 항목에 대해
    for idx, row in shelter_code_df.iterrows():
        shelter_name = row['보호소명']
        
        # 보호소명으로 주소 찾기
        matching_shelters = shelter_address_map[shelter_address_map['careNm'] == shelter_name]
        
        if not matching_shelters.empty and row['주소'] == '':
            # 첫 번째 일치하는 주소 사용
            shelter_code_df.at[idx, '주소'] = matching_shelters.iloc[0]['careAddr']
            updated_count += 1
    
    print(f"총 {updated_count}개 보호소의 주소 정보가 업데이트되었습니다.")
    
    # 결과 저장
    shelter_code_df['lat'] = shelter_code_df.get('lat', '')
    shelter_code_df['lon'] = shelter_code_df.get('lng', '')
    shelter_code_df.to_csv(output_path, index=False)
    print(f"업데이트된 보호소 정보가 '{output_path}'에 저장되었습니다.")
    
    # 업데이트 실패한 보호소 정보 출력
    not_updated = shelter_code_df[shelter_code_df['주소'] == '']
    if not not_updated.empty:
        print(f"\n{len(not_updated)}개 보호소의 주소 정보를 찾을 수 없습니다.")
        print("주소 정보를 찾을 수 없는 보호소 목록 (처음 10개):")
        for name in not_updated['보호소명'].head(10):
            print(f"- {name}")

if __name__ == "__main__":
    update_shelter_address() 