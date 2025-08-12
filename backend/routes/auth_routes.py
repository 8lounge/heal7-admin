"""
인증 시스템 API 라우터
HEAL7 사용자 인증 (이메일 기반)
"""

import re
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import jwt
from datetime import datetime, timedelta
import secrets

logger = logging.getLogger(__name__)

# Pydantic 모델 정의
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('비밀번호는 8자 이상이어야 합니다')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('비밀번호에는 영문자가 포함되어야 합니다')
        if not re.search(r'\d', v):
            raise ValueError('비밀번호에는 숫자가 포함되어야 합니다')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^01[0-9]-\d{4}-\d{4}$', v):
            raise ValueError('올바른 휴대폰 번호 형식을 입력해주세요 (예: 010-1234-5678)')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    is_active: bool
    email_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# JWT 설정
SECRET_KEY = "heal7_jwt_secret_key_2025"  # 실제 운영에서는 환경변수에서 가져와야 함
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30일

# 라우터 생성
router = APIRouter(prefix="/api/auth")
security = HTTPBearer()

# 데이터베이스 연결 함수
def get_db_connection():
    """PostgreSQL 데이터베이스 연결"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="livedb",
            user="liveuser",
            password="livepass2024",
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """액세스 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """현재 사용자 정보 가져오기"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT id, email, full_name, phone, is_active, email_verified, created_at, last_login
    FROM users WHERE id = %s AND is_active = true
    """, (user_id,))
    
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return UserResponse(**user)

@router.get("/health")
async def auth_health():
    """인증 시스템 상태 확인"""
    return {
        "service": "Authentication System",
        "status": "healthy",
        "version": "1.0.0",
        "provider": "HEAL7"
    }

@router.post("/register", response_model=TokenResponse)
async def register_user(user_data: UserRegister):
    """사용자 회원가입"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 이메일 중복 확인
        cursor.execute("SELECT id FROM users WHERE email = %s", (user_data.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다")
        
        # 비밀번호 해싱
        hashed_password = hash_password(user_data.password)
        
        # 사용자 생성
        cursor.execute("""
        INSERT INTO users (email, hashed_password, full_name, phone, is_active, email_verified, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, email, full_name, phone, is_active, email_verified, created_at
        """, (
            user_data.email,
            hashed_password,
            user_data.full_name,
            user_data.phone,
            True,
            False,  # 이메일 인증은 추후 구현
            datetime.now(),
            datetime.now()
        ))
        
        new_user = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        # JWT 토큰 생성
        access_token = create_access_token(data={"sub": new_user["id"]})
        
        user_response = UserResponse(**new_user, last_login=None)
        
        return TokenResponse(
            access_token=access_token,
            user=user_response
        )
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        if "이미 등록된 이메일입니다" in str(e):
            raise e
        raise HTTPException(status_code=500, detail="회원가입 중 오류가 발생했습니다")

@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin):
    """사용자 로그인"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 사용자 조회
        cursor.execute("""
        SELECT id, email, hashed_password, full_name, phone, is_active, email_verified, created_at, last_login
        FROM users WHERE email = %s AND is_active = true
        """, (login_data.email,))
        
        user = cursor.fetchone()
        if not user or not verify_password(login_data.password, user["hashed_password"]):
            raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다")
        
        # 마지막 로그인 시간 업데이트
        cursor.execute("""
        UPDATE users SET last_login = %s, updated_at = %s WHERE id = %s
        """, (datetime.now(), datetime.now(), user["id"]))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # JWT 토큰 생성
        access_token = create_access_token(data={"sub": user["id"]})
        
        user_response = UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            phone=user["phone"],
            is_active=user["is_active"],
            email_verified=user["email_verified"],
            created_at=user["created_at"],
            last_login=datetime.now()
        )
        
        return TokenResponse(
            access_token=access_token,
            user=user_response
        )
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        if "이메일 또는 비밀번호가 올바르지 않습니다" in str(e):
            raise e
        raise HTTPException(status_code=500, detail="로그인 중 오류가 발생했습니다")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """현재 로그인한 사용자 정보 조회"""
    return current_user

@router.post("/logout")
async def logout_user():
    """사용자 로그아웃 (클라이언트에서 토큰 삭제)"""
    return {"message": "로그아웃되었습니다"}

@router.post("/refresh")
async def refresh_token(current_user: UserResponse = Depends(get_current_user)):
    """토큰 갱신"""
    access_token = create_access_token(data={"sub": current_user.id})
    return {"access_token": access_token, "token_type": "bearer"}