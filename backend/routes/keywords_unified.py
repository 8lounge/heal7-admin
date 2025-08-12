#!/usr/bin/env python3
"""
HEAL7 키워드 시스템 통합 API
모든 키워드 관련 기능을 하나의 라우터로 통합
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import subprocess
import asyncio

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
import asyncpg
import redis
import json
import os

# 로깅 설정
logger = logging.getLogger(__name__)

# 통합 API 라우터 생성 (관리자 백엔드용)
router = APIRouter(prefix="/admin-api/keywords", tags=["Keywords Unified"])

# Redis 연결 정보 (데이터베이스는 database_manager 사용)
REDIS_URL = "redis://localhost:6379"

# 응답 모델들
class KeywordResponse(BaseModel):
    id: int
    keyword: str
    subcategory_id: Optional[int] = None
    subcategory_name: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

class KeywordStats(BaseModel):
    total_keywords: int
    active_keywords: int
    subcategories: Dict[str, int]

class KeywordSearchRequest(BaseModel):
    query: Optional[str] = None
    subcategory_id: Optional[int] = None
    limit: Optional[int] = 100

# 서브프로세스를 통한 PostgreSQL 직접 접근
async def run_postgres_query(query: str, params: List = None):
    """PostgreSQL 쿼리를 subprocess로 실행"""
    try:
        # psql 명령어 구성
        cmd = [
            'sudo', '-u', 'postgres', 'psql', '-d', 'livedb',
            '-t', '-A', '-F', '\t',  # 탭 분리, 헤더 없음
            '-c', query
        ]
        
        # 비동기 subprocess 실행
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode('utf-8').strip()
            logger.error(f"PostgreSQL query failed: {error_msg}")
            raise Exception(f"Database query failed: {error_msg}")
        
        result = stdout.decode('utf-8').strip()
        logger.debug(f"Query executed successfully: {len(result)} chars returned")
        return result
        
    except Exception as e:
        logger.error(f"Failed to execute PostgreSQL query: {e}")
        raise

async def parse_query_result(result: str, columns: List[str]) -> List[Dict]:
    """쿼리 결과를 파싱하여 딕셔너리 리스트로 변환"""
    if not result:
        return []
    
    rows = []
    for line in result.split('\n'):
        if line.strip():
            values = line.split('\t')
            if len(values) == len(columns):
                row_dict = {}
                for i, col in enumerate(columns):
                    value = values[i]
                    # NULL 값 처리
                    if value == '' or value == 'NULL':
                        row_dict[col] = None
                    # 정수 변환
                    elif col in ['id', 'count', 'total', 'active', 'usage_count']:
                        try:
                            row_dict[col] = int(value)
                        except ValueError:
                            row_dict[col] = 0
                    # 실수 변환
                    elif col in ['avg_score', 'score']:
                        try:
                            row_dict[col] = float(value)
                        except ValueError:
                            row_dict[col] = 0.0
                    # 불린 변환
                    elif col in ['is_active']:
                        row_dict[col] = value.lower() in ('t', 'true', '1', 'yes')
                    else:
                        row_dict[col] = value
                rows.append(row_dict)
    
    return rows

# ==================== 통합 키워드 API 엔드포인트 ====================

@router.get("/health")
@router.get("/health/")
async def keyword_health_check():
    """키워드 시스템 헬스체크"""
    return {
        "status": "healthy",
        "service": "keywords-unified",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/all", response_model=List[KeywordResponse])
@router.get("/all/", response_model=List[KeywordResponse])
async def get_all_keywords(
    subcategory_id: Optional[int] = Query(None, description="서브카테고리 ID 필터"),
    active_only: bool = Query(True, description="활성화된 키워드만 조회"),
    limit: int = Query(500, description="최대 결과 수")
):
    """모든 키워드 조회 (통합)"""
    try:
        # WHERE 조건 구성
        where_conditions = []
        if subcategory_id:
            where_conditions.append(f"k.subcategory_id = {subcategory_id}")
        if active_only:
            where_conditions.append("k.is_active = true")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        query = f"""
            SELECT k.id, k.text, k.subcategory_id, ks.name as subcategory_name, k.is_active, k.created_at
            FROM keywords k 
            LEFT JOIN keyword_subcategories ks ON k.subcategory_id = ks.id
            WHERE {where_clause}
            ORDER BY ks.name, k.text
            LIMIT {limit}
        """
        
        result = await run_postgres_query(query)
        columns = ['id', 'text', 'subcategory_id', 'subcategory_name', 'is_active', 'created_at']
        rows = await parse_query_result(result, columns)
            
        keywords = []
        for row in rows:
            keywords.append(KeywordResponse(
                id=row['id'],
                keyword=row['text'],
                subcategory_id=row['subcategory_id'],
                subcategory_name=row['subcategory_name'],
                is_active=row['is_active'],
                created_at=row['created_at']
            ))
        
        logger.info(f"키워드 조회 완료: {len(keywords)}개")
        return keywords
        
    except Exception as e:
        logger.error(f"키워드 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"키워드 조회 실패: {str(e)}")

@router.get("/stats", response_model=KeywordStats)
@router.get("/stats/", response_model=KeywordStats)
async def get_keyword_stats():
    """키워드 통계 조회 (통합)"""
    try:
        # 전체 통계 쿼리
        total_query = "SELECT COUNT(*) as total FROM keywords"
        total_result = await run_postgres_query(total_query)
        total_count = int(total_result.strip()) if total_result.strip() else 0
        
        # 활성 키워드 통계
        active_query = "SELECT COUNT(*) as active FROM keywords WHERE is_active = true"
        active_result = await run_postgres_query(active_query)
        active_count = int(active_result.strip()) if active_result.strip() else 0
        
        # 서브카테고리별 통계
        subcategory_query = """
            SELECT ks.name, COUNT(*) as count 
            FROM keywords k
            LEFT JOIN keyword_subcategories ks ON k.subcategory_id = ks.id
            WHERE k.is_active = true 
            GROUP BY ks.name 
            ORDER BY count DESC
        """
        subcategory_result = await run_postgres_query(subcategory_query)
        subcategory_rows = await parse_query_result(subcategory_result, ['name', 'count'])
        
        subcategories = {row['name']: row['count'] for row in subcategory_rows if row['name']}
        
        stats = KeywordStats(
            total_keywords=total_count,
            active_keywords=active_count,
            subcategories=subcategories
        )
        
        logger.info(f"키워드 통계 조회 완료: 총 {stats.total_keywords}개, 활성 {stats.active_keywords}개")
        return stats
        
    except Exception as e:
        logger.error(f"키워드 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"키워드 통계 조회 실패: {str(e)}")

@router.get("/search", response_model=List[KeywordResponse])
@router.get("/search/", response_model=List[KeywordResponse])
async def search_keywords(
    q: Optional[str] = Query(None, description="검색할 키워드"),
    subcategory_id: Optional[int] = Query(None, description="서브카테고리 ID 필터"),
    limit: int = Query(100, description="최대 결과 수")
):
    """키워드 검색 (통합)"""
    try:
        # WHERE 조건 구성
        where_conditions = ["k.is_active = true"]
        
        if q:
            # SQL Injection 방지를 위한 이스케이프 처리
            escaped_query = q.replace("'", "''")
            where_conditions.append(f"k.text ILIKE '%{escaped_query}%'")
        
        if subcategory_id:
            where_conditions.append(f"k.subcategory_id = {subcategory_id}")
        
        where_clause = " AND ".join(where_conditions)
        
        # 검색 순서: 정확한 매치 우선
        order_clause = "ORDER BY k.text" 
        if q:
            escaped_query = q.replace("'", "''")
            order_clause = f"ORDER BY CASE WHEN k.text ILIKE '{escaped_query}%' THEN 1 ELSE 2 END, k.text"
        
        query = f"""
            SELECT k.id, k.text, k.subcategory_id, ks.name as subcategory_name, k.is_active, k.created_at
            FROM keywords k
            LEFT JOIN keyword_subcategories ks ON k.subcategory_id = ks.id
            WHERE {where_clause}
            {order_clause}
            LIMIT {limit}
        """
        
        result = await run_postgres_query(query)
        columns = ['id', 'text', 'subcategory_id', 'subcategory_name', 'is_active', 'created_at']
        rows = await parse_query_result(result, columns)
            
        keywords = []
        for row in rows:
            keywords.append(KeywordResponse(
                id=row['id'],
                keyword=row['text'],
                subcategory_id=row['subcategory_id'],
                subcategory_name=row['subcategory_name'],
                is_active=row['is_active'],
                created_at=row['created_at']
            ))
        
        logger.info(f"키워드 검색 완료: '{q}' 결과 {len(keywords)}개")
        return keywords
        
    except Exception as e:
        logger.error(f"키워드 검색 실패: {e}")
        raise HTTPException(status_code=500, detail=f"키웛드 검색 실패: {str(e)}")

@router.get("/subcategories")
async def get_subcategories():
    """키워드 서브카테고리 목록 조회"""
    try:
        query = """
            SELECT ks.id, ks.name, ks.group_code, ks.description, COUNT(k.id) as keyword_count
            FROM keyword_subcategories ks
            LEFT JOIN keywords k ON ks.id = k.subcategory_id AND k.is_active = true
            GROUP BY ks.id, ks.name, ks.group_code, ks.description
            ORDER BY ks.group_code, ks.name
        """
        
        result = await run_postgres_query(query)
        rows = await parse_query_result(result, ['id', 'name', 'group_code', 'description', 'keyword_count'])
            
        subcategories = [
            {
                "id": row['id'],
                "name": row['name'], 
                "group_code": row['group_code'],
                "description": row['description'],
                "keyword_count": row['keyword_count']
            } 
            for row in rows
        ]
        
        logger.info(f"서브카테고리 조회 완료: {len(subcategories)}개")
        return {"subcategories": subcategories}
        
    except Exception as e:
        logger.error(f"서브카테고리 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서브카테고리 조회 실패: {str(e)}")

@router.get("/matrix")
async def get_keyword_matrix(
    subcategory_id: Optional[int] = Query(None, description="서브카테고리 ID 필터")
):
    """키워드 매트릭스 데이터 조회 (3D 시각화용)"""
    try:
        # 간단한 키워드 목록으로 매트릭스 생성
        where_clause = "k.is_active = true"
        if subcategory_id:
            where_clause += f" AND k.subcategory_id = {subcategory_id}"
        
        query = f"""
            SELECT k.id, k.text, k.subcategory_id, ks.name as subcategory_name
            FROM keywords k
            LEFT JOIN keyword_subcategories ks ON k.subcategory_id = ks.id
            WHERE {where_clause}
            ORDER BY k.id
            LIMIT 442
        """
        
        result = await run_postgres_query(query)
        columns = ['id', 'text', 'subcategory_id', 'subcategory_name']
        rows = await parse_query_result(result, columns)
            
        matrix_data = []
        for row in rows:
            matrix_data.append({
                "id": row['id'],
                "keyword": row['text'],
                "subcategory_id": row['subcategory_id'],
                "subcategory_name": row['subcategory_name'],
                "score": 5.0,  # 기본 점수
                "usage": 1,    # 기본 사용량
                "x": hash(row['text']) % 100,  # 간단한 위치 계산
                "y": hash(row['subcategory_name'] or 'default') % 100,
                "z": 5.0  # 기본 Z 위치
            })
        
        logger.info(f"키워드 매트릭스 생성 완료: {len(matrix_data)}개")
        return {
            "matrix": matrix_data,
            "total_keywords": len(matrix_data),
            "subcategory_filter": subcategory_id
        }
        
    except Exception as e:
        logger.error(f"키워드 매트릭스 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"키워드 매트릭스 생성 실패: {str(e)}")

# ==================== 디버그 및 관리 기능 ====================

@router.get("/debug/info")
async def get_debug_info():
    """디버그 정보 조회"""
    try:
        # 데이터베이스 연결 테스트
        db_version_result = await run_postgres_query("SELECT version()")
        db_version = db_version_result.strip() if db_version_result else "Unknown"
        
        # 키워드 테이블 정보
        table_query = """
            SELECT 
                schemaname, tablename, tableowner, tablespace, hasindexes, hasrules, hastriggers
            FROM pg_tables 
            WHERE tablename = 'keywords'
        """
        table_result = await run_postgres_query(table_query)
        table_info = await parse_query_result(table_result, 
                                            ['schemaname', 'tablename', 'tableowner', 'tablespace', 
                                             'hasindexes', 'hasrules', 'hastriggers'])
            
        debug_info = {
            "database": {
                "connected": True,
                "version": db_version[:50] + "..." if len(db_version) > 50 else db_version,
                "connection_method": "subprocess_psql"
            },
            "table_info": table_info,
            "service_info": {
                "router_prefix": "/admin-api/keywords",
                "unified_version": "4.0",
                "features": ["search", "stats", "matrix", "subcategories", "debug"],
                "database_manager": "subprocess_psql",
                "actual_columns": ["id", "text", "subcategory_id", "is_active", "created_at", "updated_at"]
            }
        }
        
        return debug_info
        
    except Exception as e:
        logger.error(f"디버그 정보 조회 실패: {e}")
        return {
            "database": {"connected": False, "error": str(e)},
            "service_info": {"status": "error", "connection_method": "subprocess_psql"}
        }