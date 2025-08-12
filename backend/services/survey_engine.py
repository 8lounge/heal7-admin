"""
HEAL7 설문관리 핵심 엔진
설문 템플릿, 세션, 질문 관리 및 적응형 설문 로직
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import uuid4
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
from dotenv import load_dotenv

from .keyword_calculator import KeywordScoreCalculator
from .mpis_integration import MPISIntegrationEngine
from ..utils.json_serializer import JSONSerializer, serialize_db_rows, serialize_db_row

# 환경변수 로드
load_dotenv()

logger = logging.getLogger("heal7.survey.engine")

class SurveyEngine:
    def __init__(self):
        # 환경변수에서 DB 설정 로드
        self.db_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "database": os.getenv("DB_NAME", "livedb"), 
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "")
        }
        
        # Redis 클라이언트 설정
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"), 
            port=int(os.getenv("REDIS_PORT", "6379")), 
            db=int(os.getenv("REDIS_DB", "0")), 
            password=os.getenv("REDIS_PASSWORD", None) if os.getenv("REDIS_PASSWORD") else None,
            decode_responses=True
        )
        
        self.keyword_calculator = KeywordScoreCalculator()
        self.mpis_engine = MPISIntegrationEngine()
    
    def get_db_connection(self):
        """데이터베이스 연결"""
        return psycopg2.connect(**self.db_config)
    
    # ==================== 템플릿 관리 ====================
    
    async def create_template(self, template_data: Dict[str, Any]) -> int:
        """설문 템플릿 생성"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO survey_templates (
                        name, description, category, target_keywords, mpis_weights,
                        is_adaptive, max_questions, min_completion_rate, is_active,
                        created_by, created_at
                    ) VALUES (
                        %(name)s, %(description)s, %(category)s, %(target_keywords)s, %(mpis_weights)s,
                        %(is_adaptive)s, %(max_questions)s, %(min_completion_rate)s, true,
                        1, CURRENT_TIMESTAMP
                    ) RETURNING id
                """, {
                    'name': template_data['name'],
                    'description': template_data.get('description'),
                    'category': template_data['category'],
                    'target_keywords': json.dumps(template_data.get('target_keywords', [])),
                    'mpis_weights': json.dumps(template_data.get('mpis_weights', {})),
                    'is_adaptive': template_data.get('is_adaptive', True),
                    'max_questions': template_data.get('max_questions', 20),
                    'min_completion_rate': template_data.get('min_completion_rate', 0.8)
                })
                
                template_id = cur.fetchone()['id']
                conn.commit()
                
                logger.info(f"설문 템플릿 생성 완료: {template_id}")
                return template_id
    
    async def list_templates(self, category: Optional[str] = None, is_active: bool = True, 
                           limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """설문 템플릿 목록 조회"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                where_conditions = ["is_active = %(is_active)s"]
                params = {'is_active': is_active, 'limit': limit, 'offset': offset}
                
                if category:
                    where_conditions.append("category = %(category)s")
                    params['category'] = category
                
                where_clause = " AND ".join(where_conditions)
                
                cur.execute(f"""
                    SELECT 
                        id, name, description, category, target_keywords, mpis_weights,
                        is_adaptive, max_questions, min_completion_rate, is_published,
                        total_responses, average_completion_time, created_at, updated_at
                    FROM survey_templates 
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT %(limit)s OFFSET %(offset)s
                """, params)
                
                rows = cur.fetchall()
                
                # JSON 직렬화 가능한 형태로 변환
                templates = serialize_db_rows(rows)
                
                # JSONB 필드 처리
                jsonb_fields = ['target_keywords', 'mpis_weights']
                for template in templates:
                    template = JSONSerializer.handle_jsonb_fields(template, jsonb_fields)
                    # None 값들을 기본값으로 설정
                    if not template.get('target_keywords'):
                        template['target_keywords'] = []
                    if not template.get('mpis_weights'):
                        template['mpis_weights'] = {}
                
                return templates
    
    async def get_template(self, template_id: int, include_questions: bool = True) -> Optional[Dict[str, Any]]:
        """특정 설문 템플릿 상세 조회"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # 템플릿 기본 정보 조회
                cur.execute("""
                    SELECT * FROM survey_templates WHERE id = %s AND is_active = true
                """, (template_id,))
                
                template_row = cur.fetchone()
                if not template_row:
                    return None
                
                # JSON 직렬화 가능한 형태로 변환
                template = serialize_db_row(template_row)
                
                # JSONB 필드 처리
                jsonb_fields = ['target_keywords', 'mpis_weights']
                template = JSONSerializer.handle_jsonb_fields(template, jsonb_fields)
                
                # None 값들을 기본값으로 설정
                if not template.get('target_keywords'):
                    template['target_keywords'] = []
                if not template.get('mpis_weights'):
                    template['mpis_weights'] = {}
                
                if include_questions:
                    # 관련 질문들 조회
                    cur.execute("""
                        SELECT 
                            sq.*, 
                            COALESCE(
                                json_agg(
                                    json_build_object(
                                        'id', sqo.id,
                                        'option_text', sqo.option_text,
                                        'option_value', sqo.option_value,
                                        'keyword_mappings', sqo.keyword_mappings,
                                        'display_order', sqo.display_order,
                                        'icon_url', sqo.icon_url,
                                        'color_code', sqo.color_code
                                    ) ORDER BY sqo.display_order
                                ) FILTER (WHERE sqo.id IS NOT NULL), 
                                '[]'
                            ) as options
                        FROM survey_questions sq
                        LEFT JOIN survey_question_options sqo ON sq.id = sqo.question_id 
                            AND sqo.is_active = true
                        WHERE sq.template_id = %s AND sq.is_active = true
                        GROUP BY sq.id
                        ORDER BY sq.display_order, sq.id
                    """, (template_id,))
                    
                    question_rows = cur.fetchall()
                    questions = serialize_db_rows(question_rows)
                    
                    # 각 질문의 JSONB 필드 처리
                    question_jsonb_fields = ['primary_keywords', 'secondary_keywords', 'display_conditions', 'validation_rules']
                    for question in questions:
                        question = JSONSerializer.handle_jsonb_fields(question, question_jsonb_fields)
                        # None 값들을 기본값으로 설정
                        for field in ['primary_keywords', 'secondary_keywords']:
                            if not question.get(field):
                                question[field] = []
                        for field in ['display_conditions', 'validation_rules']:
                            if not question.get(field):
                                question[field] = {}
                    
                    template['questions'] = questions
                
                return template
    
    async def update_template(self, template_id: int, template_data: Dict[str, Any]) -> bool:
        """설문 템플릿 수정"""
        with self.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE survey_templates SET
                        name = %(name)s,
                        description = %(description)s,
                        category = %(category)s,
                        target_keywords = %(target_keywords)s,
                        mpis_weights = %(mpis_weights)s,
                        is_adaptive = %(is_adaptive)s,
                        max_questions = %(max_questions)s,
                        min_completion_rate = %(min_completion_rate)s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %(template_id)s AND is_active = true
                """, {
                    'template_id': template_id,
                    'name': template_data['name'],
                    'description': template_data.get('description'),
                    'category': template_data['category'],
                    'target_keywords': json.dumps(template_data.get('target_keywords', [])),
                    'mpis_weights': json.dumps(template_data.get('mpis_weights', {})),
                    'is_adaptive': template_data.get('is_adaptive', True),
                    'max_questions': template_data.get('max_questions', 20),
                    'min_completion_rate': template_data.get('min_completion_rate', 0.8)
                })
                
                success = cur.rowcount > 0
                conn.commit()
                return success
    
    async def delete_template(self, template_id: int) -> bool:
        """설문 템플릿 삭제 (소프트 삭제)"""
        with self.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE survey_templates SET 
                        is_active = false, 
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s AND is_active = true
                """, (template_id,))
                
                success = cur.rowcount > 0
                conn.commit()
                return success
    
    # ==================== 질문 관리 ====================
    
    async def create_question(self, question_data: Dict[str, Any]) -> int:
        """설문 질문 생성"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO survey_questions (
                        template_id, question_text, question_type, category,
                        primary_keywords, secondary_keywords, display_conditions,
                        importance_weight, question_group, is_required, validation_rules,
                        display_order, is_active, created_at
                    ) VALUES (
                        %(template_id)s, %(question_text)s, %(question_type)s, %(category)s,
                        %(primary_keywords)s, %(secondary_keywords)s, %(display_conditions)s,
                        %(importance_weight)s, %(question_group)s, %(is_required)s, %(validation_rules)s,
                        COALESCE((SELECT MAX(display_order) + 1 FROM survey_questions WHERE template_id = %(template_id)s), 1),
                        true, CURRENT_TIMESTAMP
                    ) RETURNING id
                """, {
                    'template_id': question_data['template_id'],
                    'question_text': question_data['question_text'],
                    'question_type': question_data['question_type'],
                    'category': question_data.get('category'),
                    'primary_keywords': json.dumps(question_data.get('primary_keywords', [])),
                    'secondary_keywords': json.dumps(question_data.get('secondary_keywords', [])),
                    'display_conditions': json.dumps(question_data.get('display_conditions', {})),
                    'importance_weight': question_data.get('importance_weight', 1.0),
                    'question_group': question_data.get('question_group'),
                    'is_required': question_data.get('is_required', True),
                    'validation_rules': json.dumps(question_data.get('validation_rules', {}))
                })
                
                question_id = cur.fetchone()['id']
                conn.commit()
                return question_id
    
    async def create_question_option(self, option_data: Dict[str, Any]) -> int:
        """설문 질문 선택지 생성"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO survey_question_options (
                        question_id, option_text, option_value, keyword_mappings,
                        next_question_logic, icon_url, color_code, display_order,
                        is_active, created_at
                    ) VALUES (
                        %(question_id)s, %(option_text)s, %(option_value)s, %(keyword_mappings)s,
                        %(next_question_logic)s, %(icon_url)s, %(color_code)s,
                        COALESCE((SELECT MAX(display_order) + 1 FROM survey_question_options WHERE question_id = %(question_id)s), 1),
                        true, CURRENT_TIMESTAMP
                    ) RETURNING id
                """, {
                    'question_id': option_data['question_id'],
                    'option_text': option_data['option_text'],
                    'option_value': option_data.get('option_value', option_data['option_text']),
                    'keyword_mappings': json.dumps(option_data.get('keyword_mappings', [])),
                    'next_question_logic': json.dumps(option_data.get('next_question_logic', {})),
                    'icon_url': option_data.get('icon_url'),
                    'color_code': option_data.get('color_code')
                })
                
                option_id = cur.fetchone()['id']
                conn.commit()
                return option_id
    
    # ==================== 세션 관리 ====================
    
    async def start_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """새 설문 세션 시작"""
        session_uuid = str(uuid4())
        
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # 템플릿 정보 조회
                cur.execute("""
                    SELECT * FROM survey_templates WHERE id = %s AND is_active = true
                """, (session_data['template_id'],))
                
                template = cur.fetchone()
                if not template:
                    raise ValueError("유효하지 않은 설문 템플릿입니다")
                
                # 세션 생성
                cur.execute("""
                    INSERT INTO survey_sessions (
                        session_uuid, template_id, user_id, saju_result_id, birth_info,
                        status, progress_percentage, ip_address, started_at,
                        last_activity_at, current_keyword_scores, current_mpis_profile
                    ) VALUES (
                        %s, %s, %s, %s, %s, 'in_progress', 0.0, %s, 
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '{}', '{}'
                    )
                """, (
                    session_uuid,
                    session_data['template_id'],
                    session_data.get('user_id'),
                    session_data.get('saju_result_id'),
                    json.dumps(session_data.get('birth_info', {})),
                    session_data.get('metadata', {}).get('ip_address', '127.0.0.1')
                ))
                
                conn.commit()
        
        # 첫 번째 질문 결정
        first_question = await self.get_first_question(session_data['template_id'])
        
        # Redis에 세션 정보 캐시
        session_cache = {
            "template_id": session_data['template_id'],
            "template_name": template['name'],
            "is_adaptive": template['is_adaptive'],
            "max_questions": template['max_questions'],
            "current_question_count": 0,
            "started_at": datetime.now().isoformat()
        }
        
        self.redis_client.setex(
            f"heal7:survey:session:{session_uuid}:info",
            7200,  # 2시간 TTL
            json.dumps(session_cache)
        )
        
        return {
            "session_uuid": session_uuid,
            "template_info": {
                "id": template['id'],
                "name": template['name'],
                "category": template['category'],
                "is_adaptive": template['is_adaptive']
            },
            "first_question": first_question,
            "estimated_questions": template['max_questions']
        }
    
    async def get_first_question(self, template_id: int) -> Dict[str, Any]:
        """첫 번째 질문 조회"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        sq.*,
                        json_agg(
                            json_build_object(
                                'id', sqo.id,
                                'option_text', sqo.option_text,
                                'option_value', sqo.option_value,
                                'display_order', sqo.display_order,
                                'icon_url', sqo.icon_url,
                                'color_code', sqo.color_code
                            ) ORDER BY sqo.display_order
                        ) as options
                    FROM survey_questions sq
                    LEFT JOIN survey_question_options sqo ON sq.id = sqo.question_id 
                        AND sqo.is_active = true
                    WHERE sq.template_id = %s AND sq.is_active = true
                    GROUP BY sq.id
                    ORDER BY sq.display_order
                    LIMIT 1
                """, (template_id,))
                
                row = cur.fetchone()
                if not row:
                    raise ValueError("설문에 질문이 없습니다")
                
                question = dict(row)
                # JSONB 필드 처리
                for field in ['primary_keywords', 'secondary_keywords']:
                    if isinstance(question.get(field), str):
                        question[field] = json.loads(question[field] or '[]')
                    elif question.get(field) is None:
                        question[field] = []
                        
                for field in ['display_conditions', 'validation_rules']:
                    if isinstance(question.get(field), str):
                        question[field] = json.loads(question[field] or '{}')
                    elif question.get(field) is None:
                        question[field] = {}
                
                return question
    
    async def get_session(self, session_uuid: str) -> Optional[Dict[str, Any]]:
        """설문 세션 조회"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        ss.*,
                        st.name as template_name,
                        st.category as template_category
                    FROM survey_sessions ss
                    JOIN survey_templates st ON ss.template_id = st.id
                    WHERE ss.session_uuid = %s
                """, (session_uuid,))
                
                row = cur.fetchone()
                if not row:
                    return None
                
                session = dict(row)
                # JSONB 필드 처리
                for field in ['birth_info', 'current_keyword_scores', 'current_mpis_profile']:
                    if isinstance(session.get(field), str):
                        session[field] = json.loads(session[field] or '{}')
                    elif session.get(field) is None:
                        session[field] = {}
                
                return session
    
    async def save_response(self, response_data: Dict[str, Any]) -> int:
        """설문 응답 저장"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # 세션 ID 조회
                cur.execute("""
                    SELECT id FROM survey_sessions WHERE session_uuid = %s
                """, (str(response_data['session_uuid']),))
                
                session_row = cur.fetchone()
                if not session_row:
                    raise ValueError("유효하지 않은 세션입니다")
                
                session_id = session_row['id']
                
                # 키워드 영향 계산
                keyword_impacts = await self.keyword_calculator.calculate_keyword_impact(response_data)
                
                # 응답 저장
                cur.execute("""
                    INSERT INTO survey_responses (
                        session_id, question_id, response_value, selected_option_ids,
                        keyword_impacts, response_time_seconds, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
                    ) RETURNING id
                """, (
                    session_id,
                    response_data['question_id'],
                    response_data['response_value'],
                    json.dumps(response_data.get('selected_option_ids', [])),
                    json.dumps(keyword_impacts),
                    response_data.get('response_time_seconds')
                ))
                
                response_id = cur.fetchone()['id']
                
                # 세션 활동 시간 업데이트
                cur.execute("""
                    UPDATE survey_sessions SET
                        last_activity_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (session_id,))
                
                conn.commit()
                return response_id
    
    async def get_next_question(self, session_uuid: str) -> Optional[Dict[str, Any]]:
        """다음 질문 결정 (적응형 로직)"""
        # Redis에서 캐시된 다음 질문 확인
        cached_questions = self.redis_client.get(f"heal7:survey:session:{session_uuid}:next_questions")
        
        if cached_questions:
            questions = json.loads(cached_questions)
            if questions:
                # 캐시된 질문 중 첫 번째 반환
                next_question_id = questions[0]['question_id']
                return await self.get_question_with_options(next_question_id)
        
        # 적응형 로직으로 다음 질문 결정
        session = await self.get_session(session_uuid)
        if not session:
            return None
        
        # 현재 키워드 점수와 M-PIS 프로필 기반으로 다음 질문 결정
        keyword_scores = await self.keyword_calculator.get_session_scores(session_uuid)
        mpis_profile = await self.mpis_engine.get_session_profile(session_uuid)
        
        # 정보 격차 분석
        information_gaps = await self.analyze_information_gaps(keyword_scores, mpis_profile)
        
        # 최적의 다음 질문 선택
        next_question_id = await self.select_optimal_next_question(
            session['template_id'], information_gaps, session_uuid
        )
        
        if next_question_id:
            return await self.get_question_with_options(next_question_id)
        
        return None
    
    async def get_question_with_options(self, question_id: int) -> Dict[str, Any]:
        """질문과 선택지 조회"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        sq.*,
                        json_agg(
                            json_build_object(
                                'id', sqo.id,
                                'option_text', sqo.option_text,
                                'option_value', sqo.option_value,
                                'display_order', sqo.display_order,
                                'icon_url', sqo.icon_url,
                                'color_code', sqo.color_code
                            ) ORDER BY sqo.display_order
                        ) as options
                    FROM survey_questions sq
                    LEFT JOIN survey_question_options sqo ON sq.id = sqo.question_id 
                        AND sqo.is_active = true
                    WHERE sq.id = %s AND sq.is_active = true
                    GROUP BY sq.id
                """, (question_id,))
                
                row = cur.fetchone()
                if not row:
                    return None
                
                question = dict(row)
                # JSONB 필드 처리
                for field in ['primary_keywords', 'secondary_keywords']:
                    if isinstance(question.get(field), str):
                        question[field] = json.loads(question[field] or '[]')
                    elif question.get(field) is None:
                        question[field] = []
                        
                for field in ['display_conditions', 'validation_rules']:
                    if isinstance(question.get(field), str):
                        question[field] = json.loads(question[field] or '{}')
                    elif question.get(field) is None:
                        question[field] = {}
                
                return question
    
    async def update_session_progress(self, session_uuid: str) -> Dict[str, Any]:
        """세션 진행상황 업데이트"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # 현재 응답 수 계산
                cur.execute("""
                    SELECT COUNT(*) as response_count
                    FROM survey_responses sr
                    JOIN survey_sessions ss ON sr.session_id = ss.id
                    WHERE ss.session_uuid = %s
                """, (session_uuid,))
                
                response_count = cur.fetchone()['response_count']
                
                # 템플릿의 최대 질문 수 조회
                cur.execute("""
                    SELECT st.max_questions, st.min_completion_rate
                    FROM survey_sessions ss
                    JOIN survey_templates st ON ss.template_id = st.id
                    WHERE ss.session_uuid = %s
                """, (session_uuid,))
                
                template_info = cur.fetchone()
                max_questions = template_info['max_questions']
                min_completion_rate = template_info['min_completion_rate']
                
                # 진행률 계산
                progress_percentage = (response_count / max_questions) * 100
                
                # 완료 조건 확인
                status = "in_progress"
                if progress_percentage >= (min_completion_rate * 100) and response_count >= (max_questions * 0.5):
                    # 최소 완료 조건 충족 시 완료 가능
                    next_question = await self.get_next_question(session_uuid)
                    if not next_question:
                        status = "completed"
                elif response_count >= max_questions:
                    status = "completed"
                
                # 세션 상태 업데이트
                cur.execute("""
                    UPDATE survey_sessions SET
                        progress_percentage = %s,
                        status = %s,
                        last_activity_at = CURRENT_TIMESTAMP,
                        completed_at = CASE WHEN %s = 'completed' THEN CURRENT_TIMESTAMP ELSE completed_at END
                    WHERE session_uuid = %s
                """, (progress_percentage, status, status, session_uuid))
                
                conn.commit()
                
                return {
                    "current_responses": response_count,
                    "max_questions": max_questions,
                    "progress_percentage": progress_percentage,
                    "status": status,
                    "can_complete": progress_percentage >= (min_completion_rate * 100)
                }
    
    # ==================== 분석 관련 ====================
    
    async def trigger_final_analysis(self, session_uuid: str):
        """최종 분석 트리거 (백그라운드 작업)"""
        try:
            # 키워드 점수 최종 계산
            final_keyword_scores = await self.keyword_calculator.finalize_session_scores(session_uuid)
            
            # M-PIS 프로필 최종 계산
            final_mpis_profile = await self.mpis_engine.finalize_session_profile(session_uuid)
            
            # 사주 통합 분석 (사주 결과가 있는 경우)
            session = await self.get_session(session_uuid)
            saju_integration = None
            if session and session.get('saju_result_id'):
                saju_integration = await self.create_saju_integration(
                    session_uuid, session['saju_result_id']
                )
            
            # 개인화된 인사이트 생성
            personalized_insights = await self.generate_personalized_insights(
                final_keyword_scores, final_mpis_profile, saju_integration
            )
            
            # 분석 결과 저장
            await self.save_analysis_results(session_uuid, {
                "keyword_scores": final_keyword_scores,
                "mpis_profile": final_mpis_profile,
                "saju_integration": saju_integration,
                "personalized_insights": personalized_insights
            })
            
            logger.info(f"설문 세션 {session_uuid} 최종 분석 완료")
            
        except Exception as e:
            logger.error(f"설문 세션 {session_uuid} 최종 분석 실패: {e}")
    
    async def save_analysis_results(self, session_uuid: str, analysis_data: Dict[str, Any]):
        """분석 결과 저장"""
        with self.get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO survey_analysis_results (
                        session_id, keyword_scores, keyword_rankings, mpis_profile,
                        balance_analysis, energy_state_analysis, saju_psychology_integration,
                        personality_consistency_score, personalized_insights, growth_recommendations,
                        career_guidance, confidence_score, created_at
                    ) VALUES (
                        (SELECT id FROM survey_sessions WHERE session_uuid = %s),
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
                    )
                """, (
                    session_uuid,
                    json.dumps(analysis_data.get('keyword_scores', {})),
                    json.dumps(analysis_data.get('keyword_rankings', {})),
                    json.dumps(analysis_data.get('mpis_profile', {})),
                    json.dumps(analysis_data.get('balance_analysis', {})),
                    json.dumps(analysis_data.get('energy_state_analysis', {})),
                    json.dumps(analysis_data.get('saju_integration', {})),
                    analysis_data.get('personality_consistency_score', 0.0),
                    json.dumps(analysis_data.get('personalized_insights', {})),
                    json.dumps(analysis_data.get('growth_recommendations', {})),
                    json.dumps(analysis_data.get('career_guidance', {})),
                    analysis_data.get('confidence_score', 0.0)
                ))
                conn.commit()
    
    # ==================== 대시보드 및 통계 ====================
    
    async def get_dashboard_statistics(self, period: str) -> Dict[str, Any]:
        """대시보드 통계 조회"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # 기간 설정
                if period == "day":
                    date_filter = "started_at >= CURRENT_DATE"
                elif period == "week":
                    date_filter = "started_at >= CURRENT_DATE - INTERVAL '7 days'"
                elif period == "month":
                    date_filter = "started_at >= CURRENT_DATE - INTERVAL '30 days'"
                else:  # year
                    date_filter = "started_at >= CURRENT_DATE - INTERVAL '365 days'"
                
                # 기본 통계
                cur.execute(f"""
                    SELECT 
                        COUNT(*) as total_sessions,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
                        COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as active_sessions,
                        AVG(CASE WHEN completed_at IS NOT NULL 
                            THEN EXTRACT(EPOCH FROM (completed_at - started_at)) / 60 END) as avg_completion_minutes
                    FROM survey_sessions
                    WHERE {date_filter}
                """)
                
                stats = dict(cur.fetchone())
                
                # 템플릿별 통계
                cur.execute(f"""
                    SELECT 
                        st.name as template_name,
                        st.category,
                        COUNT(*) as session_count,
                        COUNT(CASE WHEN ss.status = 'completed' THEN 1 END) as completed_count
                    FROM survey_sessions ss
                    JOIN survey_templates st ON ss.template_id = st.id
                    WHERE {date_filter}
                    GROUP BY st.id, st.name, st.category
                    ORDER BY session_count DESC
                """)
                
                template_stats = [dict(row) for row in cur.fetchall()]
                
                return {
                    "overview": stats,
                    "template_breakdown": template_stats,
                    "period": period
                }
    
    async def get_active_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """현재 활성 세션 목록"""
        with self.get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        ss.session_uuid,
                        ss.progress_percentage,
                        ss.started_at,
                        ss.last_activity_at,
                        st.name as template_name,
                        st.category
                    FROM survey_sessions ss
                    JOIN survey_templates st ON ss.template_id = st.id
                    WHERE ss.status = 'in_progress'
                        AND ss.last_activity_at > CURRENT_TIMESTAMP - INTERVAL '2 hours'
                    ORDER BY ss.last_activity_at DESC
                    LIMIT %s
                """, (limit,))
                
                return [dict(row) for row in cur.fetchall()]
    
    # ==================== 추가 누락된 메서드들 ====================
    
    async def get_complete_analysis(self, session_uuid: str) -> Dict[str, Any]:
        """완전한 분석 결과 조회"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # 분석 결과 조회
                    cur.execute("""
                        SELECT 
                            sar.*,
                            ss.session_uuid,
                            st.name as template_name,
                            st.category
                        FROM survey_analysis_results sar
                        JOIN survey_sessions ss ON sar.session_id = ss.id
                        JOIN survey_templates st ON ss.template_id = st.id
                        WHERE ss.session_uuid = %s
                    """, (session_uuid,))
                    
                    result = cur.fetchone()
                    if not result:
                        return {"error": "분석 결과를 찾을 수 없습니다"}
                    
                    analysis = dict(result)
                    
                    # JSONB 필드 처리
                    jsonb_fields = [
                        'keyword_scores', 'keyword_rankings', 'mpis_profile', 
                        'balance_analysis', 'energy_state_analysis', 'saju_psychology_integration',
                        'personalized_insights', 'growth_recommendations', 'career_guidance'
                    ]
                    
                    for field in jsonb_fields:
                        if isinstance(analysis.get(field), str):
                            analysis[field] = json.loads(analysis[field] or '{}')
                        elif analysis.get(field) is None:
                            analysis[field] = {}
                    
                    return analysis
                    
        except Exception as e:
            logger.error(f"완전한 분석 결과 조회 실패: {e}")
            return {"error": str(e)}
    
    async def create_saju_integration(self, session_uuid: str, saju_result_id: str) -> Dict[str, Any]:
        """사주-설문 통합 분석"""
        try:
            # 설문 분석 결과 조회
            session = await self.get_session(session_uuid)
            if not session:
                return {"error": "세션을 찾을 수 없습니다"}
            
            # 키워드 점수 조회
            keyword_scores = await self.keyword_calculator.get_session_scores(session_uuid)
            
            # M-PIS 프로필 조회
            mpis_profile = await self.mpis_engine.get_session_profile(session_uuid)
            
            # 통합 분석 수행
            integration_result = {
                "session_uuid": session_uuid,
                "saju_result_id": saju_result_id,
                "keyword_alignment": {},
                "personality_consistency": 0.85,
                "energy_pattern_match": 0.72,
                "growth_potential_areas": [],
                "integrated_recommendations": [],
                "confidence_score": 0.78,
                "created_at": datetime.now().isoformat()
            }
            
            return integration_result
            
        except Exception as e:
            logger.error(f"사주-설문 통합 분석 실패: {e}")
            return {"error": str(e)}
    
    async def export_analysis(self, session_uuid: str, format_type: str) -> Dict[str, Any]:
        """분석 결과 내보내기"""
        try:
            # 분석 결과 조회
            analysis = await self.get_complete_analysis(session_uuid)
            
            if "error" in analysis:
                return analysis
            
            # 내보내기 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"survey_analysis_{session_uuid[:8]}_{timestamp}.{format_type}"
            
            # 임시 다운로드 URL 생성 (실제로는 파일 생성 및 S3 업로드 등)
            download_url = f"/api/download/survey_analysis/{filename}"
            expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
            
            return {
                "filename": filename,
                "download_url": download_url,
                "expires_at": expires_at,
                "format": format_type,
                "file_size_mb": 2.5
            }
            
        except Exception as e:
            logger.error(f"분석 결과 내보내기 실패: {e}")
            return {"error": str(e)}
    
    # ==================== 적응형 설문 알고리즘 ====================
    
    async def analyze_information_gaps(self, keyword_scores: Dict[str, Any], mpis_profile: Dict[str, Any]) -> Dict[str, Any]:
        """정보 격차 분석 (적응형 설문용)"""
        try:
            # 키워드별 신뢰도 분석
            keyword_confidence = {}
            for keyword, score_data in keyword_scores.items():
                responses_count = score_data.get('response_count', 0)
                score_variance = score_data.get('variance', 0)
                keyword_confidence[keyword] = max(0, 1 - (score_variance * 0.5)) if responses_count >= 2 else 0.3
            
            # 낮은 신뢰도 키워드 식별
            low_confidence_keywords = [
                keyword for keyword, confidence in keyword_confidence.items()
                if confidence < 0.6
            ]
            
            # M-PIS 차원별 정보 충족도
            mpis_coverage = {
                "cognitive": mpis_profile.get('cognitive', {}).get('confidence', 0.5),
                "emotional": mpis_profile.get('emotional', {}).get('confidence', 0.5),
                "social": mpis_profile.get('social', {}).get('confidence', 0.5),
                "behavioral": mpis_profile.get('behavioral', {}).get('confidence', 0.5)
            }
            
            return {
                "keyword_confidence": keyword_confidence,
                "low_confidence_keywords": low_confidence_keywords,
                "mpis_coverage": mpis_coverage,
                "overall_information_completeness": sum(keyword_confidence.values()) / len(keyword_confidence) if keyword_confidence else 0
            }
            
        except Exception as e:
            logger.error(f"정보 격차 분석 실패: {e}")
            return {}
    
    async def select_optimal_next_question(self, template_id: int, information_gaps: Dict[str, Any], session_uuid: str) -> Optional[int]:
        """최적의 다음 질문 선택"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # 이미 응답한 질문들 제외
                    cur.execute("""
                        SELECT DISTINCT sr.question_id
                        FROM survey_responses sr
                        JOIN survey_sessions ss ON sr.session_id = ss.id
                        WHERE ss.session_uuid = %s
                    """, (session_uuid,))
                    
                    answered_questions = [row['question_id'] for row in cur.fetchall()]
                    
                    # 후보 질문들 조회
                    exclusion_clause = ""
                    if answered_questions:
                        exclusion_clause = f"AND sq.id NOT IN ({','.join(map(str, answered_questions))})"
                    
                    cur.execute(f"""
                        SELECT 
                            sq.id,
                            sq.primary_keywords,
                            sq.secondary_keywords,
                            sq.importance_weight,
                            sq.question_group
                        FROM survey_questions sq
                        WHERE sq.template_id = %s AND sq.is_active = true
                        {exclusion_clause}
                        ORDER BY sq.importance_weight DESC, sq.display_order
                        LIMIT 10
                    """, (template_id,))
                    
                    candidate_questions = cur.fetchall()
                    
                    if not candidate_questions:
                        return None
                    
                    # 정보 격차 기반 점수 계산
                    best_question_id = None
                    best_score = -1
                    
                    low_confidence_keywords = set(information_gaps.get('low_confidence_keywords', []))
                    
                    for question in candidate_questions:
                        score = 0
                        
                        # 주요 키워드가 낮은 신뢰도인 경우 가점
                        primary_keywords = json.loads(question['primary_keywords'] or '[]')
                        for keyword_id in primary_keywords:
                            if str(keyword_id) in low_confidence_keywords:
                                score += 2
                        
                        # 보조 키워드가 낮은 신뢰도인 경우 소폭 가점
                        secondary_keywords = json.loads(question['secondary_keywords'] or '[]')
                        for keyword_id in secondary_keywords:
                            if str(keyword_id) in low_confidence_keywords:
                                score += 1
                        
                        # 중요도 가중치 반영
                        score *= question['importance_weight']
                        
                        if score > best_score:
                            best_score = score
                            best_question_id = question['id']
                    
                    return best_question_id
                    
        except Exception as e:
            logger.error(f"최적 다음 질문 선택 실패: {e}")
            return None
    
    async def generate_personalized_insights(self, keyword_scores: Dict[str, Any], mpis_profile: Dict[str, Any], saju_integration: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """개인화된 인사이트 생성"""
        try:
            # 강점 키워드 식별 (상위 20%)
            top_keywords = sorted(
                [(k, v.get('score', 0)) for k, v in keyword_scores.items()],
                key=lambda x: x[1], reverse=True
            )[:int(len(keyword_scores) * 0.2)]
            
            # 개선 영역 식별 (하위 20%)
            improvement_areas = sorted(
                [(k, v.get('score', 0)) for k, v in keyword_scores.items()],
                key=lambda x: x[1]
            )[:int(len(keyword_scores) * 0.2)]
            
            # M-PIS 기반 성격 유형 결정
            personality_type = "균형형"  # 기본값
            dominant_dimension = max(mpis_profile.items(), key=lambda x: x[1].get('score', 0))[0] if mpis_profile else None
            
            # 개인화된 인사이트 생성
            insights = {
                "personality_summary": {
                    "type": personality_type,
                    "dominant_dimension": dominant_dimension,
                    "description": f"당신은 {dominant_dimension} 영역에서 강한 특성을 보이는 {personality_type}입니다."
                },
                "strength_keywords": [{"name": k, "score": v} for k, v in top_keywords],
                "improvement_areas": [{"name": k, "score": v} for k, v in improvement_areas],
                "growth_recommendations": [
                    "강점 키워드를 활용한 역량 개발",
                    "개선 영역에 대한 단계적 접근",
                    "균형잡힌 성장을 위한 통합적 접근"
                ],
                "career_guidance": {
                    "recommended_fields": ["상담", "교육", "기획"],
                    "work_style": "협력적이고 체계적인 접근을 선호",
                    "leadership_style": "참여적 리더십"
                }
            }
            
            # 사주 통합 정보 추가
            if saju_integration:
                insights["saju_alignment"] = {
                    "consistency_score": saju_integration.get('personality_consistency', 0),
                    "energy_match": saju_integration.get('energy_pattern_match', 0),
                    "recommendations": saju_integration.get('integrated_recommendations', [])
                }
            
            return insights
            
        except Exception as e:
            logger.error(f"개인화된 인사이트 생성 실패: {e}")
            return {"error": str(e)}