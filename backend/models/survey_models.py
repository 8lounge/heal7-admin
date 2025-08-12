"""
HEAL7 설문관리 시스템 데이터 모델
Pydantic 모델 정의
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from uuid import UUID
from enum import Enum

# 열거형 정의
class SurveyCategoryType(str, Enum):
    mpis = "mpis"
    saju_psychology = "saju_psychology"
    custom = "custom"

class QuestionType(str, Enum):
    single_choice = "single_choice"
    multiple_choice = "multiple_choice"
    scale = "scale"
    text = "text"
    ranking = "ranking"

class SessionStatus(str, Enum):
    in_progress = "in_progress"
    completed = "completed"
    abandoned = "abandoned"
    expired = "expired"

# 기본 응답 모델
class BaseResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    timestamp: Optional[datetime] = None

# 설문 템플릿 관련 모델
class SurveyTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: SurveyCategoryType
    target_keywords: Optional[List[int]] = []
    mpis_weights: Optional[Dict[str, float]] = {}
    is_adaptive: bool = True
    max_questions: int = Field(20, ge=5, le=100)
    min_completion_rate: float = Field(0.8, ge=0.1, le=1.0)

class SurveyTemplateCreate(SurveyTemplateBase):
    pass

class SurveyTemplateUpdate(SurveyTemplateBase):
    pass

class SurveyTemplate(SurveyTemplateBase):
    id: int
    version: str = "1.0"
    is_active: bool = True
    is_published: bool = False
    total_responses: int = 0
    average_completion_time: int = 0
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 설문 질문 관련 모델
class SurveyQuestionBase(BaseModel):
    template_id: int
    question_text: str = Field(..., min_length=10)
    question_type: QuestionType
    category: Optional[str] = None
    primary_keywords: List[int] = []
    secondary_keywords: List[int] = []
    display_conditions: Optional[Dict[str, Any]] = {}
    importance_weight: float = Field(1.0, ge=0.1, le=3.0)
    question_group: Optional[str] = None
    is_required: bool = True
    validation_rules: Optional[Dict[str, Any]] = {}

class SurveyQuestionCreate(SurveyQuestionBase):
    pass

class SurveyQuestionUpdate(SurveyQuestionBase):
    pass

class SurveyQuestion(SurveyQuestionBase):
    id: int
    display_order: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    options: Optional[List['SurveyQuestionOption']] = []
    
    class Config:
        from_attributes = True

# 설문 질문 선택지 관련 모델
class SurveyQuestionOptionBase(BaseModel):
    question_id: int
    option_text: str = Field(..., min_length=1)
    option_value: Optional[str] = None
    keyword_mappings: List[Dict[str, Any]] = []
    next_question_logic: Optional[Dict[str, Any]] = {}
    icon_url: Optional[str] = None
    color_code: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")

class SurveyQuestionOptionCreate(SurveyQuestionOptionBase):
    pass

class SurveyQuestionOptionUpdate(SurveyQuestionOptionBase):
    pass

class SurveyQuestionOption(SurveyQuestionOptionBase):
    id: int
    display_order: int = 0
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True

# 설문 세션 관련 모델
class SurveySessionBase(BaseModel):
    template_id: int
    user_id: Optional[int] = None
    saju_result_id: Optional[str] = None
    birth_info: Optional[Dict[str, Any]] = {}
    metadata: Optional[Dict[str, Any]] = {}

class SurveySessionStart(SurveySessionBase):
    pass

class SurveySession(SurveySessionBase):
    id: int
    session_uuid: UUID
    status: SessionStatus = SessionStatus.in_progress
    progress_percentage: float = 0.0
    current_question_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    last_activity_at: datetime
    estimated_completion_time: Optional[int] = None
    current_keyword_scores: Optional[Dict[str, Any]] = {}
    current_mpis_profile: Optional[Dict[str, Any]] = {}
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 설문 응답 관련 모델
class SurveyResponseBase(BaseModel):
    session_uuid: UUID
    question_id: int
    response_value: str
    selected_option_ids: List[int] = []
    response_time_seconds: Optional[int] = None

class SurveyResponseCreate(SurveyResponseBase):
    pass

class SurveyResponse(SurveyResponseBase):
    id: int
    session_id: int
    response_score: Optional[float] = None
    keyword_impacts: Optional[Dict[str, Any]] = {}
    confidence_level: float = 1.0
    revision_count: int = 0
    is_skipped: bool = False
    question_displayed_order: Optional[int] = None
    previous_responses_context: Optional[Dict[str, Any]] = {}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 설문 분석 결과 관련 모델
class SurveyAnalysisResultBase(BaseModel):
    session_id: int
    keyword_scores: Dict[str, Any]
    keyword_rankings: Optional[Dict[str, Any]] = {}
    mpis_profile: Dict[str, Any]
    balance_analysis: Optional[Dict[str, Any]] = {}
    energy_state_analysis: Optional[Dict[str, Any]] = {}
    saju_psychology_integration: Optional[Dict[str, Any]] = {}
    personality_consistency_score: Optional[float] = None
    personalized_insights: Optional[Dict[str, Any]] = {}
    growth_recommendations: Optional[Dict[str, Any]] = {}
    career_guidance: Optional[Dict[str, Any]] = {}
    confidence_score: Optional[float] = None

class SurveyAnalysisResult(SurveyAnalysisResultBase):
    id: int
    analysis_version: str = "1.0"
    analysis_duration_ms: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# API 응답 모델들
class TemplateResponse(BaseResponse):
    data: Optional[Union[SurveyTemplate, List[SurveyTemplate], Dict[str, Any]]] = None

class QuestionResponse(BaseResponse):
    data: Optional[Union[SurveyQuestion, List[SurveyQuestion], Dict[str, Any]]] = None

class SessionResponse(BaseResponse):
    data: Optional[Union[SurveySession, Dict[str, Any]]] = None

class ResponseSubmissionResponse(BaseResponse):
    data: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseResponse):
    data: Optional[Union[SurveyAnalysisResult, Dict[str, Any]]] = None

# 대시보드 및 통계 모델
class DashboardStats(BaseModel):
    total_sessions: int
    completed_sessions: int
    active_sessions: int
    average_completion_minutes: Optional[float] = None
    period: str
    template_breakdown: List[Dict[str, Any]] = []

class ActiveSession(BaseModel):
    session_uuid: UUID
    progress_percentage: float
    started_at: datetime
    last_activity_at: datetime
    template_name: str
    category: str

# 키워드 시각화 모델
class KeywordVisualization(BaseModel):
    visualization_type: str
    visualization_data: Dict[str, Any]
    metadata: Dict[str, Any]

# 실시간 분석 모델
class RealtimeAnalysis(BaseModel):
    keyword_analysis: Optional[Dict[str, Any]] = None
    mpis_analysis: Optional[Dict[str, Any]] = None
    timestamp: datetime

# 완전한 분석 결과 모델
class CompleteAnalysis(BaseModel):
    session_info: Dict[str, Any]
    keyword_analysis: Dict[str, Any]
    mpis_analysis: Dict[str, Any]
    saju_integration: Optional[Dict[str, Any]] = None
    personalized_insights: Dict[str, Any]
    growth_recommendations: Dict[str, Any]
    confidence_metrics: Dict[str, Any]

# Forward reference 해결
SurveyQuestion.model_rebuild()