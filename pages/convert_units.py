import pandas as pd
import re
import ast

# 단위 변환 상수
INCH_TO_CM = 2.54
POUND_TO_KG = 0.453592
LBS_TO_KG = 0.453592  # lbs도 파운드와 동일

def clean_value(value):
    """문자열에서 숫자 부분만 추출하는 함수"""
    if isinstance(value, str):
        # 숫자 부분만 추출 (소수점 포함)
        match = re.search(r'(\d+(?:\.\d+)?)', value)
        if match:
            return float(match.group(1))
    return None

def extract_range(text):
    """텍스트에서 범위 값(시작-끝)을 추출하는 함수"""
    if isinstance(text, str):
        match = re.search(r'(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)', text)
        if match:
            return float(match.group(1)), float(match.group(2))
    return None, None

def extract_special_format(text):
    """특수한 형식(예: '22-25 inches (males); 20-23 inches (females)')에서 값 추출"""
    if isinstance(text, str):
        # 수컷 부분 추출
        male_pattern = r'(\d+(?:\.\d+)?-\d+(?:\.\d+)?)\s*(?:inches|inch|pounds|pound|lbs)\s*\(males?\)'
        male_match = re.search(male_pattern, text)
        if not male_match:
            # 세미콜론 앞에 있는 경우
            male_match = re.search(r'(\d+(?:\.\d+)?-\d+(?:\.\d+)?)\s*(?:inches|inch|pounds|pound|lbs)\s*\(males?\);', text)
        
        # 암컷 부분 추출
        female_pattern = r'(\d+(?:\.\d+)?-\d+(?:\.\d+)?)\s*(?:inches|inch|pounds|pound|lbs)\s*\(females?\)'
        female_match = re.search(female_pattern, text)
        
        male_value = male_match.group(1) if male_match else None
        female_value = female_match.group(1) if female_match else None
            
        return male_value, female_value
    return None, None

def convert_life_expectancy(life_expectancy_data):
    """수명 데이터를 한글(년)로 변환"""
    try:
        # 문자열로 된 리스트를 실제 리스트로 변환
        if isinstance(life_expectancy_data, str):
            life_expectancy_list = ast.literal_eval(life_expectancy_data)
        else:
            life_expectancy_list = life_expectancy_data
            
        result = []
        
        for item in life_expectancy_list:
            # 범위 형식 (예: '10-14 years')
            start, end = extract_range(item)
            if start and end:
                result.append(f"{int(start)}-{int(end)}년")
            else:
                # 단일 값 (예: '15 years')
                value = clean_value(item)
                if value:
                    result.append(f"{int(value)}년")
        
        # 결과 조합
        if result:
            return ', '.join(result)
        else:
            return ""
        
    except Exception as e:
        print(f"수명 변환 중 오류 발생: {e}, 데이터: {life_expectancy_data}")
        return ""

def convert_height(height_data):
    """높이 데이터를 인치에서 센티미터로 변환"""
    try:
        # 문자열로 된 리스트를 실제 리스트로 변환
        if isinstance(height_data, str):
            height_list = ast.literal_eval(height_data)
        else:
            height_list = height_data
            
        result = []
        male_values = []
        female_values = []
        standard_values = []
        
        for item in height_list:
            # 특수 형식 처리 (예: '22-25 inches (males); 20-23 inches (females)')
            if ';' in item and ('males' in item.lower() or 'females' in item.lower()):
                try:
                    male_value, female_value = extract_special_format(item)
                    
                    if male_value:
                        start, end = extract_range(male_value)
                        if start and end:
                            male_values.append(f"{round(start * INCH_TO_CM)}-{round(end * INCH_TO_CM)}cm")
                    
                    if female_value:
                        start, end = extract_range(female_value)
                        if start and end:
                            female_values.append(f"{round(start * INCH_TO_CM)}-{round(end * INCH_TO_CM)}cm")
                except Exception as e:
                    print(f"특수 형식 처리 중 오류: {e}, 데이터: {item}")
                
                continue
            
            if '(male)' in item.lower() or '(males)' in item.lower():
                # 수컷 높이
                start, end = extract_range(item)
                if start and end:
                    male_values.append(f"{round(start * INCH_TO_CM)}-{round(end * INCH_TO_CM)}cm")
                else:
                    value = clean_value(item)
                    if value:
                        male_values.append(f"{round(value * INCH_TO_CM)}cm")
            elif '(female)' in item.lower() or '(females)' in item.lower():
                # 암컷 높이
                start, end = extract_range(item)
                if start and end:
                    female_values.append(f"{round(start * INCH_TO_CM)}-{round(end * INCH_TO_CM)}cm")
                else:
                    value = clean_value(item)
                    if value:
                        female_values.append(f"{round(value * INCH_TO_CM)}cm")
            elif '(toy)' in item.lower():
                standard_values.append(f"토이: {round(clean_value(item) * INCH_TO_CM)}cm")
            elif '(miniature)' in item.lower():
                standard_values.append(f"미니어처: {round(clean_value(item) * INCH_TO_CM)}cm")
            elif '(standard)' in item.lower():
                standard_values.append(f"스탠다드: {round(clean_value(item) * INCH_TO_CM)}cm")
            else:
                # 성별 구분 없는 경우
                start, end = extract_range(item)
                if start and end:
                    standard_values.append(f"{round(start * INCH_TO_CM)}-{round(end * INCH_TO_CM)}cm")
                else:
                    value = clean_value(item)
                    if value:
                        standard_values.append(f"{round(value * INCH_TO_CM)}cm")
        
        # 결과 조합
        if male_values and female_values:
            return f"수컷: {', '.join(male_values)}, 암컷: {', '.join(female_values)}"
        elif standard_values:
            return ', '.join(standard_values)
        else:
            return ""
        
    except Exception as e:
        print(f"높이 변환 중 오류 발생: {e}, 데이터: {height_data}")
        return ""

