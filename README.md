# 🐾 Pet Companion

반려동물과 함께하는 일상을 더욱 특별하게 만들어주는 웹 애플리케이션입니다.

## 주요 기능

- 반려동물 프로필 관리
- 건강 기록 추적
- 병원 예약 일정 관리
- 산책 및 활동 기록

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/yourusername/PetCompanion.git
cd PetCompanion
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
.\venv\Scripts\activate  # Windows
```

3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

4. 환경 설정
```bash
# .env.example 파일을 .env로 복사
cp .env.example .env

# 필요에 따라 .env 파일을 수정
# 관리자 비밀번호를 변경하려면:
python -c "from src.settings import set_password; set_password('새_비밀번호')"
# 이 명령은 새 비밀번호의 해시값을 출력합니다. 이 값을 .env 파일의 ADMIN_PASSWORD_HASH에 설정하세요.
```

5. 애플리케이션 실행
```bash
# 일반 실행
streamlit run app.py

# 개발 모드 실행 (자동 새로고침)
python run_dev.py
```

## 기술 스택

- Python
- Streamlit
- Pandas
- Pillow 