import streamlit as st

def display_footer():
    """페이지 하단에 푸터를 표시합니다."""
    st.markdown('<div class="footer">© SH Consulting, 2025</div>', unsafe_allow_html=True)

def display_banner():
    """쿠팡 파트너스 배너를 표시합니다."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div class="banner">
                <iframe 
                    src="https://ads-partners.coupang.com/widgets.html?id=843563&template=carousel&trackingCode=AF6451134&subId=" 
                    width="100%" frameborder="0" scrolling="no" referrerpolicy="unsafe-url" browsingtopics>
                </iframe>
            </div>
        """, unsafe_allow_html=True)


def load_css(css_file):
    """외부 CSS 파일 불러오기"""
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True) 
