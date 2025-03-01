import streamlit as st
from pathlib import Path
import datetime

def load_css(css_file):
    """CSS 파일을 로드하는 함수"""
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def display_banner():
    """페이지 상단에 배너를 표시하는 함수"""
    st.markdown(
        """
         <div class="banner">
                <iframe 
                    src="https://ads-partners.coupang.com/widgets.html?id=842740&template=carousel&trackingCode=AF6451134&subId=&width=680&height=140&tsource=" 
                    frameborder="0" 
                    scrolling="no" 
                    referrerpolicy="unsafe-url" 
                    browsingtopics>
                </iframe>
            </div>
        """,
        unsafe_allow_html=True
    )

def display_footer():
    """페이지 하단에 푸터를 표시하는 함수"""
    current_year = datetime.datetime.now().year
    st.markdown(
        f"""
        <div class="footer">
            <p>© {current_year} SH Consulting. All rights reserved.</p>
        </div>
        """,
        unsafe_allow_html=True
    ) 