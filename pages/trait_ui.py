import streamlit as st
import pandas as pd
import os

class BreedTraitUI:
    def __init__(self):
        # 데이터 파일 경로
        breed_info_path = os.path.join("static", "database", "akcBreedInfo.csv")
        trait_info_path = os.path.join("static", "database", "trait_descriptions.csv")
        
        # 데이터 로드
        self.breed_info = pd.read_csv(breed_info_path)
        
        # trait_descriptions.csv 파일이 없는 경우를 대비해 기본 정보 설정
        try:
            self.trait_info = pd.read_csv(trait_info_path)
        except FileNotFoundError:
            # 기본 특성 정보 생성
            self.create_default_trait_info()
    
    def create_default_trait_info(self):
        """기본 특성 정보 생성"""
        traits = [
            "Affectionate With Family", "Good With Young Children", 
            "Good With Other Dogs", "Shedding Level", "Coat Grooming Frequency",
            "Drooling Level", "Openness To Strangers", "Playfulness Level",
            "Watchdog/Protective Nature", "Adaptability Level", "Trainability Level",
            "Energy Level", "Barking Level", "Mental Stimulation Needs"
        ]
        
        trait_desc = [
            "가족에 대한 애정", "어린 아이들과의 호환성", 
            "다른 개들과의 호환성", "털 빠짐 정도", "털 손질 빈도",
            "침 흘림 정도", "낯선 사람에 대한 개방성", "장난기 정도",
            "경계/보호 본능", "적응성", "훈련 가능성",
            "에너지 레벨", "짖는 정도", "정신적 자극 필요성"
        ]
        
        score_low = [
            "덜 애정적", "아이들과 덜 호환됨", 
            "다른 개와 덜 호환됨", "적게 빠짐", "적은 털 손질 필요",
            "적게 흘림", "낯선 사람에게 경계적", "덜 장난스러움",
            "경계심 낮음", "적응력 낮음", "훈련이 어려움",
            "에너지 낮음", "조용함", "적은 자극 필요"
        ]
        
        score_high = [
            "매우 애정적", "아이들과 매우 호환됨", 
            "다른 개와 매우 호환됨", "많이 빠짐", "많은 털 손질 필요",
            "많이 흘림", "낯선 사람에게 친근함", "매우 장난스러움",
            "경계심 높음", "적응력 높음", "훈련이 쉬움",
            "에너지 높음", "많이 짖음", "많은 자극 필요"
        ]
        
        # 데이터프레임 생성
        data = {
            'trait': traits,
            'trait_desc': trait_desc,
            'score_low': score_low,
            'score_high': score_high
        }
        
        self.trait_info = pd.DataFrame(data)
    
    def show_breed_trait_5scale(self, breed_name, trait):
        """품종의 특정 특성에 대한 5단계 스케일 UI 표시"""
        try:
            # 품종 특성 점수 조회
            score = self.breed_info[self.breed_info['breed_name_kor'] == breed_name][trait].values[0]
            
            # 특성 설명 조회
            trait_row = self.trait_info[self.trait_info['trait'] == trait]
            if len(trait_row) > 0:
                trait_desc = trait_row['trait_desc'].values[0]
                score_low = trait_row['score_low'].values[0]
                score_high = trait_row['score_high'].values[0]
            else:
                trait_desc = trait
                score_low = "낮음"
                score_high = "높음"
            
            # 점수가 없는 경우 처리
            if pd.isna(score):
                score = 0
            
            # UI 표시
            st.write(f"**{trait_desc}**")
            
            # 점수 스케일 시각화
            col1, col2, col3, col4, col5 = st.columns(5)
            
            # 각 열에 적절한 배경색 설정
            for i, col in enumerate([col1, col2, col3, col4, col5], 1):
                if i <= score:
                    col.markdown(
                        f"""
                        <div style="
                            background-color: #4F7CAC; 
                            color: white; 
                            padding: 10px; 
                            border-radius: 5px; 
                            text-align: center;
                            height: 20px;
                        "></div>
                        """, 
                        unsafe_allow_html=True
                    )
                else:
                    col.markdown(
                        f"""
                        <div style="
                            background-color: #E0E0E0; 
                            color: white; 
                            padding: 10px; 
                            border-radius: 5px; 
                            text-align: center;
                            height: 20px;
                        "></div>
                        """, 
                        unsafe_allow_html=True
                    )
            
            # 점수 설명
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                    <div style="color: #666; font-size: 0.8em;">{score_low}</div>
                    <div style="color: #666; font-size: 0.8em;">{score_high}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            return score, trait_desc, score_low, score_high
        
        except Exception as e:
            st.error(f"오류 발생: {str(e)}")
            return 0, trait, "낮음", "높음"
    
    def show_all_breed_traits(self, breed_name):
        """품종의 모든 특성을 표시"""
        st.subheader(f"{breed_name}의 특성")
        
        # 표시할 특성 목록
        traits = [
            "Affectionate With Family", "Good With Young Children", 
            "Good With Other Dogs", "Shedding Level", "Coat Grooming Frequency",
            "Drooling Level", "Openness To Strangers", "Playfulness Level",
            "Watchdog/Protective Nature", "Adaptability Level", "Trainability Level",
            "Energy Level", "Barking Level", "Mental Stimulation Needs"
        ]
        
        # 각 특성 표시
        for trait in traits:
            self.show_breed_trait_5scale(breed_name, trait)
            st.write("")  # 특성 사이 간격 추가

# 테스트 코드
if __name__ == "__main__":
    st.set_page_config(page_title="개 품종 특성", layout="wide")
    
    # UI 인스턴스 생성
    ui = BreedTraitUI()
    
    # 테스트용 품종 선택
    breed_options = ui.breed_info['breed_name_kor'].dropna().unique().tolist()
    if breed_options:
        selected_breed = st.selectbox("품종 선택", options=breed_options)
        
        # 선택한 품종의 모든 특성 표시
        ui.show_all_breed_traits(selected_breed)
    else:
        st.warning("품종 정보를 찾을 수 없습니다. 데이터 파일을 확인해주세요.") 