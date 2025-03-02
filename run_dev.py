#!/usr/bin/env python3
"""
개발 모드로 Streamlit을 실행하는 스크립트
이 스크립트는 파일 변경 시 자동으로 앱을 새로고침합니다.
"""

import os
import streamlit.web.cli as stcli
import sys

if __name__ == "__main__":
    # 개발 모드 플래그 설정
    os.environ["STREAMLIT_DEVELOPMENT"] = "true"
    
    # Streamlit 캐시 정책 설정 환경 변수 
    os.environ["STREAMLIT_SERVER_RUN_ON_SAVE"] = "true"
    os.environ["STREAMLIT_SERVER_MAX_UPLOAD_SIZE"] = "10"
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    os.environ["STREAMLIT_SERVER_WATCH_FOR_CHANGES"] = "true"  # 파일 변경 감지 활성화
    
    # 추가 명령행 인수 설정
    sys.argv = ["streamlit", "run", "app.py", 
                "--server.runOnSave=true",
                "--server.maxUploadSize=10",
                "--client.showErrorDetails=true",
                "--server.fileWatcherType=auto",  # 파일 감시 방식 설정
                "--server.watchForChanges=true"]  # 변경 감지 활성화
    
    print("🚀 개발 모드에서 Streamlit 실행 중...")
    print("📝 파일 변경 시 자동으로 새로고침됩니다.")
    
    # Streamlit 실행
    sys.exit(stcli.main()) 