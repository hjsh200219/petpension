import streamlit as st
from src.data import Public, Common
from src.ui import UI, BreedInfo
from src.survey import Survey
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.graph_objects as go
import pydeck as pdk
import pandas as pd
import ast
import numpy as np

# def calculate_breed_match(user_answers, breed_info):
#     """사용자 답변과 견종 정보를 비교하여 매칭 점수를 계산합니다."""
#     scores = {}
    
#     for _, breed in breed_info.iterrows():
#         score, total_weight = calculate_scores(user_answers, breed)
#         final_score = (score / total_weight) * 100 if total_weight > 0 else 0
#         scores[breed['breed_name_kor']] = final_score
    
#     return scores

# def calculate_scores(user_answers, breed):
#     score = 0
#     total_weight = 0

#     criteria = {
#         "당신의 개가 얼마나 훈련되기를 원하십니까?": (2, 'Trainability Level', [4, 3, 2]),
#         "당신은 개가 얼마나 활동적이기를 원하십니까?": (2, 'Energy Level', [4, 3, 2]),
#         "얼마나 많은 털 빠짐을 감당할 수 있습니까?": (1.5, 'Shedding Level', [3, 2, 2], True),
#         "개 미용 관리를 얼마나 자주 해줄 수 있습니까?": (1.5, 'Coat Grooming Frequency', [4, 3, 2]),
#         "얼마나 많은 짖음이나 다른 소리에 괜찮으십니까?": (1, 'Barking Level', [4, 3, 2]),
#         "원하는 개의 크기는 무엇입니까?": (1.5, 'weight', None, False, True),
#         "가정에 어린이가 있습니까?": (2, 'Good With Young Children', [4]),
#         "가정에 다른 동물이 있습니까?": (1.5, 'Good With Other Dogs', [4]),
#         "저알레르기 개를 원하십니까?": (2, 'Shedding Level', [2], True)
#     }

#     for question, (weight, trait, levels, *optional) in criteria.items():
#         is_shedding = optional[0] if len(optional) > 0 else False
#         is_size = optional[1] if len(optional) > 1 else False
        
#         if question in user_answers:
#             answer = user_answers[question]
#             score, total_weight = update_score_and_weight(
#                 score, total_weight, weight, breed, trait, answer, levels, is_shedding, is_size
#             )

#     return score, total_weight

# def update_score_and_weight(score, total_weight, weight, breed, trait, answer, levels, is_shedding, is_size):
#     if is_size:
#         size_score = get_size_score(answer)
#         breed_size = get_breed_size(breed)
#         if abs(size_score - breed_size) <= 1:
#             score += weight
#     else:
#         if is_shedding:
#             if answer == "많은 털 빠짐도 괜찮음" and breed[trait] >= levels[0]:
#                 score += weight
#             elif answer == "보통 정도의 털 빠짐은 괜찮음" and breed[trait] >= levels[1]:
#                 score += weight
#             elif answer == "가끔씩만 털 빠짐을 원함" and breed[trait] <= levels[2]:
#                 score += weight
#         else:
#             for i, level in enumerate(levels):
#                 if answer == get_answer_string(i) and breed[trait] >= level:
#                     score += weight
#                     break

#     total_weight += weight
#     return score, total_weight

# def get_size_score(answer):
#     size_mapping = {
#         "초대형": 5,
#         "대형": 4,
#         "중형": 3,
#         "소형": 2,
#         "초소형": 1
#     }
#     return size_mapping.get(answer, 0)

# def get_breed_size(breed):
#     try:
#         weight_str = breed['weight']
#         if isinstance(weight_str, str):
#             weight_list = ast.literal_eval(weight_str)
#             max_weight = max([float(w.split()[0].replace("'", "")) for w in weight_list])
#             if max_weight > 100:
#                 return 5
#             elif max_weight > 50:
#                 return 4
#             elif max_weight > 25:
#                 return 3
#             elif max_weight > 10:
#                 return 2
#             else:
#                 return 1
#     except:
#         pass
#     return 0

# def get_answer_string(index):
#     answer_strings = [
#         "매우 훈련하기 쉬움",
#         "훈련하기 쉬움",
#         "훈련 가능",
#         "매우 높은 에너지 (하루 60~120분 운동)",
#         "활발함 (하루 60~90분 운동)",
#         "적당한 에너지 (하루 30~60분 운동)",
#         "많은 털 빠짐도 괜찮음",
#         "보통 정도의 털 빠짐은 괜찮음",
#         "가끔씩만 털 빠짐을 원함",
#         "매일",
#         "주 2~3회",
#         "매주",
#         "매우 시끄러움",
#         "자주 짖음",
#         "가끔 짖음"
#     ]
#     return answer_strings[index]

