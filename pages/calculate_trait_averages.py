import pandas as pd
import os

def calculate_trait_averages():
    """
    akcBreedInfo.csv 파일에서 특성 컬럼들의 평균값을 계산하고 CSV 파일로 저장합니다.
    """
    # 파일 경로 설정
    input_file_path = os.path.join("static", "database", "akcBreedInfo.csv")
    output_file_path = os.path.join("static", "database", "trait_averages.csv")
    
    # 데이터 로드
    try:
        df = pd.read_csv(input_file_path)
        print(f"파일을 성공적으로 로드했습니다: {input_file_path}")
    except Exception as e:
        print(f"파일 로드 중 오류 발생: {str(e)}")
        return
    
    # 특성 컬럼 목록
    trait_columns = [
        "Affectionate With Family", "Good With Young Children", 
        "Good With Other Dogs", "Shedding Level", "Coat Grooming Frequency",
        "Drooling Level", "Openness To Strangers", "Playfulness Level",
        "Watchdog/Protective Nature", "Adaptability Level", "Trainability Level",
        "Energy Level", "Barking Level", "Mental Stimulation Needs"
    ]
    
    # 각 특성의 평균값 계산
    try:
        trait_averages = df[trait_columns].mean().reset_index()
        trait_averages.columns = ['trait', 'average_score']
        
        # 소수점 두 자리까지 반올림
        trait_averages['average_score'] = trait_averages['average_score'].round(2)
        
        print("특성 평균 계산 완료:")
        print(trait_averages)
    except Exception as e:
        print(f"평균 계산 중 오류 발생: {str(e)}")
        return
    
    # 결과를 CSV 파일로 저장
    try:
        trait_averages.to_csv(output_file_path, index=False)
        print(f"결과가 성공적으로 저장되었습니다: {output_file_path}")
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {str(e)}")

# 메인 실행 코드
if __name__ == "__main__":
    calculate_trait_averages() 