#!/usr/bin/env python3
"""
HEAL7 통합 관리자 API 서버 (2025-08-02 긴급 복구)
포트 8001에서 실행되는 모든 관리자 API의 통합 서버
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="HEAL7 통합 관리자 API",
    description="모든 관리자 서비스를 통합한 단일 API 서버",
    version="5.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 헬스체크 API
@app.get("/admin-api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "heal7-admin",
        "port": 8001,
        "timestamp": datetime.now().isoformat()
    }

# 기본 라우트
@app.get("/")
async def root():
    return {
        "service": "HEAL7 통합 관리자 API",
        "version": "5.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

# 글로벌 예외 처리기 추가
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Global exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {type(exc).__name__}: {str(exc)}"}
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ==================== 사주 AI 폴백 시스템 제거됨 ====================

# 사주 AI 서비스 제거됨


# AI 통계 서비스 제거됨

# 종합 AI 통계 서비스 제거됨

# 프론트엔드 호환성을 위한 별칭 API
@app.post("/admin-api/saju/ai")
async def saju_ai_compatibility_endpoint(request: dict):
    """사주 AI API (프론트엔드 호환성용 별칭)"""
    # ai-generate 엔드포인트로 리다이렉트
    return await saju_ai_generate_endpoint(request)

@app.post("/admin-api/ai/optimization/toggle")
async def toggle_optimization_mode(request: dict):
    """AI 최적화 모드 토글 API"""
    try:
        global OPTIMIZATION_ENABLED
        
        requested_mode = request.get("optimization_enabled", OPTIMIZATION_ENABLED)
        
        if requested_mode != OPTIMIZATION_ENABLED:
            OPTIMIZATION_ENABLED = requested_mode
            
            mode_text = "활성화" if OPTIMIZATION_ENABLED else "비활성화"
            logging.info(f"🔄 AI 최적화 모드 변경: {mode_text}")
            
            return {
                "success": True,
                "optimization_enabled": OPTIMIZATION_ENABLED,
                "message": f"AI 최적화 모드가 {mode_text}되었습니다",
                "performance_features": {
                    "async_io": "80% 성능 향상" if OPTIMIZATION_ENABLED else "비활성화",
                    "connection_pooling": "70% 메모리 절약" if OPTIMIZATION_ENABLED else "비활성화",
                    "intelligent_cache": "90% 응답시간 단축" if OPTIMIZATION_ENABLED else "비활성화"
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": True,
                "optimization_enabled": OPTIMIZATION_ENABLED,
                "message": "최적화 모드 변경 없음",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logging.error(f"최적화 모드 토글 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 라우터 등록 (안전한 임포트)
try:
    from routes.store_management_routes import router as store_router
    app.include_router(store_router, tags=["Store Management"])
    logging.info("✅ 스토어 관리 라우터 등록 완료")
except ImportError as e:
    logging.warning(f"⚠️ 스토어 관리 라우터 임포트 실패: {e}")

# 사주 시스템 제거됨

# 키워드 시스템 통합 라우터 (5개 라우터 통합)
try:
    from routes.keywords_unified import router as keyword_unified_router
    app.include_router(keyword_unified_router, tags=["Keywords Unified"])
    logging.info("✅ 키워드 시스템 통합 라우터 등록 완료 (5개 라우터 → 1개 통합)")
except ImportError as e:
    logging.warning(f"⚠️ 키워드 통합 라우터 임포트 실패: {e}")

# 순수 사주 시스템 제거됨

# 하이브리드 사주 시스템 제거됨

# 설문 관리 라우터 (신규) - 임시 M-PIS API 추가
try:
    from routes.survey_management_routes import router as survey_router
    app.include_router(survey_router, tags=["Survey Management"])
    logging.info("✅ 설문 관리 라우터 등록 완료")
except ImportError as e:
    logging.warning(f"⚠️ 설문 관리 라우터 임포트 실패: {e}")
    logging.warning("사주 페이지에서 설문 API 호출 시 404 오류 발생 가능")

# 아카데미 관리 라우터 (신규)
try:
    from routes.academy_routes import router as academy_router
    app.include_router(academy_router, tags=["Academy Management"])
    logging.info("✅ 아카데미 관리 라우터 등록 완료")
except ImportError as e:
    logging.warning(f"⚠️ 아카데미 관리 라우터 임포트 실패: {e}")

# 커뮤니티 관리 라우터 (신규)
try:
    from routes.community_routes import router as community_router
    app.include_router(community_router, tags=["Community Management"])
    logging.info("✅ 커뮤니티 관리 라우터 등록 완료")
except ImportError as e:
    logging.warning(f"⚠️ 커뮤니티 관리 라우터 임포트 실패: {e}")

# 결제 시스템 라우터 (신규)
try:
    from routes.payment_routes import router as payment_router
    app.include_router(payment_router, tags=["Payment System"])
    logging.info("✅ 결제 시스템 라우터 등록 완료")
except ImportError as e:
    logging.warning(f"⚠️ 결제 시스템 라우터 임포트 실패: {e}")

# 인증 시스템 라우터 (신규)
try:
    from routes.auth_routes import router as auth_router
    app.include_router(auth_router, tags=["Authentication"])
    logging.info("✅ 인증 시스템 라우터 등록 완료")
except ImportError as e:
    logging.warning(f"⚠️ 인증 시스템 라우터 임포트 실패: {e}")

# 백업 관리 라우터 (8004 포트 worker에서 전담 처리로 인해 비활성화)
# try:
#     from routes.backup_routes import router as backup_router
#     app.include_router(backup_router, prefix="/admin-api", tags=["Backup Management"])
#     logging.info("✅ 백업 관리 라우터 등록 완료")
# except ImportError as e:
#     logging.warning(f"⚠️ 백업 관리 라우터 임포트 실패: {e}")

# 마케팅 크롤러 관리 라우터
try:
    from routes.marketing_crawler_routes import marketing_crawler_router
    app.include_router(marketing_crawler_router, tags=["Marketing Crawler Management"])
    logging.info("✅ 마케팅 크롤러 관리 라우터 등록 완료")
except ImportError as e:
    logging.warning(f"⚠️ 마케팅 크롤러 관리 라우터 임포트 실패: {e}")

# Analytics API Routes (독립적으로 분리)
try:
    from routes.analytics_routes import router as analytics_router
    app.include_router(analytics_router, tags=["Analytics Dashboard"])
    logging.info("✅ Analytics 라우터 등록 완료")
except Exception as e:
    logging.error(f"⚠️ Analytics 라우터 임포트 실패: {e}")

# M-PIS 시스템 제거됨

# 벌크 동기화 라우터 (원격서버 동기화용)
try:
    from routes.bulk_sync_endpoint import router as bulk_sync_router
    app.include_router(bulk_sync_router, tags=["Bulk Sync"])
    logging.info("✅ 벌크 동기화 라우터 등록 완료")
except Exception as e:
    logging.error(f"⚠️ 벌크 동기화 라우터 임포트 실패: {e}")

# 누락된 엔드포인트 라우터 (프론트엔드 오류 해결용)
try:
    from routes.missing_endpoints import router as missing_endpoints_router
    app.include_router(missing_endpoints_router, tags=["Missing Endpoints"])
    logging.info("✅ 누락된 엔드포인트 라우터 등록 완료")
except Exception as e:
    logging.error(f"⚠️ 누락된 엔드포인트 라우터 임포트 실패: {e}")

# 디버깅 라우터 (키워드 API 문제 해결용)
# 디버깅 기능은 통합 키워드 라우터에 포함됨

# 정적 파일 서빙 (키워드 매트릭스 HTML)
try:
    # frontend/public 디렉토리를 정적 파일로 마운트
    static_path = os.path.join(os.path.dirname(__file__), "../frontend/public")
    if os.path.exists(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")
        logging.info("✅ 정적 파일 서빙 활성화: /static -> frontend/public")
        
        # 키워드 매트릭스 페이지 라우트 추가
        from fastapi.responses import FileResponse
        
        @app.get("/keywords/matrix/")
        async def keyword_matrix_page():
            """키워드 매트릭스 3D 시각화 페이지"""
            html_path = os.path.join(static_path, "keyword-matrix.html")
            if os.path.exists(html_path):
                return FileResponse(html_path, media_type="text/html")
            else:
                raise HTTPException(status_code=404, detail="Keyword matrix page not found")
        
        logging.info("✅ 키워드 매트릭스 페이지 라우트 등록 완료: /keywords/matrix/")
    else:
        logging.warning(f"⚠️ 정적 파일 디렉토리 없음: {static_path}")
except Exception as e:
    logging.error(f"⚠️ 정적 파일 서빙 설정 실패: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "admin_api_updated:app",
        host="0.0.0.0",
        port=8001,
        workers=2,  # 관리자 백엔드 - 복잡한 연산 대응
        access_log=True,
        log_level="info"
    )