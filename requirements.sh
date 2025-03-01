#!/bin/bash

# 스크립트 실행 오류 발생시 즉시 중단
set -e

echo "PetPension 프로젝트 환경 설정을 시작합니다..."

# 파이썬 버전 확인
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "파이썬 버전: $python_version"

# 가상환경 생성 및 활성화
if [ ! -d "venv" ]; then
    echo "가상환경을 생성합니다..."
    python3 -m venv venv
    echo "가상환경이 생성되었습니다."
else
    echo "이미 가상환경이 존재합니다."
fi

echo "가상환경을 활성화합니다..."
source venv/bin/activate

# pip 업그레이드
echo "pip를 최신 버전으로 업데이트합니다..."
pip install --upgrade pip

# 의존성 패키지 설치
echo "필요한 패키지를 설치합니다..."
pip install -r requirements.txt

echo "환경 설정이 완료되었습니다!"
echo "가상환경을 활성화하려면 다음 명령어를 실행하세요: source venv/bin/activate"
echo "애플리케이션을 실행하려면 다음 명령어를 실행하세요: python app.py"

# 스크립트 실행 권한 부여 안내
echo "참고: 이 스크립트를 실행하려면 먼저 다음 명령어로 실행 권한을 부여해야 할 수 있습니다: chmod +x requirements.sh" 