# def show_breed_results(matched_breeds, breed_info):
#     """매칭된 견종 결과를 표시합니다."""
#     st.subheader("🏆 추천 품종")
#     upkind = '417000'
    
#     for i, (breed, score) in enumerate(matched_breeds[:5], 1):
#         breed_data = breed_info[breed_info['breed_name_kor'] == breed].iloc[0]
#         kindCd = breed_data.get('breed_name_kor', '')

#         if i == 1:
#             BreedInfo().show_breed_info(kindCd, expandedoption=True, matching_score=score)
#             BreedInfo().match_breed(upkind, kindCd)
#         else:
#             BreedInfo().show_breed_info(kindCd, expandedoption=False, matching_score=score)
#             BreedInfo().match_breed(upkind, kindCd)

# def show_progress_bar(current_step, total_steps):
#     """진행 상황을 보여주는 프로그레스 바를 표시합니다."""
#     progress = current_step / total_steps
#     st.progress(progress)
#     st.write(f"진행 상황: {current_step}/{total_steps} 단계")

# def handle_survey_navigation(survey_data, current_step):   
#     row = survey_data.iloc[current_step]
#     question = row['question_k']
#     options = ast.literal_eval(row['select_option_k']) if pd.notna(row['select_option_k']) else []
#     description = row['description_k'] if pd.notna(row['description_k']) else ""
    
#     st.subheader(question)
#     if description:
#         st.write(description)
#     else:
#         st.write("")
    
#     if options and isinstance(options, list):
#         answer = st.radio(
#             "답변을 선택해주세요",
#             options,
#             key=f"survey_{current_step}",
#             index=None,
#             label_visibility="collapsed"
#         )
        
#         if answer:
#             st.session_state.user_answers[question] = answer
#             handle_conditional_questions(row, answer)
#             if not (pd.notna(row['if_question_k']) and pd.notna(row['if_option_k'])):
#                 st.session_state.current_step += 1
#                 st.rerun()
    
#     col1, col2 = st.columns([1, 5])
#     with col1:
#         if current_step > 0:
#             if st.button(
#                 "이전",
#                 type="secondary",
#                 key=f"prev_button_{current_step}",
#                 use_container_width=True
#             ):
#                 reset_answers(survey_data, current_step)
#                 st.session_state.current_step -= 1
#                 st.rerun()

# def reset_answers(survey_data, current_step):
#     current_question = survey_data.iloc[current_step]['question_k']
#     if current_question in st.session_state.user_answers:
#         del st.session_state.user_answers[current_question]
    
#     current_row = survey_data.iloc[current_step]
#     if pd.notna(current_row['if_question_k']):
#         if current_row['if_question_k'] in st.session_state.user_answers:
#             del st.session_state.user_answers[current_row['if_question_k']]
    
#     prev_question = survey_data.iloc[current_step - 1]['question_k']
#     if prev_question in st.session_state.user_answers:
#         del st.session_state.user_answers[prev_question]

# def handle_conditional_questions(row, answer):
#     if pd.notna(row['if_question_k']) and pd.notna(row['if_option_k']):
#         if answer == "예":
#             try:
#                 if_options = ast.literal_eval(row['if_option_k'])
#                 if isinstance(if_options, list) and if_options:
#                     if row['question_k'] in ["가정에 다른 동물이 있습니까?", "집에서 키우는 다른 동물이 있습니까?"]:
#                         st.write(row['if_question_k'])
#                         selected_animals = []
#                         for option in if_options:
#                             if st.checkbox(
#                                 option,
#                                 key=f"survey_if_{row['question_k']}_{option}",
#                                 value=option in st.session_state.user_answers.get(row['if_question_k'], [])
#                             ):
#                                 selected_animals.append(option)
                        
