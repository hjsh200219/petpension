import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st

class Chart:
    """차트 관련 함수를 모아둔 클래스"""
    
    # 공통으로 사용할 색상 세트
    DEFAULT_COLOR_SEQUENCE = px.colors.qualitative.Bold
    
    @staticmethod
    def create_bar_chart(data, pension_col, x='zscore', y='review_item'):
        """표준화 점수 바 차트 생성"""
        fig = px.bar(
            data,
            x=x,
            y=y,
            color=pension_col,
            title='펜션별 리뷰 항목 표준화 점수 비교 (평균=0 기준)',
            labels={
                'zscore': '표준화 점수 (Z-score)', 
                'review_item': '리뷰 항목',
                pension_col: '펜션명'
            },
            orientation='h',
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        
        fig.update_layout(
            xaxis=dict(
                title='표준화 점수 (Z-score)',
                zeroline=True,
                zerolinecolor='black', 
                zerolinewidth=1,
                range=[-2, 2]
            ),
            yaxis=dict(
                title='리뷰 항목',
                categoryorder='total ascending'
            ),
            legend_title_text='펜션명',
            legend={'traceorder': 'normal'},
            height=900,
            margin=dict(l=0, r=0, t=50, b=30)
        )
        
        return fig
    
    @staticmethod
    def create_zscore_bar_chart(data, pension_col):
        """Z-score 막대 차트 생성"""
        fig = px.bar(
            data,
            x='zscore',
            y='review_item',
            color=pension_col,
            title='펜션별 리뷰 항목 표준화 점수 비교 (평균=0 기준)',
            labels={
                'zscore': '표준화 점수 (Z-score)', 
                'review_item': '리뷰 항목',
                pension_col: '펜션명'
            },
            orientation='h',
            barmode='group',
            color_discrete_sequence=Chart.DEFAULT_COLOR_SEQUENCE
        )
        
        fig.update_layout(
            xaxis=dict(
                title='표준화 점수 (Z-score)',
                zeroline=True,
                zerolinecolor='black', 
                zerolinewidth=1,
                range=[-2, 2]
            ),
            yaxis=dict(
                title='리뷰 항목',
                categoryorder='total ascending'
            ),
            legend_title_text='펜션명',
            legend={'traceorder': 'normal'},
            height=900,
            margin=dict(l=0, r=0, t=50, b=30)
        )
        
        return fig
    
    @staticmethod
    def create_heatmap(data, index_col, pension_order, value_col='zscore'):
        """표준화 점수 히트맵 생성"""
        heatmap_data = data.pivot_table(
            values=value_col,
            index=index_col,
            columns='review_item',
            aggfunc='mean'
        ).fillna(0)
        
        # 히트맵 데이터의 인덱스 순서를 명시적으로 지정
        heatmap_data = heatmap_data.reindex(pension_order)
        
        fig = px.imshow(
            heatmap_data,
            title='펜션별 리뷰 항목 표준화 점수 히트맵 (평균=0 기준)',
            labels=dict(
                x="리뷰 항목",
                y="펜션명",
                color="표준화 점수 (Z-score)"
            ),
            color_continuous_scale='RdBu_r',
            zmin=-2,
            zmax=2
        )
        
        fig.update_layout(
            yaxis_title='펜션명',
            xaxis_title='리뷰 항목',
            coloraxis_colorbar=dict(
                title="표준화 점수<br>(Z-score)"
            ),
            height=900,
            margin=dict(l=0, r=0, t=50, b=30)
        )
        
        return fig
    
    @staticmethod
    def create_zscore_heatmap(data, pension_col, category_order):
        """Z-score 히트맵 생성"""
        # 히트맵 데이터
        heatmap_data = data.pivot_table(
            values='zscore',
            index=pension_col,
            columns='review_item',
            aggfunc='mean'
        ).fillna(0)
        
        # 히트맵 데이터의 인덱스 순서를 명시적으로 지정
        heatmap_data = heatmap_data.reindex(category_order)
        
        fig = px.imshow(
            heatmap_data,
            title='펜션별 리뷰 항목 표준화 점수 히트맵 (평균=0 기준)',
            labels=dict(
                x="리뷰 항목",
                y="펜션명",
                color="표준화 점수 (Z-score)"
            ),
            color_continuous_scale='RdBu_r',
            zmin=-2,
            zmax=2
        )
        
        fig.update_layout(
            yaxis_title='펜션명',
            xaxis_title='리뷰 항목',
            coloraxis_colorbar=dict(
                title="표준화 점수<br>(Z-score)"
            ),
            height=900,
            margin=dict(l=0, r=0, t=50, b=30)
        )
        
        return fig
    
    @staticmethod
    def create_line_chart(data, x, y, color=None, title='', labels=None, markers=True):
        """선 차트 생성"""
        fig = px.line(
            data,
            x=x,
            y=y,
            color=color,
            title=title,
            labels=labels or {},
            markers=markers,
            color_discrete_sequence=Chart.DEFAULT_COLOR_SEQUENCE
        )
        
        fig.update_layout(
            xaxis_title=labels.get(x, x) if labels else x,
            yaxis_title=labels.get(y, y) if labels else y,
            yaxis=dict(tickformat=',d', range=[0, None]),
            legend={'traceorder': 'normal'}
        )
        
        return fig
    
    @staticmethod
    def create_price_comparison_charts(selected_data, category_avg_price, category_order):
        """가격 비교 차트 세트 생성"""
        # 1. 평균 가격 막대 차트
        avg_price_fig = px.bar(
            category_avg_price,
            x='펜션/상품',
            y='평균 가격',
            color='펜션/상품',
            title='펜션/상품별 평균 가격 비교',
            text_auto=True,
            category_orders={'펜션/상품': category_order},
            color_discrete_sequence=Chart.DEFAULT_COLOR_SEQUENCE
        )
        
        avg_price_fig.update_layout(
            xaxis_title='펜션/상품',
            yaxis_title='평균 가격 (원)',
            yaxis=dict(tickformat=',d', range=[0, None])
        )
        
        # 2. 가격 범위 상자 그림
        # 카테고리 순서를 위한 매핑 생성
        category_order_map = {cat: i for i, cat in enumerate(category_order)}
        
        # 정렬을 위한 임시 열 추가
        selected_data_sorted = selected_data.copy()
        selected_data_sorted['카테고리_순서'] = selected_data_sorted['카테고리'].map(
            lambda x: category_order_map.get(x, len(category_order))
        )
        
        # 카테고리 순서로 데이터 정렬
        selected_data_sorted = selected_data_sorted.sort_values('카테고리_순서')
        
        box_fig = px.box(
            selected_data_sorted,
            x='카테고리',
            y='가격',
            color='카테고리',
            title='펜션/상품별 가격 분포',
            category_orders={'카테고리': category_order},
            color_discrete_sequence=Chart.DEFAULT_COLOR_SEQUENCE
        )
        
        box_fig.update_layout(
            xaxis_title='펜션/상품',
            yaxis_title='가격 (원)',
            yaxis=dict(tickformat=',d', range=[0, None])
        )
        
        # 3. 날짜별 평균 가격 차트
        date_avg_price = selected_data.groupby(['날짜', '카테고리'])['가격'].mean().reset_index()
        
        daily_price_fig = px.line(
            date_avg_price,
            x='날짜',
            y='가격',
            color='카테고리',
            title='날짜별 펜션/상품 평균 가격 추이',
            markers=True,
            category_orders={'카테고리': category_order},
            color_discrete_sequence=Chart.DEFAULT_COLOR_SEQUENCE
        )
        
        daily_price_fig.update_layout(
            xaxis_title='날짜',
            yaxis_title='평균 가격 (원)',
            yaxis=dict(tickformat=',d', range=[0, None]),
            legend={'traceorder': 'normal'}
        )
        
        # 4. 요일별 가격 차트
        # 요일 추가
        selected_data['요일'] = selected_data['날짜'].dt.day_name()
        
        # 요일 순서 정렬
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # 한글 요일로 변환
        day_korean = {
            'Monday': '월요일',
            'Tuesday': '화요일',
            'Wednesday': '수요일',
            'Thursday': '목요일',
            'Friday': '금요일',
            'Saturday': '토요일',
            'Sunday': '일요일'
        }
        
        selected_data['요일_한글'] = selected_data['요일'].map(day_korean)
        
        # 요일별 평균 가격 계산
        day_avg_price = selected_data.groupby(['요일_한글', '카테고리'])['가격'].mean().reset_index()
        
        # 요일 순서 맞추기
        day_order_korean = [day_korean[day] for day in days_order]
        day_avg_price['요일_순서'] = day_avg_price['요일_한글'].map(lambda x: day_order_korean.index(x))
        day_avg_price = day_avg_price.sort_values('요일_순서')
        
        weekday_price_fig = px.line(
            day_avg_price,
            x='요일_한글',
            y='가격',
            color='카테고리',
            title='요일별 펜션/상품 평균 가격',
            markers=True,
            category_orders={'카테고리': category_order},
            color_discrete_sequence=Chart.DEFAULT_COLOR_SEQUENCE
        )
        
        weekday_price_fig.update_layout(
            xaxis={'categoryorder': 'array', 'categoryarray': day_order_korean},
            yaxis_title='평균 가격 (원)',
            yaxis=dict(tickformat=',d', range=[0, None]),
            legend={'traceorder': 'normal'}
        )
        
        return {
            'avg_price': avg_price_fig,
            'box': box_fig,
            'daily_price': daily_price_fig,
            'weekday_price': weekday_price_fig
        }
    
    @staticmethod
    def create_radar_tabs(rating_average, pension_col, pension_names):
        """펜션별 레이더 차트 탭 생성
        
        항상 카페이안과 선택된 다른 펜션 비교 탭만 생성
        """
        # 문자열 변환 보장
        pension_names = [str(name) for name in pension_names]
        
        # 카페이안 펜션 이름 찾기 - '카페이안' 또는 '카페 이안' 모두 검색
        cafeian_pensions = [name for name in pension_names if '카페이안' in name or '카페 이안' in name]
        cafeian_pension = cafeian_pensions[0] if cafeian_pensions else None
        
        # 카페이안이 있는 경우, 다른 펜션과 비교 탭 생성
        if cafeian_pension:
            # 카페이안을 제외한 다른 펜션들
            other_pensions = [name for name in pension_names if name != cafeian_pension]
            
            if other_pensions:
                # 비교 탭 생성 (다른 펜션들의 이름 사용)
                tab_labels = [f"vs {other}" for other in other_pensions]
                tabs = st.tabs(tab_labels)
                
                for i, other_pension in enumerate(other_pensions):
                    with tabs[i]:
                        # 두 펜션 데이터 비교 차트 생성
                        Chart.create_comparison_radar_chart(
                            rating_average, 
                            pension_col, 
                            cafeian_pension, 
                            other_pension
                        )
            else:
                # 다른 펜션이 없는 경우 메시지 표시
                st.warning("비교할 다른 펜션을 선택해주세요.")
        else:
            # 카페이안이 없는 경우 선택된 펜션끼리 비교
            if len(pension_names) >= 2:
                # 첫 번째 펜션을 기준으로 나머지 펜션과 비교
                base_pension = pension_names[0]
                compare_pensions = pension_names[1:]
                
                # 비교 탭 생성
                tab_labels = [f"{base_pension} vs {other}" for other in compare_pensions]
                tabs = st.tabs(tab_labels)
                
                for i, other_pension in enumerate(compare_pensions):
                    with tabs[i]:
                        # 두 펜션 데이터 비교 차트 생성
                        Chart.create_comparison_radar_chart(
                            rating_average, 
                            pension_col, 
                            base_pension, 
                            other_pension
                        )
            elif len(pension_names) == 1:
                # 펜션이 하나만 있는 경우
                st.info(f"{pension_names[0]} 펜션의 리뷰 데이터만 있어 비교할 수 없습니다.")
                Chart.create_radar_chart(rating_average, pension_col, pension_names[0])
            else:
                st.warning("분석할 펜션 데이터가 없습니다. 펜션을 선택하고 분석을 시작해주세요.")

    @staticmethod
    def create_comparison_radar_chart(data, pension_col, pension1, pension2):
        """두 펜션 비교 레이더 차트 생성"""
        # 두 펜션의 데이터 추출
        pension1_data = data[data[pension_col] == pension1].copy()
        pension2_data = data[data[pension_col] == pension2].copy()
        
        if pension1_data.empty or pension2_data.empty:
            st.warning(f"하나 이상의 펜션 데이터가 없습니다: {pension1 if pension1_data.empty else pension2}")
            return
        
        # 모든 리뷰 항목 수집 및 정렬
        all_items = sorted(data['review_item'].unique())
        
        # 각 펜션별 Z-score 값 준비 (모든 항목 포함)
        pension1_values = []
        pension2_values = []
        
        for item in all_items:
            # 첫 번째 펜션 데이터
            p1_item_data = pension1_data[pension1_data['review_item'] == item]
            p1_value = p1_item_data['zscore'].values[0] if not p1_item_data.empty else 0
            pension1_values.append(p1_value)
            
            # 두 번째 펜션 데이터
            p2_item_data = pension2_data[pension2_data['review_item'] == item]
            p2_value = p2_item_data['zscore'].values[0] if not p2_item_data.empty else 0
            pension2_values.append(p2_value)
        
        # 데이터 준비 - 폐곡선을 위해 첫 번째 값을 마지막에 추가
        closed_items = all_items + [all_items[0]]
        closed_pension1_values = pension1_values + [pension1_values[0]]
        closed_pension2_values = pension2_values + [pension2_values[0]]
        
        # 데이터 준비
        fig = go.Figure()
        
        # 첫 번째 펜션 (카페이안) 데이터 추가
        fig.add_trace(go.Scatterpolar(
            r=closed_pension1_values,
            theta=closed_items,
            fill='toself',
            name=pension1,
            line_color=Chart.DEFAULT_COLOR_SEQUENCE[0]
        ))
        
        # 두 번째 펜션 데이터 추가
        fig.add_trace(go.Scatterpolar(
            r=closed_pension2_values,
            theta=closed_items,
            # fill='toself',
            name=pension2,
            line_color=Chart.DEFAULT_COLOR_SEQUENCE[1]
        ))
        
        # 0점 참조선 추가
        fig.add_trace(
            go.Scatterpolar(
                r=[0] * len(closed_items),
                theta=closed_items,
                mode='lines',
                line=dict(color='gray', width=1, dash='dash'),
                fill='none',
                name='평균 (0점)'
            )
        )
        
        # 레이아웃 설정
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[-3, 3],
                    showline=True,
                    linecolor='gray'
                ),
                angularaxis=dict(
                    showline=True,
                    linecolor='gray'
                )
            ),
            title=f'{pension1} vs {pension2} 리뷰 항목 비교',
            height=700,
            margin=dict(l=30, r=30, t=50, b=30)
        )
        
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def create_radar_chart(data, pension_col, pension_name, color_index=0):
        """레이더 차트 생성"""
        pension_data = data[data[pension_col] == pension_name].copy()
        
        if pension_data.empty:
            st.warning(f"펜션 데이터가 없습니다: {pension_name}")
            return
        
        # 모든 리뷰 항목 수집 및 정렬
        all_items = sorted(data['review_item'].unique())
        
        # 펜션의 Z-score 값 준비 (모든 항목 포함)
        pension_values = []
        
        for item in all_items:
            item_data = pension_data[pension_data['review_item'] == item]
            item_value = item_data['zscore'].values[0] if not item_data.empty else 0
            pension_values.append(item_value)
        
        # 폐곡선을 위해 첫 번째 값을 마지막에 추가
        closed_items = all_items + [all_items[0]]
        closed_pension_values = pension_values + [pension_values[0]]
        
        # 데이터 준비
        fig = go.Figure()
        
        # 펜션 데이터 추가
        fig.add_trace(go.Scatterpolar(
            r=closed_pension_values,
            theta=closed_items,
            fill='toself',
            name=pension_name,
            line_color=Chart.DEFAULT_COLOR_SEQUENCE[color_index % len(Chart.DEFAULT_COLOR_SEQUENCE)]
        ))
        
        # 0점 참조선 추가
        fig.add_trace(
            go.Scatterpolar(
                r=[0] * len(closed_items),
                theta=closed_items,
                mode='lines',
                line=dict(color='gray', width=1, dash='dash'),
                fill='none',
                name='평균 (0점)'
            )
        )
        
        # 레이아웃 설정
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[-3, 3],
                    showline=True,
                    linecolor='gray'
                ),
                angularaxis=dict(
                    showline=True,
                    linecolor='gray'
                )
            ),
            title=f'{pension_name} 리뷰 항목 표준화 점수 (평균=0 기준)',
            height=700,
            margin=dict(l=30, r=30, t=50, b=30)
        )
        
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def create_single_radar_chart(rating_average, pension_col, pension_name, color_index):
        """개별 펜션 레이더 차트 생성 (더 이상 사용하지 않음)"""
        pension_data = rating_average[rating_average[pension_col] == pension_name].copy()
        
        fig = px.line_polar(
            pension_data, 
            r='zscore', 
            theta='review_item', 
            line_close=True,
            title=f'{pension_name} 리뷰 항목 표준화 점수 (평균=0 기준)',
            labels={'zscore': '표준화 점수 (Z-score)', 'review_item': '리뷰 항목'},
            color_discrete_sequence=[px.colors.qualitative.Bold[color_index % len(px.colors.qualitative.Bold)]]
        )
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[-3, 3],
                    showline=True,
                    linecolor='gray'
                ),
                angularaxis=dict(
                    showline=True,
                    linecolor='gray'
                )
            ),
            showlegend=False,
            height=700,
            margin=dict(l=30, r=30, t=50, b=30)
        )
        
        # 0점 참조선 추가
        items = pension_data['review_item'].unique()
        fig.add_trace(
            go.Scatterpolar(
                r=[0] * len(items),
                theta=items,
                mode='lines',
                line=dict(color='gray', width=1, dash='dash'),
                fill='none',
                name='평균 (0점)'
            )
        )
        
        # 차트 및 데이터 표시
        st.plotly_chart(fig, use_container_width=True)
        
        # 상세 데이터 표시
        st.markdown(f"#### {pension_name} 리뷰 항목 점수")
        display_cols = ['review_item', 'rating', 'rating_relative_pct', 'zscore']
        st.dataframe(
            pension_data[display_cols].sort_values('zscore', ascending=False),
            use_container_width=True,
            hide_index=True
        ) 