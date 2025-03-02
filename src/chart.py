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
    def create_radar_chart(data, pension_col, pension_name, color_index=0):
        """레이더 차트 생성"""
        pension_data = data[data[pension_col] == pension_name].copy()
        
        fig = px.line_polar(
            pension_data, 
            r='zscore', 
            theta='review_item', 
            line_close=True,
            title=f'{pension_name} 리뷰 항목 표준화 점수 (평균=0 기준)',
            labels={'zscore': '표준화 점수 (Z-score)', 'review_item': '리뷰 항목'},
            color_discrete_sequence=[Chart.DEFAULT_COLOR_SEQUENCE[color_index % len(Chart.DEFAULT_COLOR_SEQUENCE)]]
        )
        
        # 레이아웃 설정
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[-2, 2],
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
        
        return fig
    
    @staticmethod
    def create_combined_radar_chart(data, pension_col, pension_names):
        """모든 펜션을 포함하는 단일 레이더 차트 생성"""
        fig = go.Figure()
        
        # 모든 리뷰 항목을 가져옴
        all_review_items = data['review_item'].unique()
        
        # 각 펜션에 대한 트레이스 추가
        for i, pension_name in enumerate(pension_names):
            pension_data = data[data[pension_col] == pension_name].copy()
            
            # 펜션별 Z-score 값 추출
            z_scores = {}
            for _, row in pension_data.iterrows():
                z_scores[row['review_item']] = row['zscore']
            
            # 모든 리뷰 항목에 대해 z-score 값 설정 (없는 항목은 0으로)
            r_values = [z_scores.get(item, 0) for item in all_review_items]
            
            # 트레이스 추가
            fig.add_trace(go.Scatterpolar(
                r=r_values,
                theta=all_review_items,
                fill='toself',
                name=pension_name,
                line_color=Chart.DEFAULT_COLOR_SEQUENCE[i % len(Chart.DEFAULT_COLOR_SEQUENCE)]
            ))
        
        # 0점 참조선 추가
        fig.add_trace(
            go.Scatterpolar(
                r=[0] * len(all_review_items),
                theta=all_review_items,
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
                    range=[-2, 2],
                    showline=True,
                    linecolor='gray'
                )
            ),
            title="펜션별 리뷰 항목 표준화 점수 비교 (평균=0 기준)",
            height=700,
            margin=dict(l=30, r=30, t=50, b=30)
        )
        
        return fig

    @staticmethod
    def create_radar_tabs(rating_average, pension_col, pension_names):
        """펜션별 레이더 차트 탭 생성"""
        # 문자열 변환 보장
        pension_names = [str(name) for name in pension_names]
        
        # 탭 생성
        tabs = st.tabs(pension_names)
        
        for i, pension_name in enumerate(pension_names):
            with tabs[i]:
                Chart.create_single_radar_chart(rating_average, pension_col, pension_name, i)

    @staticmethod
    def create_single_radar_chart(rating_average, pension_col, pension_name, color_index):
        """개별 펜션 레이더 차트 생성"""
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
        
        # 레이아웃 설정
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[-2, 2],
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