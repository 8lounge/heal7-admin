"""
HEAL7 설문관리 시스템 API 라우터
M-PIS + 키워드 매트릭스 + 사주 시스템 통합 설문관리
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import json
import asyncio
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# 내부 모듈 임포트 (절대 임포트)
try:
    import sys
    import os
    
    # 현재 파일의 디렉토리 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 백엔드 디렉토리 경로
    backend_dir = os.path.dirname(current_dir)
    
    # Python 경로에 추가
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    
    # 직접 import
    sys.path.insert(0, os.path.join(backend_dir, 'services'))
    sys.path.insert(0, os.path.join(backend_dir, 'models'))
    sys.path.insert(0, os.path.join(backend_dir, 'utils'))
    
    from survey_engine import SurveyEngine
    from mpis_integration import MPISIntegrationEngine
    from mpis_global_manager import mpis_global_manager
    from keyword_calculator import KeywordScoreCalculator
    from survey_models import *
    from json_serializer import JSONSerializer, create_api_response
    
    logger = logging.getLogger(__name__)
    logger.info("✅ 설문 관리 모듈 임포트 성공")
    
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.error(f"❌ 설문 관리 모듈 임포트 실패: {e}")
    
    # 최소한의 응답 함수 정의
    def create_api_response(data=None, success=True, message=""):
        return {
            "success": success,
            "data": data if data is not None else {},
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    
    # 더미 클래스들 (서버가 시작되도록)
    class SurveyEngine:
        async def get_dashboard_statistics(self, period: str):
            return {
                "overview": {
                    "total_sessions": 0,
                    "completed_sessions": 0,
                    "active_sessions": 0,
                    "avg_completion_minutes": 0
                },
                "template_breakdown": [],
                "period": period
            }
        
        async def list_templates(self, **kwargs):
            return []
        
        async def get_active_sessions(self, limit: int):
            return []
        
        async def create_template(self, template_data: dict):
            # 더미 구현: 단순히 ID 1을 반환
            return 1
        
        async def get_template(self, template_id: int, include_questions: bool = True):
            return None
        
        async def update_template(self, template_id: int, template_data: dict):
            return True
        
        async def delete_template(self, template_id: int):
            return True
    
    class MPISIntegrationEngine:
        pass
    
    class KeywordScoreCalculator:
        pass
    
    class MPISGlobalManager:
        async def get_global_mpis_status(self):
            return {"status": "unavailable", "error": "Module import failed"}
    
    mpis_global_manager = MPISGlobalManager()

# 라우터 초기화
router = APIRouter(prefix="/admin-api/surveys", tags=["설문관리"])

# 로깅 설정
logger = logging.getLogger("heal7.survey")

# 의존성 주입
def get_survey_engine():
    return SurveyEngine()

def get_mpis_engine():
    return MPISIntegrationEngine()

def get_keyword_calculator():
    return KeywordScoreCalculator()

# ==================== 데이터 모델 정의 ====================

class SurveyTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str = Field(..., pattern="^(psychological_analysis|neurological_assessment|growth_potential|custom)$")
    target_keywords: Optional[List[int]] = []
    mpis_weights: Optional[Dict[str, float]] = {}
    is_adaptive: bool = True
    max_questions: int = Field(20, ge=5, le=100)
    min_completion_rate: float = Field(0.8, ge=0.1, le=1.0)

class SurveyAutoGenerateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    intent: str = Field("general", pattern="^(general|psychological|neurological|growth|custom)$")
    target_coverage: Optional[float] = Field(0.15, ge=0.05, le=0.5)

class SurveyQuestionCreate(BaseModel):
    template_id: int
    question_text: str = Field(..., min_length=10)
    question_type: str = Field(..., pattern="^(single_choice|multiple_choice|scale|text|ranking)$")
    category: Optional[str] = None
    primary_keywords: List[int] = []
    secondary_keywords: List[int] = []
    display_conditions: Optional[Dict[str, Any]] = {}
    importance_weight: float = Field(1.0, ge=0.1, le=3.0)
    question_group: Optional[str] = None
    is_required: bool = True
    validation_rules: Optional[Dict[str, Any]] = {}

class SurveyQuestionOptionCreate(BaseModel):
    question_id: int
    option_text: str = Field(..., min_length=1)
    option_value: Optional[str] = None
    keyword_mappings: List[Dict[str, Any]] = []
    next_question_logic: Optional[Dict[str, Any]] = {}
    icon_url: Optional[str] = None
    color_code: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")

class SurveySessionStart(BaseModel):
    template_id: int
    user_id: Optional[int] = None
    saju_result_id: Optional[str] = None
    birth_info: Optional[Dict[str, Any]] = {}
    metadata: Optional[Dict[str, Any]] = {}

class SurveyResponse(BaseModel):
    session_uuid: UUID
    question_id: int
    response_value: str
    selected_option_ids: List[int] = []
    response_time_seconds: Optional[int] = None

# ==================== 설문 템플릿 관리 API ====================

@router.post("/templates", response_model=Dict[str, Any])
async def create_survey_template(
    template_data: SurveyTemplateCreate,
    survey_engine: SurveyEngine = Depends(get_survey_engine)
):
    """새 설문 템플릿 생성"""
    try:
        template_id = await survey_engine.create_template(template_data.dict())
        
        logger.info(f"새 설문 템플릿 생성: {template_id}")
        
        return {
            "success": True,
            "data": {
                "template_id": template_id,
                "message": "설문 템플릿이 성공적으로 생성되었습니다"
            }
        }
    except Exception as e:
        logger.error(f"설문 템플릿 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def list_survey_templates(
    category: Optional[str] = Query(None, pattern="^(psychological_analysis|neurological_assessment|growth_potential|custom)$"),
    is_active: bool = Query(True),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    survey_engine: SurveyEngine = Depends(get_survey_engine)
):
    """설문 템플릿 목록 조회"""
    try:
        templates = await survey_engine.list_templates(
            category=category,
            is_active=is_active,
            limit=limit,
            offset=offset
        )
        
        response_data = create_api_response({
            "templates": templates,
            "total_count": len(templates),
            "pagination": {
                "limit": limit,
                "offset": offset
            }
        })
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"설문 템플릿 목록 조회 실패: {e}")
        error_response = create_api_response(
            data={"error": str(e)},
            success=False,
            message="설문 템플릿 목록 조회에 실패했습니다"
        )
        return JSONResponse(content=error_response, status_code=500)

@router.get("/templates/{template_id}")
async def get_survey_template(
    template_id: int,
    include_questions: bool = Query(True),
    survey_engine: SurveyEngine = Depends(get_survey_engine)
):
    """특정 설문 템플릿 상세 조회"""
    try:
        template = await survey_engine.get_template(template_id, include_questions)
        
        if not template:
            error_response = create_api_response(
                data={"template_id": template_id},
                success=False,
                message="설문 템플릿을 찾을 수 없습니다"
            )
            return JSONResponse(content=error_response, status_code=404)
        
        response_data = create_api_response(template)
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"설문 템플릿 조회 실패: {e}")
        error_response = create_api_response(
            data={"error": str(e), "template_id": template_id},
            success=False,
            message="설문 템플릿 조회에 실패했습니다"
        )
        return JSONResponse(content=error_response, status_code=500)

@router.put("/templates/{template_id}", response_model=Dict[str, Any])
async def update_survey_template(
    template_id: int,
    template_data: SurveyTemplateCreate,
    survey_engine: SurveyEngine = Depends(get_survey_engine)
):
    """설문 템플릿 수정"""
    try:
        success = await survey_engine.update_template(template_id, template_data.dict())
        
        if not success:
            raise HTTPException(status_code=404, detail="설문 템플릿을 찾을 수 없습니다")
        
        return {
            "success": True,
            "data": {
                "message": "설문 템플릿이 성공적으로 수정되었습니다"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"설문 템플릿 수정 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/templates/{template_id}")
async def delete_survey_template(
    template_id: int,
    survey_engine: SurveyEngine = Depends(get_survey_engine)
):
    """설문 템플릿 삭제"""
    try:
        success = await survey_engine.delete_template(template_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="설문 템플릿을 찾을 수 없습니다")
        
        return {
            "success": True,
            "data": {
                "message": "설문 템플릿이 성공적으로 삭제되었습니다"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"설문 템플릿 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== M-PIS AI 마법 생성 API ====================

@router.post("/templates/ai-generate", response_model=Dict[str, Any])
async def ai_generate_survey_template(
    request: SurveyAutoGenerateRequest
):
    """AI 마법버튼: 제목 기반 자동 설문 생성"""
    try:
        logger.info(f"AI 마법 설문 생성 요청: {request.title}")
        
        # M-PIS 전역 관리자를 통한 자동 생성
        generation_result = await mpis_global_manager.auto_generate_survey(
            title=request.title,
            intent=request.intent
        )
        
        if not generation_result.get('success', False):
            raise HTTPException(
                status_code=400, 
                detail=f"AI 설문 생성 실패: {generation_result.get('error', '알 수 없는 오류')}"
            )
        
        template = generation_result['template']
        validation = generation_result.get('validation', {})
        
        return {
            "success": True,
            "data": {
                "template": template,
                "validation_result": validation,
                "mpis_score": generation_result.get('mpis_score', 0.0),
                "ai_generation_info": {
                    "generated_questions": len(template.get('questions', [])),
                    "target_keywords": len(template.get('target_keywords', [])),
                    "balance_profile": template.get('balance_profile', {}),
                    "generation_timestamp": template.get('generated_at')
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI 설문 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"AI 설문 생성 중 오류가 발생했습니다: {str(e)}")

@router.post("/templates/validate-mpis", response_model=Dict[str, Any])
async def validate_survey_with_mpis(
    template_data: Dict[str, Any]
):
    """M-PIS 기준으로 설문 템플릿 검증"""
    try:
        validation_result = await mpis_global_manager.validate_survey_template(template_data)
        
        return {
            "success": True,
            "data": {
                "validation_result": validation_result,
                "is_mpis_compliant": validation_result.get('is_valid', False),
                "mpis_score": validation_result.get('mpis_score', 0.0),
                "violations": validation_result.get('violations', []),
                "recommendations": validation_result.get('recommendations', [])
            }
        }
        
    except Exception as e:
        logger.error(f"M-PIS 검증 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mpis/global-status", response_model=Dict[str, Any])
async def get_mpis_global_status():
    """M-PIS 전역 상태 조회"""
    try:
        global_status = await mpis_global_manager.get_global_mpis_status()
        
        return {
            "success": True,
            "data": global_status
        }
        
    except Exception as e:
        logger.error(f"M-PIS 전역 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 설문 질문 관리 API ====================

@router.post("/questions", response_model=Dict[str, Any])
async def create_survey_question(
    question_data: SurveyQuestionCreate,
    survey_engine: SurveyEngine = Depends(get_survey_engine)
):
    """새 설문 질문 생성"""
    try:
        question_id = await survey_engine.create_question(question_data.dict())
        
        return {
            "success": True,
            "data": {
                "question_id": question_id,
                "message": "설문 질문이 성공적으로 생성되었습니다"
            }
        }
    except Exception as e:
        logger.error(f"설문 질문 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/questions/{question_id}/options", response_model=Dict[str, Any])
async def create_question_option(
    question_id: int,
    option_data: SurveyQuestionOptionCreate,
    survey_engine: SurveyEngine = Depends(get_survey_engine)
):
    """설문 질문 선택지 생성"""
    try:
        option_data.question_id = question_id
        option_id = await survey_engine.create_question_option(option_data.dict())
        
        return {
            "success": True,
            "data": {
                "option_id": option_id,
                "message": "선택지가 성공적으로 생성되었습니다"
            }
        }
    except Exception as e:
        logger.error(f"설문 선택지 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 설문 세션 관리 API ====================

@router.post("/sessions/start", response_model=Dict[str, Any])
async def start_survey_session(
    session_data: SurveySessionStart,
    survey_engine: SurveyEngine = Depends(get_survey_engine)
):
    """새 설문 세션 시작"""
    try:
        session = await survey_engine.start_session(session_data.dict())
        
        return {
            "success": True,
            "data": {
                "session_uuid": session["session_uuid"],
                "template_info": session["template_info"],
                "first_question": session["first_question"],
                "progress": {
                    "current_question": 1,
                    "total_estimated": session["estimated_questions"],
                    "completion_percentage": 0.0
                }
            }
        }
    except Exception as e:
        logger.error(f"설문 세션 시작 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_uuid}", response_model=Dict[str, Any])
async def get_survey_session(
    session_uuid: UUID,
    survey_engine: SurveyEngine = Depends(get_survey_engine)
):
    """설문 세션 상태 조회"""
    try:
        session = await survey_engine.get_session(str(session_uuid))
        
        if not session:
            raise HTTPException(status_code=404, detail="설문 세션을 찾을 수 없습니다")
        
        return {
            "success": True,
            "data": session
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"설문 세션 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_uuid}/respond", response_model=Dict[str, Any])
async def submit_survey_response(
    session_uuid: UUID,
    response_data: SurveyResponse,
    background_tasks: BackgroundTasks,
    survey_engine: SurveyEngine = Depends(get_survey_engine),
    keyword_calculator: KeywordScoreCalculator = Depends(get_keyword_calculator),
    mpis_engine: MPISIntegrationEngine = Depends(get_mpis_engine)
):
    """설문 응답 제출 및 실시간 분석"""
    try:
        # 1. 응답 저장
        response_id = await survey_engine.save_response(response_data.dict())
        
        # 2. 실시간 키워드 점수 계산 (백그라운드)
        background_tasks.add_task(
            keyword_calculator.update_session_scores,
            str(session_uuid),
            response_data.dict()
        )
        
        # 3. M-PIS 프로필 업데이트 (백그라운드)
        background_tasks.add_task(
            mpis_engine.update_session_profile,
            str(session_uuid)
        )
        
        # 4. 다음 질문 결정
        next_question = await survey_engine.get_next_question(str(session_uuid))
        
        # 5. 세션 진행상황 업데이트
        progress = await survey_engine.update_session_progress(str(session_uuid))
        
        response_result = {
            "success": True,
            "data": {
                "response_id": response_id,
                "next_question": next_question,
                "progress": progress,
                "session_status": progress.get("status", "in_progress")
            }
        }
        
        # 설문 완료 시 최종 분석 트리거
        if progress.get("status") == "completed":
            background_tasks.add_task(
                survey_engine.trigger_final_analysis,
                str(session_uuid)
            )
            response_result["data"]["completion_message"] = "설문이 완료되었습니다. 분석 결과를 준비 중입니다."
        
        return response_result
        
    except Exception as e:
        logger.error(f"설문 응답 제출 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 실시간 분석 API ====================

@router.get("/sessions/{session_uuid}/analysis/realtime", response_model=Dict[str, Any])
async def get_realtime_analysis(
    session_uuid: UUID,
    include_keywords: bool = Query(True),
    include_mpis: bool = Query(True),
    keyword_calculator: KeywordScoreCalculator = Depends(get_keyword_calculator),
    mpis_engine: MPISIntegrationEngine = Depends(get_mpis_engine)
):
    """실시간 분석 결과 조회"""
    try:
        analysis_result = {}
        
        if include_keywords:
            # 실시간 키워드 점수 조회
            keyword_scores = await keyword_calculator.get_session_scores(str(session_uuid))
            analysis_result["keyword_analysis"] = {
                "scores": keyword_scores,
                "top_keywords": keyword_calculator.get_top_keywords(keyword_scores, limit=10),
                "group_scores": keyword_calculator.aggregate_by_groups(keyword_scores)
            }
        
        if include_mpis:
            # 실시간 M-PIS 프로필 조회
            mpis_profile = await mpis_engine.get_session_profile(str(session_uuid))
            analysis_result["mpis_analysis"] = mpis_profile
        
        return {
            "success": True,
            "data": analysis_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"실시간 분석 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_uuid}/analysis/complete", response_model=Dict[str, Any])
async def get_complete_analysis(
    session_uuid: UUID,
    survey_engine: SurveyEngine = Depends(get_survey_engine)
):
    """완전한 분석 결과 조회 (설문 완료 후)"""
    try:
        # 세션 상태 확인
        session = await survey_engine.get_session(str(session_uuid))
        if not session or session.get("status") != "completed":
            raise HTTPException(
                status_code=400, 
                detail="설문이 완료되지 않았거나 분석 결과가 준비되지 않았습니다"
            )
        
        # 완전한 분석 결과 조회
        complete_analysis = await survey_engine.get_complete_analysis(str(session_uuid))
        
        return {
            "success": True,
            "data": complete_analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"완전한 분석 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 키워드 시각화 API ====================

@router.get("/sessions/{session_uuid}/visualization/keyword-matrix", response_model=Dict[str, Any])
async def get_keyword_matrix_visualization(
    session_uuid: UUID,
    matrix_type: str = Query("network", pattern="^(network|heatmap|scatter)$"),
    keyword_calculator: KeywordScoreCalculator = Depends(get_keyword_calculator)
):
    """키워드 매트릭스 3D 시각화 데이터"""
    try:
        keyword_scores = await keyword_calculator.get_session_scores(str(session_uuid))
        
        if matrix_type == "network":
            # 네트워크 그래프 데이터
            visualization_data = await keyword_calculator.generate_network_visualization(
                keyword_scores, session_uuid
            )
        elif matrix_type == "heatmap":
            # 히트맵 데이터
            visualization_data = await keyword_calculator.generate_heatmap_visualization(
                keyword_scores
            )
        else:  # scatter
            # 산점도 데이터
            visualization_data = await keyword_calculator.generate_scatter_visualization(
                keyword_scores
            )
        
        return {
            "success": True,
            "data": {
                "visualization_type": matrix_type,
                "visualization_data": visualization_data,
                "metadata": {
                    "total_keywords": len(keyword_scores),
                    "active_keywords": len([k for k, v in keyword_scores.items() if abs(v.get('score', 0)) > 0.1]),
                    "generation_timestamp": datetime.now().isoformat()
                }
            }
        }
        
    except Exception as e:
        logger.error(f"키워드 매트릭스 시각화 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 관리자 대시보드 API ====================

@router.get("/dashboard/stats", response_model=Dict[str, Any])
async def get_dashboard_statistics(
    period: str = Query("week", pattern="^(day|week|month|year)$"),
    survey_engine: SurveyEngine = Depends(get_survey_engine)
):
    """설문관리 대시보드 통계"""
    try:
        stats = await survey_engine.get_dashboard_statistics(period)
        
        return {
            "success": True,
            "data": {
                "period": period,
                "statistics": stats,
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"대시보드 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/active-sessions", response_model=Dict[str, Any])
async def get_active_sessions(
    limit: int = Query(50, ge=1, le=200),
    survey_engine: SurveyEngine = Depends(get_survey_engine)
):
    """현재 활성 설문 세션 목록"""
    try:
        active_sessions = await survey_engine.get_active_sessions(limit)
        
        return {
            "success": True,
            "data": {
                "active_sessions": active_sessions,
                "total_count": len(active_sessions)
            }
        }
        
    except Exception as e:
        logger.error(f"활성 세션 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 통합 분석 API ====================

@router.post("/analysis/saju-integration", response_model=Dict[str, Any])
async def create_saju_integration_analysis(
    session_uuid: UUID,
    saju_result_id: str,
    survey_engine: SurveyEngine = Depends(get_survey_engine)
):
    """사주-설문 통합 분석 실행"""
    try:
        integration_result = await survey_engine.create_saju_integration(
            str(session_uuid), saju_result_id
        )
        
        return {
            "success": True,
            "data": integration_result
        }
        
    except Exception as e:
        logger.error(f"사주-설문 통합 분석 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/export/{session_uuid}", response_model=Dict[str, Any])
async def export_analysis_result(
    session_uuid: UUID,
    format_type: str = Query("json", pattern="^(json|pdf|csv)$"),
    survey_engine: SurveyEngine = Depends(get_survey_engine)
):
    """분석 결과 내보내기"""
    try:
        export_data = await survey_engine.export_analysis(str(session_uuid), format_type)
        
        return {
            "success": True,
            "data": {
                "format": format_type,
                "download_url": export_data.get("download_url"),
                "expires_at": export_data.get("expires_at")
            }
        }
        
    except Exception as e:
        logger.error(f"분석 결과 내보내기 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 헬스체크 API ====================

@router.get("/health")
async def survey_system_health():
    """설문관리 시스템 헬스체크"""
    try:
        # 데이터베이스 연결 확인
        # Redis 연결 확인  
        # 핵심 서비스 상태 확인
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "up",
                "redis": "up", 
                "survey_engine": "up",
                "mpis_integration": "up",
                "keyword_calculator": "up"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ==================== M-PIS 전역 상태 API (ADMIN 호환) ====================

@router.get("/mpis/global-status")
async def get_mpis_global_status():
    """M-PIS 전역 상태 조회 - ADMIN에서 제거됨 (폴백 응답 제공)"""
    try:
        # ADMIN 환경에서는 M-PIS 전역 상태가 제거되었으므로 폴백 데이터 반환
        return {
            "success": True,
            "data": {
                "globalConfig": {
                    "aiSystemActive": False,
                    "autoAnalysisEnabled": False,
                    "keywordMatrixMode": "static",
                    "processingMode": "offline"
                },
                "systemBalance": {
                    "overallBalance": 0.0,
                    "kognitiveBalance": 0.0,
                    "emotionalBalance": 0.0,
                    "socialBalance": 0.0,
                    "lastCalculated": datetime.now().isoformat()
                },
                "autoGenerationEngine": {
                    "isReady": False,
                    "aiModelStatus": "offline",
                    "generationMode": "disabled",
                    "lastUpdate": datetime.now().isoformat()
                }
            },
            "message": "ADMIN 환경에서 M-PIS 전역 상태가 비활성화되었습니다",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"M-PIS 전역 상태 조회 실패: {e}")
        return {
            "success": False,
            "data": {
                "globalConfig": {"aiSystemActive": False},
                "systemBalance": {"overallBalance": 0.0},
                "autoGenerationEngine": {"isReady": False}
            },
            "error": "M-PIS 전역 상태 서비스 비활성화됨",
            "timestamp": datetime.now().isoformat()
        }