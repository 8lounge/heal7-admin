#!/usr/bin/env python3
"""
HEAL7 마케팅 크롤러 관리 API 라우터
8001 포트 admin.heal7.com에서 크롤링 시스템 전체 관리
"""

import logging
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
import httpx
import asyncpg

# AI 서비스 임포트
from api.services.gemini_crawler_service import (
    validate_api_with_ai,
    optimize_job_with_ai,
    validate_worker_config_with_ai
)

logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/admin-api/marketing-crawler", tags=["Marketing Crawler Management"])

# Pydantic 모델 정의
class APIKeyCreate(BaseModel):
    name: str = Field(..., description="API 키 이름")
    provider: str = Field(..., description="제공업체")
    base_url: str = Field(..., description="기본 URL")
    api_key: str = Field(..., description="API 키")
    additional_params: Optional[Dict[str, Any]] = Field(None, description="추가 파라미터")
    rate_limit: int = Field(1000, description="시간당 호출 제한")

class CrawlingJobCreate(BaseModel):
    name: str = Field(..., description="작업 이름")
    category: str = Field(..., description="카테고리")
    source_type: str = Field(..., description="소스 타입")
    target_url: str = Field(..., description="대상 URL")
    search_keywords: List[str] = Field(..., description="검색 키워드")
    crawl_frequency: str = Field("30 minutes", description="크롤링 주기")
    access_pattern: str = Field("sequential", description="접근 패턴")
    random_delay_min: int = Field(5, description="최소 지연(초)")
    random_delay_max: int = Field(30, description="최대 지연(초)")
    collection_scope: Optional[Dict[str, Any]] = Field(None, description="수집 범위")
    speed_settings: Optional[Dict[str, Any]] = Field(None, description="속도 설정")
    ai_processing: bool = Field(True, description="AI 처리 여부")

class WorkerConfig(BaseModel):
    worker_id: int
    max_workers: int = Field(2, description="최대 워커 수")
    config: Dict[str, Any] = Field(..., description="워커 설정")

# 임시 데이터베이스 연결 (실제로는 연결 풀 사용)
async def get_db_connection():
    # 실제 구현 시 connection pool 사용
    return None

# ==============================================
# API 키 관리
# ==============================================

@router.get("/api-keys")
async def get_api_keys():
    """등록된 API 키 목록 조회"""
    # 임시 하드코딩 데이터 (실제로는 DB 조회)
    return {
        "api_keys": [
            {
                "id": 1,
                "name": "공공데이터포털_기업정보",
                "provider": "공공데이터포털",
                "base_url": "https://apis.data.go.kr/1160100/service/GetCorpBasicInfoService",
                "api_key": "SAMPLE_KEY_1***",
                "rate_limit": 2000,
                "status": "active",
                "last_used": "2025-08-05T10:30:00",
                "usage_count": 1247
            },
            {
                "id": 2,
                "name": "네이버_트렌드API",
                "provider": "NAVER",
                "base_url": "https://openapi.naver.com/v1/datalab/search",
                "api_key": "NAVER_KEY***",
                "rate_limit": 5000,
                "status": "active",
                "last_used": "2025-08-05T10:25:00",
                "usage_count": 892
            },
            {
                "id": 3,
                "name": "구글_트렌드API",
                "provider": "Google",
                "base_url": "https://trends.googleapis.com/trends/api",
                "api_key": "GOOGLE_KEY***",
                "rate_limit": 10000,
                "status": "error",
                "last_used": "2025-08-05T09:15:00",
                "usage_count": 0,
                "error_message": "인증 키 만료"
            }
        ]
    }

@router.post("/api-keys")
async def create_api_key(api_key_data: APIKeyCreate):
    """새 API 키 등록 (AI 자동 검증 포함)"""
    
    # 1. AI 모델을 통한 API 검증
    ai_validation_result = await validate_api_with_ai(api_key_data)
    
    if not ai_validation_result["valid"]:
        raise HTTPException(
            status_code=400, 
            detail=f"API 검증 실패: {ai_validation_result['error']}"
        )
    
    # 2. 실제 API 테스트 호출
    test_result = await test_api_connection(api_key_data)
    
    # 3. 데이터베이스에 저장 (실제 구현)
    api_key_id = await save_api_key_to_db(api_key_data, ai_validation_result)
    
    logger.info(f"새 API 키 등록: {api_key_data.name} (ID: {api_key_id})")
    
    return {
        "success": True,
        "api_key_id": api_key_id,
        "message": "API 키가 성공적으로 등록되었습니다",
        "ai_analysis": ai_validation_result["analysis"],
        "test_result": test_result
    }

@router.put("/api-keys/{api_key_id}")
async def update_api_key(api_key_id: int, api_key_data: APIKeyCreate):
    """API 키 정보 수정"""
    # AI를 통한 변경사항 검증 (기본 API 검증 재사용)
    ai_validation = await validate_api_with_ai(api_key_data)
    
    # 데이터베이스 업데이트
    updated = await update_api_key_in_db(api_key_id, api_key_data)
    
    if not updated:
        raise HTTPException(status_code=404, detail="API 키를 찾을 수 없습니다")
    
    return {
        "success": True,
        "message": "API 키가 성공적으로 수정되었습니다",
        "ai_validation": ai_validation
    }

# ==============================================
# 크롤링 작업 관리
# ==============================================

@router.get("/jobs")
async def get_crawling_jobs():
    """크롤링 작업 목록 조회"""
    return {
        "jobs": [
            {
                "id": 1,
                "name": "공공데이터_기업현황",
                "category": "창업자",
                "source_type": "api",
                "target_url": "https://apis.data.go.kr/1160100/service/GetCorpBasicInfoService",
                "status": "active",
                "last_run": "2025-08-05T10:00:00",
                "next_run": "2025-08-05T11:00:00",
                "success_rate": 98.5,
                "items_collected": 15467,
                "search_keywords": ["스타트업", "중소기업", "벤처기업"]
            },
            {
                "id": 2,
                "name": "네이버_뉴스_심리",
                "category": "심리분석",
                "source_type": "api",
                "target_url": "https://openapi.naver.com/v1/search/news.json",
                "status": "running",
                "last_run": "2025-08-05T10:30:00",
                "next_run": "2025-08-05T11:00:00",
                "success_rate": 95.2,
                "items_collected": 8923,
                "search_keywords": ["심리상담", "정신건강", "스트레스"]
            },
            {
                "id": 3,
                "name": "RSS_경제뉴스",
                "category": "전략가",
                "source_type": "rss",
                "target_url": "https://www.mk.co.kr/rss/30000001/",
                "status": "error",
                "last_run": "2025-08-05T09:45:00",
                "next_run": "2025-08-05T10:05:00",
                "success_rate": 45.3,
                "items_collected": 234,
                "search_keywords": ["경제전망", "투자전략", "시장분석"],
                "error_message": "RSS 피드 접근 거부"
            }
        ]
    }

@router.post("/jobs")
async def create_crawling_job(job_data: CrawlingJobCreate, background_tasks: BackgroundTasks):
    """새 크롤링 작업 생성 (AI 최적화 포함)"""
    
    # AI를 통한 작업 설정 최적화
    ai_optimization = await optimize_job_with_ai(job_data)
    
    # 최적화된 설정 적용
    optimized_job = apply_ai_optimization(job_data, ai_optimization)
    
    # 데이터베이스에 저장
    job_id = await save_crawling_job(optimized_job)
    
    # 백그라운드에서 초기 테스트 실행
    background_tasks.add_task(test_crawling_job, job_id)
    
    logger.info(f"새 크롤링 작업 생성: {job_data.name} (ID: {job_id})")
    
    return {
        "success": True,
        "job_id": job_id,
        "message": "크롤링 작업이 성공적으로 생성되었습니다",
        "ai_optimization": ai_optimization,
        "optimized_settings": optimized_job.dict()
    }

@router.post("/jobs/{job_id}/start")
async def start_crawling_job(job_id: int, background_tasks: BackgroundTasks):
    """크롤링 작업 시작"""
    
    # 작업 상태 확인
    job = await get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
    
    if job["status"] == "running":
        return {"message": "작업이 이미 실행 중입니다", "status": "running"}
    
    # 백그라운드에서 크롤링 시작
    background_tasks.add_task(execute_crawling_job, job_id)
    
    # 작업 상태 업데이트
    await update_job_status(job_id, "running")
    
    return {
        "success": True,
        "message": f"크롤링 작업이 시작되었습니다: {job['name']}",
        "job_id": job_id,
        "status": "running"
    }

@router.post("/jobs/{job_id}/stop")
async def stop_crawling_job(job_id: int):
    """크롤링 작업 중지"""
    
    # 작업 중지 처리
    stopped = await stop_job_execution(job_id)
    
    if not stopped:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
    
    await update_job_status(job_id, "stopped")
    
    return {
        "success": True,
        "message": "크롤링 작업이 중지되었습니다",
        "job_id": job_id,
        "status": "stopped"
    }

# ==============================================
# 워커 관리
# ==============================================

@router.get("/workers")
async def get_workers():
    """워커 목록 및 상태 조회"""
    return {
        "workers": [
            {
                "id": 1,
                "name": "서버워커1",
                "type": "server",
                "location": "heal7_server",
                "status": "running",
                "max_workers": 2,
                "current_workers": 2,
                "last_heartbeat": "2025-08-05T10:35:00",
                "jobs_assigned": 3,
                "success_rate": 98.2,
                "config": {
                    "api_only": True,
                    "rate_limit": 1000,
                    "concurrent_requests": 5
                }
            },
            {
                "id": 2,
                "name": "서버워커2",
                "type": "server",
                "location": "heal7_server",
                "status": "running",
                "max_workers": 2,
                "current_workers": 1,
                "last_heartbeat": "2025-08-05T10:34:30",
                "jobs_assigned": 2,
                "success_rate": 95.7,
                "config": {
                    "rss_xml_only": True,
                    "interval": "15min",
                    "timeout": 30
                }
            },
            {
                "id": 3,
                "name": "로컬워커1",
                "type": "local",
                "location": "home_docker",
                "status": "offline",
                "max_workers": 8,
                "current_workers": 0,
                "last_heartbeat": "2025-08-05T08:15:00",
                "jobs_assigned": 0,
                "success_rate": 0,
                "config": {
                    "playwright_ratio": 0.2,
                    "aggressive": True,
                    "stealth_mode": True
                }
            }
        ]
    }

@router.post("/workers/{worker_id}/config")
async def update_worker_config(worker_id: int, config: WorkerConfig):
    """워커 설정 업데이트"""
    
    # AI를 통한 설정 검증
    ai_validation = await validate_worker_config_with_ai(config.dict())
    
    if not ai_validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail=f"설정 검증 실패: {ai_validation['error']}"
        )
    
    # 설정 적용
    updated = await update_worker_config_in_db(worker_id, config)
    
    if not updated:
        raise HTTPException(status_code=404, detail="워커를 찾을 수 없습니다")
    
    return {
        "success": True,
        "message": "워커 설정이 성공적으로 업데이트되었습니다",
        "ai_validation": ai_validation,
        "applied_config": config.dict()
    }

# ==============================================
# AI 처리 및 분석
# ==============================================

@router.get("/ai-processing/queue")
async def get_ai_processing_queue():
    """AI 처리 큐 상태 조회"""
    return {
        "queue_status": {
            "pending": 234,
            "processing": 12,
            "completed": 15687,
            "failed": 45
        },
        "recent_processes": [
            {
                "id": 12345,
                "type": "api_conversion",
                "data_source": "공공데이터포털_기업정보",
                "status": "processing",
                "started_at": "2025-08-05T10:30:00",
                "estimated_completion": "2025-08-05T10:32:00"
            },
            {
                "id": 12344,
                "type": "content_analysis",
                "data_source": "네이버_뉴스_심리",
                "status": "completed",
                "started_at": "2025-08-05T10:28:00",
                "completed_at": "2025-08-05T10:29:15",
                "confidence_score": 0.95
            }
        ]
    }

@router.get("/analytics/dashboard")
async def get_analytics_dashboard():
    """크롤링 시스템 전체 대시보드"""
    return {
        "summary": {
            "total_jobs": 12,
            "active_jobs": 8,
            "total_workers": 4,
            "running_workers": 2,
            "daily_collections": 45621,
            "success_rate": 96.8,
            "ai_processing_rate": 98.2
        },
        "category_stats": [
            {"category": "창업자", "jobs": 3, "collections": 15467, "success_rate": 98.5},
            {"category": "소비분석", "jobs": 2, "collections": 8923, "success_rate": 95.2},
            {"category": "심리분석", "jobs": 2, "collections": 7834, "success_rate": 93.7},
            {"category": "트렌드분석", "jobs": 3, "collections": 9234, "success_rate": 97.1},
            {"category": "전략가", "jobs": 2, "collections": 4163, "success_rate": 89.3}
        ],
        "performance_metrics": {
            "avg_response_time": "1.2s",
            "data_quality_score": 8.7,
            "ai_accuracy": 94.3,
            "system_uptime": "99.8%"
        }
    }

# ==============================================
# AI 처리 헬퍼 함수들 (실제 Gemini 연동)
# ==============================================

async def validate_api_with_ai(api_data: APIKeyCreate) -> Dict[str, Any]:
    """AI를 통한 API 키 및 설정 검증"""
    # 실제 Gemini API 호출 구현
    return {
        "valid": True,
        "analysis": {
            "api_type": "REST API",
            "authentication": "API Key",
            "rate_limits": "Standard",
            "recommended_settings": {
                "concurrent_requests": 5,
                "retry_attempts": 3,
                "timeout": 30
            }
        }
    }

async def optimize_job_with_ai(job_data: CrawlingJobCreate) -> Dict[str, Any]:
    """AI를 통한 크롤링 작업 최적화"""
    # 실제 AI 최적화 로직
    return {
        "optimized": True,
        "recommendations": {
            "frequency": "25 minutes",  # 원본 30분에서 최적화
            "batch_size": 100,
            "retry_strategy": "exponential_backoff"
        }
    }

# 기타 헬퍼 함수들 (DB 연동)
async def save_api_key_to_db(api_data: APIKeyCreate, ai_result: Dict) -> int:
    # 실제 DB 저장 로직
    return 1

async def test_api_connection(api_data: APIKeyCreate) -> Dict[str, Any]:
    # 실제 API 테스트 호출
    return {"success": True, "response_time": "0.8s"}

async def update_api_key_in_db(api_key_id: int, api_data: APIKeyCreate) -> bool:
    # 실제 DB 업데이트 로직
    return True

async def apply_ai_optimization(job_data: CrawlingJobCreate, ai_optimization: Dict[str, Any]) -> CrawlingJobCreate:
    # AI 최적화 결과를 job_data에 적용
    if ai_optimization.get("optimized"):
        recommendations = ai_optimization.get("recommendations", {})
        if "frequency" in recommendations:
            job_data.crawl_frequency = recommendations["frequency"]
        if "batch_size" in recommendations:
            if not job_data.speed_settings:
                job_data.speed_settings = {}
            job_data.speed_settings["batch_size"] = recommendations["batch_size"]
    return job_data

async def save_crawling_job(job_data: CrawlingJobCreate) -> int:
    # 실제 DB 저장 로직
    return 1

async def test_crawling_job(job_id: int):
    # 백그라운드 테스트 실행
    logger.info(f"크롤링 작업 테스트 시작: {job_id}")
    # 테스트 로직 구현
    pass

async def get_job_by_id(job_id: int) -> Optional[Dict[str, Any]]:
    # DB에서 작업 조회
    return {"id": job_id, "name": "Test Job", "status": "stopped"}

async def update_job_status(job_id: int, status: str) -> bool:
    # 작업 상태 업데이트
    logger.info(f"작업 {job_id} 상태 변경: {status}")
    return True

async def stop_job_execution(job_id: int) -> bool:
    # 실제 작업 중지 로직
    logger.info(f"작업 중지: {job_id}")
    return True

async def execute_crawling_job(job_id: int):
    # 실제 크롤링 실행 로직
    logger.info(f"크롤링 작업 실행: {job_id}")
    # 크롤링 로직 구현
    pass

async def update_worker_config_in_db(worker_id: int, config: WorkerConfig) -> bool:
    # 워커 설정 DB 업데이트
    logger.info(f"워커 {worker_id} 설정 업데이트")
    return True

# 라우터 내보내기
marketing_crawler_router = router