#                         if selected_animals:
#                             st.session_state.user_answers[row['if_question_k']] = selected_animals
#                             col1, col2 = st.columns([1, 5])
#                             with col1:
#                                 if st.button(
#                                     "다음",
#                                     type="primary",
#                                     key=f"next_button_animals_{id(row)}",
#                                     use_container_width=True
#                                 ):
#                                     st.session_state.current_step += 1
#                                     st.rerun()
#                     else:
#                         if_answer = st.radio(
#                             row['if_question_k'],
#                             if_options,
#                             key=f"survey_if_{row['question_k']}",
#                             index=None
#                         )
#                         if if_answer:
#                             st.session_state.user_answers[row['if_question_k']] = if_answer
#                             st.session_state.current_step += 1
#                             st.rerun()
#             except (ValueError, SyntaxError) as e:
#                 st.error(f"조건부 질문 '{row['if_question_k']}'의 옵션을 처리하는 중 오류가 발생했습니다: {str(e)}")
        
#         elif answer == "아니오" and row['question_k'] in ["가정에 어린이가 있습니까?", "집에 자녀가 있습니까?", 
#                                                        "가정에 다른 동물이 있습니까?", "집에서 키우는 다른 동물이 있습니까?"]:
#             st.session_state.current_step += 1
#             st.rerun()

# def handle_survey_completion(breed_info, akcTraits):
#     st.success("모든 질문이 완료되었습니다!")


#     col1, col2, col3 = st.columns([1, 1, 4])
#     with col1:
#         if st.button(
#             "결과 보기",
#             type="primary",
#             use_container_width=True
#         ):
#             if len(st.session_state.user_answers) < 5:
#                 st.warning("더 많은 질문에 답해주세요!")
#                 return
            
#     with col2:
#         if st.button(
#             "처음부터 다시 시작",
#             type="secondary",
#             use_container_width=True
#         ):
#             st.session_state.user_answers = {}
#             st.session_state.current_step = 0
#             st.rerun()
            
#     scores = calculate_breed_match(st.session_state.user_answers, breed_info)
#     matched_breeds = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
#     show_breed_results(matched_breeds, breed_info)

# def show_intro_page():
#     UI().load_css()
#     st.image("static/images/survey_intro.png", use_container_width=True)
#     st.markdown("<p class='txt-center'>이 설문을 통해 당신의 생활 방식과 선호도에 맞는 반려견 품종을 찾아보세요.</p>", unsafe_allow_html=True)
    
#     st.markdown("<p class='txt-center'>설문에 응답하면 당신의 라이프스타일과 가장 잘 맞는 강아지 품종을 추천해 드립니다.</p>", unsafe_allow_html=True)

#     col1, col2, col3 = st.columns([1, 1, 1])
#     with col2:
#         if st.button(
#             "설문 시작",
#             type="primary",
#             use_container_width=True
#             ):
#             st.session_state.show_intro = False
#             st.rerun()

def survey_page(survey_data, breed_info, akcTraits):
    total_steps = len(survey_data)
    current_step = st.session_state.current_step

    Survey().show_progress_bar(current_step, total_steps)
    
    if current_step < total_steps:
        Survey().handle_survey_navigation(survey_data, current_step)
    else:
        Survey().handle_survey_completion(breed_info, akcTraits)

def show_survey_page():
    """메인 페이지를 표시하는 함수"""
    # CSS 및 PWA 컴포넌트 로드
    ui = UI()
    ui.load_css()
    ui.load_pwa_components()
    
    st.subheader("🔍 나의 반려동물 찾기")
    
    # 세션 상태 초기화
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'show_intro' not in st.session_state:
        st.session_state.show_intro = True
    if 'animal_type' not in st.session_state:
        st.session_state.animal_type = "강아지"
    
    # 데이터 로드
    survey_data = pd.read_csv('./static/database/survey.csv')
    breed_info = pd.read_csv('./static/database/akcBreedInfo.csv')
    akcTraits = pd.read_csv('./static/database/akcTraits.csv')
    
    # 인트로 화면과 설문 화면 분기
    if st.session_state.show_intro:
        Survey().show_intro_page()
    else:
        # 동물 유형 선택 탭
        animal_type = st.radio(
            "반려동물 유형 선택",
            ["강아지", "고양이", "기타"],
            horizontal=True,
            index=0 if st.session_state.animal_type == "강아지" else 
                  1 if st.session_state.animal_type == "고양이" else 2,
            key="animal_type_selector"
        )
        
        st.session_state.animal_type = animal_type
        
        if animal_type == "강아지":
            survey_page(survey_data, breed_info, akcTraits)
        elif animal_type == "고양이":
            st.warning("고양이 설문은 준비중입니다.")
        else:
            st.warning("기타 동물 설문은 준비중입니다.")
