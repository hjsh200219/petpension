import os
import hashlib
from dotenv import load_dotenv

# .env 파일 로드 (존재하는 경우)
load_dotenv()

DEFAULT_PASSWORD_HASH = "97f41176b020df3c9da7a55c1d725fd2f84e639e40c94283253d9fbfb807dd93"

# 환경 변수에서 비밀번호 해시 가져오기, 없으면 기본값 사용
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", DEFAULT_PASSWORD_HASH)

def verify_password(password):
    """
    입력된 비밀번호가 저장된 해시와 일치하는지 확인합니다.
    """
    # 입력된 비밀번호의 SHA-256 해시 계산
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # 저장된 해시와 비교
    return password_hash == ADMIN_PASSWORD_HASH

def set_password(password):
    """
    새 비밀번호 설정 (환경 변수 설정을 위한 도우미 함수)
    주의: 이 함수는 개발 환경에서만 사용해야 함
    """
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash 