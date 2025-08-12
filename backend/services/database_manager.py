"""
HEAL7 Database Manager
PostgreSQL 연결 관리 및 공통 데이터베이스 작업 처리
"""

import asyncio
import asyncpg
import logging
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Database connection pool
_connection_pool: Optional[asyncpg.Pool] = None

async def init_db_pool():
    """데이터베이스 연결 풀 초기화"""
    global _connection_pool
    
    if _connection_pool is None:
        try:
            # PostgreSQL peer authentication 우선 시도
            db_configs = [
                # 1. Peer authentication (Unix domain socket)
                {
                    'host': '/var/run/postgresql',
                    'user': 'postgres',
                    'database': 'livedb',
                    'min_size': 5,
                    'max_size': 20
                },
                # 2. TCP connection with environment variables
                {
                    'host': os.getenv('DB_HOST', 'localhost'),
                    'port': int(os.getenv('DB_PORT', 5432)),
                    'user': os.getenv('DB_USER', 'postgres'),
                    'password': os.getenv('DB_PASSWORD', ''),
                    'database': os.getenv('DB_NAME', 'livedb'),
                    'min_size': 5,
                    'max_size': 20
                }
            ]
            
            last_error = None
            for i, db_config in enumerate(db_configs, 1):
                try:
                    _connection_pool = await asyncpg.create_pool(**db_config)
                    logger.info(f"Database connection pool initialized successfully using config {i}")
                    break
                except Exception as e:
                    last_error = e
                    logger.warning(f"Database config {i} failed: {e}")
                    continue
            
            if _connection_pool is None:
                raise last_error or Exception("All database configurations failed")
            
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            _connection_pool = None
            raise
    
    return _connection_pool

async def get_db_connection():
    """데이터베이스 연결 획득"""
    global _connection_pool
    
    if _connection_pool is None:
        await init_db_pool()
    
    try:
        connection = await _connection_pool.acquire()
        return connection
    except Exception as e:
        logger.error(f"Failed to get database connection: {e}")
        # 재시도
        try:
            await init_db_pool()
            connection = await _connection_pool.acquire()
            return connection
        except Exception as retry_error:
            logger.error(f"Failed to reconnect to database: {retry_error}")
            raise

async def close_db_pool():
    """데이터베이스 연결 풀 종료"""
    global _connection_pool
    
    if _connection_pool:
        await _connection_pool.close()
        _connection_pool = None
        logger.info("Database connection pool closed")

class DatabaseManager:
    """데이터베이스 관리 클래스"""
    
    @staticmethod
    async def ensure_analytics_tables():
        """Analytics용 테이블들이 존재하는지 확인하고 없으면 생성"""
        conn = await get_db_connection()
        
        try:
            # Users 테이블
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE,
                    username VARCHAR(100),
                    age INTEGER,
                    gender VARCHAR(10),
                    region VARCHAR(50),
                    created_at TIMESTAMP DEFAULT NOW(),
                    last_login TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'active'
                )
            """)
            
            # Page Analytics 테이블  
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS page_analytics (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(100),
                    user_id INTEGER REFERENCES users(id),
                    page_path VARCHAR(255),
                    device_type VARCHAR(20),
                    timestamp TIMESTAMP DEFAULT NOW(),
                    date DATE DEFAULT CURRENT_DATE,
                    time_on_page INTEGER DEFAULT 0,
                    bounce BOOLEAN DEFAULT FALSE,
                    session_duration INTEGER DEFAULT 0
                )
            """)
            
            # Saju Analysis Sessions 테이블
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS saju_analysis_sessions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    session_id VARCHAR(100),
                    created_at TIMESTAMP DEFAULT NOW(),
                    completed_at TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'pending',
                    ai_reviewed BOOLEAN DEFAULT FALSE,
                    processing_time INTERVAL,
                    result_data JSONB
                )
            """)
            
            # Keyword Usage Stats 테이블
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS keyword_usage_stats (
                    id SERIAL PRIMARY KEY,
                    keyword_id INTEGER,
                    date DATE DEFAULT CURRENT_DATE,
                    usage_count INTEGER DEFAULT 1,
                    status VARCHAR(20) DEFAULT 'active',
                    UNIQUE(keyword_id, date)
                )
            """)
            
            # Sessions 테이블
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id VARCHAR(100) PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    created_at TIMESTAMP DEFAULT NOW(),
                    last_activity TIMESTAMP DEFAULT NOW(),
                    device_info JSONB,
                    ip_address INET
                )
            """)
            
            # System Workers 테이블
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS system_workers (
                    id SERIAL PRIMARY KEY,
                    worker_name VARCHAR(100) UNIQUE,
                    worker_type VARCHAR(50),
                    last_heartbeat TIMESTAMP DEFAULT NOW(),
                    status VARCHAR(20) DEFAULT 'active',
                    config JSONB
                )
            """)
            
            # 인덱스 생성
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_page_analytics_date ON page_analytics(date)",
                "CREATE INDEX IF NOT EXISTS idx_page_analytics_user ON page_analytics(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_page_analytics_page ON page_analytics(page_path)",
                "CREATE INDEX IF NOT EXISTS idx_saju_sessions_user ON saju_analysis_sessions(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_saju_sessions_date ON saju_analysis_sessions(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_keyword_stats_date ON keyword_usage_stats(date)",
                "CREATE INDEX IF NOT EXISTS idx_users_created ON users(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_sessions_activity ON sessions(last_activity)"
            ]
            
            for index_sql in indexes:
                await conn.execute(index_sql)
            
            logger.info("Analytics tables and indexes ensured")
            
        except Exception as e:
            logger.error(f"Failed to ensure analytics tables: {e}")
        finally:
            await conn.close()
    
    @staticmethod
    async def seed_sample_data():
        """샘플 데이터 삽입 (개발/테스트용)"""
        conn = await get_db_connection()
        
        try:
            # 사용자 데이터 확인
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            
            if user_count == 0:
                # 샘플 사용자 데이터 생성
                sample_users = []
                for i in range(100):
                    sample_users.append((
                        f"user{i}@heal7.com",
                        f"user{i}",
                        20 + (i % 50),  # 20-70세
                        "여성" if i % 2 == 0 else "남성",
                        ["서울", "부산", "대구", "인천", "광주"][i % 5],
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))
                
                await conn.executemany("""
                    INSERT INTO users (email, username, age, gender, region, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, sample_users)
                
                logger.info("Sample user data inserted")
            
            # 페이지 분석 데이터 확인
            pageview_count = await conn.fetchval("SELECT COUNT(*) FROM page_analytics")
            
            if pageview_count == 0:
                # 샘플 페이지뷰 데이터
                sample_pageviews = []
                pages = ["/", "/saju/free", "/saju/detail", "/keywords", "/profile", "/community"]
                devices = ["mobile", "desktop", "tablet"]
                
                for i in range(1000):
                    sample_pageviews.append((
                        f"session_{i % 200}",  # 200개 세션
                        (i % 100) + 1,       # user_id
                        pages[i % len(pages)],
                        devices[i % len(devices)],
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        60 + (i % 300),      # time_on_page
                        i % 10 == 0          # bounce (10% bounce rate)
                    ))
                
                await conn.executemany("""
                    INSERT INTO page_analytics 
                    (session_id, user_id, page_path, device_type, timestamp, time_on_page, bounce)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, sample_pageviews)
                
                logger.info("Sample pageview data inserted")
            
        except Exception as e:
            logger.error(f"Failed to seed sample data: {e}")
        finally:
            await conn.close()
    
    @staticmethod
    async def get_table_info(table_name: str) -> Dict[str, Any]:
        """테이블 정보 조회"""
        conn = await get_db_connection()
        
        try:
            # 테이블 존재 여부 확인
            exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = $1
                )
            """, table_name)
            
            if not exists:
                return {"exists": False}
            
            # 컬럼 정보 조회
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = $1
                ORDER BY ordinal_position
            """, table_name)
            
            # 레코드 수 조회
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
            
            return {
                "exists": True,
                "columns": [dict(col) for col in columns],
                "record_count": count
            }
            
        except Exception as e:
            logger.error(f"Failed to get table info for {table_name}: {e}")
            return {"exists": False, "error": str(e)}
        finally:
            await conn.close()

# 초기화 함수
async def initialize_analytics_db():
    """Analytics 데이터베이스 초기화"""
    try:
        await DatabaseManager.ensure_analytics_tables()
        await DatabaseManager.seed_sample_data()
        logger.info("Analytics database initialized successfully")
    except Exception as e:
        logger.error(f"Analytics database initialization failed: {e}")
        raise