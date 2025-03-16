import pandas as pd
import os

def translate_traits():
    """
    akcTraits.csv 파일에 한글 번역 칼럼을 추가하는 함수
    """
    # 파일 경로
    file_path = './static/database/akcTraits.csv'
    
    # CSV 파일 로드
    df = pd.read_csv(file_path)
    
    print(f"파일 로드 완료: {len(df)}개 행 발견")
    
    # 디버깅: 원본 데이터 확인
    print("\n원본 trait 값:")
    for trait in df['trait'].unique():
        print(f"- {trait}")
    
    # 각 칼럼에 대한 한글 번역 딕셔너리 생성
    trait_ko = {
        'Affectionate With Family': '가족과의 애정도',
        'Good With Young Children': '어린 아이들과의 호환성',
        'Good With Other Dogs': '다른 개들과의 호환성',
        'Shedding Level': '털빠짐 정도',
        'Coat Grooming Frequency': '털 관리 빈도',
        'Drooling Level': '침흘림 정도',
        'Coat Type': '털 유형',
        'Coat Length': '털 길이',
        'Openness To Strangers': '낯선 사람에 대한 개방성',
        'Playfulness Level': '장난기 수준',
        'Watchdog/Protective Nature': '경비견/보호 본능',
        'Adaptability Level': '적응력 수준',
        'Trainability Level': '훈련 가능성',
        'Energy Level': '에너지 수준',
        'Barking Level': '짖음 수준',
        'Mental Stimulation Needs': '정신적 자극 필요성'
    }
    
    score_low_ko = {
        'Independent': '독립적',
        'Not Recommended': '권장하지 않음',
        'No Shedding': '털빠짐 없음',
        'Monthly': '월간',
        'Less Likely to Drool': '침을 덜 흘림',
        'Reserved': '내성적',
        'Only When You Want To Play': '원할 때만 놀이',
        "What's Mine Is Yours": '공유 성향',
        'Lives For Routine': '일상에 충실',
        'Self-Willed': '자기주장 강함',
        'Couch Potato': '비활동적',
        'Only To Alert': '경고시에만',
        'Happy to Lounge': '휴식 선호'
    }
    
    score_high_ko = {
        'Lovey-Dovey': '매우 애정적',
        'Good With Children': '아이들과 잘 지냄',
        'Good With Other Dogs': '다른 개들과 잘 지냄',
        'Hair Everywhere': '털이 많이 빠짐',
        'Daily': '매일',
        'Always Have a Towel': '항상 침을 흘림',
        'Everyone Is My Best Friend': '모두와 친함',
        'Non-Stop': '끊임없이 놀이함',
        'Vigilant': '경계심 강함',
        'Highly Adaptable': '매우 적응력 좋음',
        'Eager to Please': '기쁘게 하려는 의지',
        'High Energy': '에너지 넘침',
        'Very Vocal': '매우 시끄러움',
        'Needs a Job or Activity': '활동이 필요함'
    }
    
    # 상세한 trait_desc_ko 번역
    trait_desc_ko = {
        'Affectionate With Family': '이 품종이 가족 구성원이나 잘 아는 사람들에게 얼마나 애정을 표현하는지를 나타냅니다. 일부 품종은 주인 외에는 모든 사람에게 냉담할 수 있는 반면, 다른 품종은 알고 지내는 모든 사람을 가장 친한 친구처럼 대합니다.',
        'Good With Young Children': '아이들의 행동에 대한 품종의 인내심과 내성 수준, 그리고 전반적인 가족 친화성을 나타냅니다. 개는 항상 어린 아이들이나 개에 노출이 적은 아이들 주변에서 감독되어야 합니다.',
        'Good With Other Dogs': '다른 개들에 대해 전반적으로 얼마나 친화적인지를 나타냅니다. 개는 항상 다른 개와의 상호작용과 소개에서 감독되어야 하지만, 일부 품종은 본질적으로 집과 외부에서 모두 다른 개들과 더 잘 어울릴 가능성이 높습니다.',
        'Shedding Level': '이 품종이 얼마나 많은 털과 모발을 남길 것으로 예상되는지를 나타냅니다. 털빠짐이 많은 품종은 더 자주 브러싱이 필요하고, 특정 유형의 알레르기를 유발할 가능성이 더 높으며, 더 자주 청소기와 보푸라기 제거가 필요할 수 있습니다.',
        'Coat Grooming Frequency': '품종이 목욕, 브러싱, 손질 또는 기타 종류의 코트 관리가 얼마나 자주 필요한지를 나타냅니다. 이러한 유형의 관리에 얼마나 많은 시간, 인내심 및 예산이 있는지 고려하세요. 모든 품종은 정기적인 발톱 관리가 필요합니다.',
        'Drooling Level': '품종이 얼마나 침을 흘리는 경향이 있는지를 나타냅니다. 깔끔함을 중요시하는 경우, 팔에 침 줄이나 옷에 큰 물자국을 남길 수 있는 개는 적합하지 않을 수 있습니다.',
        'Coat Type': '개의 코트는 품종의 목적에 따라 다양한 유형으로 제공됩니다. 각 코트 유형에는 다른 손질 요구 사항, 알레르기 가능성 및 털빠짐 수준이 있습니다. 가족 반려동물을 선택할 때 특정 코트 유형의 외관이나 감촉을 선호할 수도 있습니다.',
        'Coat Length': '품종의 코트가 얼마나 길 것으로 예상되는지를 나타냅니다. 일부 장모 품종은 짧게 손질할 수 있지만, 이를 유지하려면 추가적인 관리가 필요합니다.',
        'Openness To Strangers': '품종이 낯선 사람들에게 얼마나 개방적인지를 나타냅니다. 일부 품종은 위치에 관계없이 모든 낯선 사람들에게 내성적이거나 조심스러울 수 있는 반면, 다른 품종은 새로운 사람이 주변에 있을 때마다 만나는 것을 즐깁니다!',
        'Playfulness Level': '강아지 시기를 지난 후에도 품종이 놀이에 얼마나 열정적인지를 나타냅니다. 일부 품종은 성인기에도 계속해서 줄다리기나 공 던지기를 원할 것이지만, 다른 품종은 대부분의 시간을 소파에서 당신과 함께 편안하게 쉬는 것을 선호합니다.',
        'Watchdog/Protective Nature': '낯선 사람들이 주변에 있을 때 알려주는 품종의 경향을 나타냅니다. 이러한 품종은 우편배달부나 창문 밖의 다람쥐와 같은 잠재적 위협에 더 많이 반응할 가능성이 있습니다. 이 품종들은 집에 들어오는 낯선 사람들이 가족에게 받아들여지면 따뜻하게 대할 가능성이 높습니다.',
        'Adaptability Level': '품종이 변화에 얼마나 쉽게 대처하는지를 나타냅니다. 이는 주거 환경, 소음, 날씨, 일정 및 일상 생활의 기타 변화를 포함할 수 있습니다.',
        'Trainability Level': '개를 훈련시키는 것이 얼마나 쉬울지, 그리고 개가 새로운 것을 배우는 데 얼마나 기꺼이 할 것인지를 나타냅니다. 일부 품종은 단지 주인을 자랑스럽게 만들기를 원하는 반면, 다른 품종은 원하는 것을, 원할 때, 원하는 곳에서 하는 것을 선호합니다!',
        'Energy Level': '품종이 필요로 하는 운동과 정신적 자극의 양을 나타냅니다. 에너지가 높은 품종은 준비되어 있으며 다음 모험을 열심히 기다립니다. 그들은 하루 종일 달리고, 점프하고, 놀며 시간을 보낼 것입니다. 에너지가 낮은 품종은 소파 감자와 같습니다 - 그들은 단순히 주변에 누워서 낮잠을 자는 것에 행복합니다.',
        'Barking Level': '이 품종이 짖음이나 울음소리로 얼마나 자주 소리를 내는지를 나타냅니다. 일부 품종은 모든 지나가는 사람이나 창문 밖의 새에게 짖을 것이지만, 다른 품종은 특정 상황에서만 짖을 것입니다. 일부 짖지 않는 품종도 다른 소리를 사용하여 자신을 표현할 수 있습니다.',
        'Mental Stimulation Needs': '품종이 행복하고 건강하게 지내기 위해 얼마나 많은 정신적 자극이 필요한지를 나타냅니다. 목적으로 길러진 개들은 의사 결정, 문제 해결, 집중력 또는 기타 품질이 필요한 직업을 가질 수 있으며, 필요한 두뇌 운동이 없으면 자신의 마음을 바쁘게 유지하기 위한 프로젝트를 만들 것입니다 - 그리고 그것들은 아마도 당신이 좋아할 종류의 프로젝트가 아닐 것입니다.'
    }
    
    # 빈 번역 칼럼 생성
    if 'trait_ko' not in df.columns:
        df['trait_ko'] = ''
    if 'trait_desc_ko' not in df.columns:
        df['trait_desc_ko'] = ''
    if 'score_low_ko' not in df.columns:
        df['score_low_ko'] = ''
    if 'score_high_ko' not in df.columns:
        df['score_high_ko'] = ''
    
    # 번역을 직접 데이터프레임에 적용 (map 대신 직접 처리)
    for index, row in df.iterrows():
        trait = row['trait']
        
        # trait_ko 적용
        if trait in trait_ko:
            df.at[index, 'trait_ko'] = trait_ko[trait]
            print(f"[{index}] trait_ko 매핑 완료: {trait} -> {trait_ko[trait]}")
        else:
            print(f"[{index}] 경고: '{trait}'에 대한 trait_ko 번역이 없습니다.")
        
        # trait_desc_ko 적용
        if trait in trait_desc_ko:
            df.at[index, 'trait_desc_ko'] = trait_desc_ko[trait]
            print(f"[{index}] trait_desc_ko 매핑 완료: {trait}")
        else:
            print(f"[{index}] 경고: '{trait}'에 대한 trait_desc_ko 번역이 없습니다.")
        
        # score_low_ko와 score_high_ko 적용
        if pd.notna(row['score_low']) and row['score_low'] in score_low_ko:
            df.at[index, 'score_low_ko'] = score_low_ko[row['score_low']]
        elif pd.notna(row['score_low']):
            print(f"[{index}] 경고: '{row['score_low']}'에 대한 score_low_ko 번역이 없습니다.")
            
        if pd.notna(row['score_high']) and row['score_high'] in score_high_ko:
            df.at[index, 'score_high_ko'] = score_high_ko[row['score_high']]
        elif pd.notna(row['score_high']):
            print(f"[{index}] 경고: '{row['score_high']}'에 대한 score_high_ko 번역이 없습니다.")
    
    # 최종 데이터 확인
    print("\n번역 후 데이터 확인:")
    for index, row in df.iterrows():
        print(f"[{index}] {row['trait']} -> {row['trait_ko']} | desc_ko: {'설정됨' if pd.notna(row['trait_desc_ko']) else '없음'}")
    
    # 업데이트된 파일 저장
    df.to_csv(file_path, index=False)
    
    print(f"\n파일 저장 완료: {file_path}")
    print(f"총 {len(df)}개의 특성에 한글 번역 칼럼이 추가되었습니다.")
    return df

if __name__ == "__main__":
    translate_traits() 