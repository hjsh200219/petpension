import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from src.data import Naver
from src.ui import UI
from pathlib import Path
from threading import Thread, Lock
import time
from tqdm import tqdm

def show_update_shelter():
    st.subheader("🏠 보호소 정보 업데이트")
    naver = Naver()
    
    # 세션 상태 초기화
    if 'result' not in st.session_state:
        st.session_state.result = pd.DataFrame()