def convert_weight(weight_data):
    """무게 데이터를 파운드에서 킬로그램으로 변환"""
    try:
        # 문자열로 된 리스트를 실제 리스트로 변환
        if isinstance(weight_data, str):
            weight_list = ast.literal_eval(weight_data)
        else:
            weight_list = weight_data
            
        result = []
        male_values = []
        female_values = []
        standard_values = []
        
        for item in weight_list:
            # 특수 형식 처리 (예: '75-100 pounds (males); 60-80 pounds (females)')
            if ';' in item and ('males' in item.lower() or 'females' in item.lower()):
                try:
                    male_value, female_value = extract_special_format(item)
                    
                    if male_value:
                        start, end = extract_range(male_value)
                        if start and end:
                            male_values.append(f"{round(start * POUND_TO_KG)}-{round(end * POUND_TO_KG)}kg")
                    
                    if female_value:
                        start, end = extract_range(female_value)
                        if start and end:
                            female_values.append(f"{round(start * POUND_TO_KG)}-{round(end * POUND_TO_KG)}kg")
                except Exception as e:
                    print(f"특수 형식 처리 중 오류: {e}, 데이터: {item}")
                
                continue
            
            if '(male)' in item.lower() or '(males)' in item.lower():
                # 수컷 무게
                start, end = extract_range(item)
                if start and end:
                    male_values.append(f"{round(start * POUND_TO_KG)}-{round(end * POUND_TO_KG)}kg")
                else:
                    value = clean_value(item)
                    if value:
                        male_values.append(f"{round(value * POUND_TO_KG)}kg")
            elif '(female)' in item.lower() or '(females)' in item.lower():
                # 암컷 무게
                start, end = extract_range(item)
                if start and end:
                    female_values.append(f"{round(start * POUND_TO_KG)}-{round(end * POUND_TO_KG)}kg")
                else:
                    value = clean_value(item)
                    if value:
                        female_values.append(f"{round(value * POUND_TO_KG)}kg")
            elif '(toy)' in item.lower():
                # 토이 크기
                start, end = extract_range(item)
                if start and end:
                    standard_values.append(f"토이: {round(start * POUND_TO_KG)}-{round(end * POUND_TO_KG)}kg")
                else:
                    value = clean_value(item)
                    if value:
                        standard_values.append(f"토이: {round(value * POUND_TO_KG)}kg")
            elif '(miniature)' in item.lower():
                # 미니어처 크기
                start, end = extract_range(item)
                if start and end:
                    standard_values.append(f"미니어처: {round(start * POUND_TO_KG)}-{round(end * POUND_TO_KG)}kg")
                else:
                    value = clean_value(item)
                    if value:
                        standard_values.append(f"미니어처: {round(value * POUND_TO_KG)}kg")
            elif '(standard)' in item.lower():
                # 스탠다드 크기
                start, end = extract_range(item)
                if start and end:
                    standard_values.append(f"스탠다드: {round(start * POUND_TO_KG)}-{round(end * POUND_TO_KG)}kg")
                else:
                    value = clean_value(item)
                    if value:
                        standard_values.append(f"스탠다드: {round(value * POUND_TO_KG)}kg")
            else:
                # 성별 구분 없는 경우
                start, end = extract_range(item)
                if start and end:
                    standard_values.append(f"{round(start * POUND_TO_KG)}-{round(end * POUND_TO_KG)}kg")
                else:
                    # 'lbs' 또는 'pounds' 포함 여부에 따라 변환 상수 선택
                    converter = LBS_TO_KG if 'lbs' in item.lower() else POUND_TO_KG
                    value = clean_value(item)
                    if value:
                        standard_values.append(f"{round(value * converter)}kg")
        
        # 결과 조합
        if male_values and female_values:
            return f"수컷: {', '.join(male_values)}, 암컷: {', '.join(female_values)}"
        elif standard_values:
            return ', '.join(standard_values)
        else:
            return ""
        
    except Exception as e:
        print(f"무게 변환 중 오류 발생: {e}, 데이터: {weight_data}")
        return ""

def process_american_bulldog(df):
    """american-bulldog와 같은 특수 케이스를 직접 처리"""
    try:
        # american-bulldog 행 찾기
        idx = df[df['breed_name'] == 'american-bulldog'].index
        if len(idx) > 0:
            # 높이 변환
            df.at[idx[0], 'height_k'] = "수컷: 56-64cm, 암컷: 51-58cm"
            # 무게 변환
            df.at[idx[0], 'weight_k'] = "수컷: 34-45kg, 암컷: 27-36kg"
    except Exception as e:
        print(f"american-bulldog 처리 중 오류: {e}")

try:
    # 파일 읽기
    df = pd.read_csv('/Users/hoshin/workspace/petpension/static/database/akcBreedInfo.csv')
    
    # 새 칼럼 추가 및 단위 변환
    df['height_k'] = df['height'].apply(convert_height)
    df['weight_k'] = df['weight'].apply(convert_weight)
    df['life_expectancy_k'] = df['life_expectancy'].apply(convert_life_expectancy)
    
    # 특수 케이스 직접 처리
    process_american_bulldog(df)
    
    # 결과 저장
    df.to_csv('/Users/hoshin/workspace/petpension/static/database/akcBreedInfo.csv', index=False)
    print("단위 변환이 완료되었습니다. 파일이 성공적으로 생성되었습니다: akcBreedInfo.csv")

except Exception as e:
    print(f"오류 발생: {str(e)}") 