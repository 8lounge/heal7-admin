"""
HEAL7 키워드 점수 계산기
설문 응답 기반 실시간 키워드 점수 계산 및 관리
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import redis
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger("heal7.keyword.calculator")

class KeywordScoreCalculator:
    def __init__(self):
        self.db_config = {
            "host": "localhost",
            "database": "devdb", 
            "user": "devuser",
            "password": "devpass"
        }
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
    def get_db_connection(self):
        """데이터베이스 연결"""
        return psycopg2.connect(**self.db_config)
    
    async def calculate_keyword_impact(self, response_data: dict) -> dict:
        """단일 응답의 키워드 영향 계산"""
        
        keyword_impacts = {}
        
        try:
            # 1. 선택된 옵션들의 키워드 매핑 정보 수집
            for option_id in response_data.get('selected_option_ids', []):
                option_mappings = await self.get_option_keyword_mappings(option_id)
                
                for mapping in option_mappings:
                    keyword_id = mapping['keyword_id']
                    base_impact = mapping['score_impact']  # 0.0 ~ 1.0
                    impact_type = mapping['impact_type']   # 'positive', 'negative', 'neutral'
                    
                    # 2. 질문별 가중치 적용
                    question_weight = await self.get_question_importance_weight(
                        response_data['question_id']
                    )
                    
                    # 3. 응답 신뢰도 적용
                    confidence_factor = self.calculate_response_confidence(response_data)
                    
                    # 4. 최종 키워드 영향 점수 계산
                    final_impact = base_impact * question_weight * confidence_factor
                    
                    # 5. 영향 유형에 따른 부호 결정
                    if impact_type == 'negative':
                        final_impact = -final_impact
                    elif impact_type == 'neutral':
                        final_impact = final_impact * 0.5
                    
                    keyword_impacts[keyword_id] = {
                        'impact_score': final_impact,
                        'confidence': confidence_factor,
                        'source_question': response_data['question_id'],
                        'impact_type': impact_type
                    }
            
            return keyword_impacts
            
        except Exception as e:
            logger.error(f"키워드 영향 계산 실패: {e}")
            return {}
    
    async def get_option_keyword_mappings(self, option_id: int) -> List[Dict]:
        """옵션의 키워드 매핑 정보 조회"""
        
        # 임시 구현 - 실제로는 survey_question_options 테이블에서 조회
        return [
            {
                'keyword_id': 1,
                'score_impact': 0.8,
                'impact_type': 'positive'
            }
        ]
    
    async def get_question_importance_weight(self, question_id: int) -> float:
        """질문의 중요도 가중치 조회"""
        
        # 임시 구현 - 실제로는 survey_questions 테이블에서 조회
        return 1.0
    
    def calculate_response_confidence(self, response_data: dict) -> float:
        """응답 신뢰도 계산"""
        
        confidence = 1.0
        
        # 응답 시간 기반 신뢰도 조정
        response_time = response_data.get('response_time_seconds', 10)
        if response_time < 2:  # 너무 빠른 응답
            confidence *= 0.7
        elif response_time > 120:  # 너무 느린 응답
            confidence *= 0.8
            
        return max(0.1, min(1.0, confidence))
    
    async def update_session_scores(self, session_uuid: str, response_data: dict):
        """세션의 키워드 점수 업데이트 (백그라운드 작업)"""
        
        try:
            # 키워드 영향 계산
            keyword_impacts = await self.calculate_keyword_impact(response_data)
            
            # Redis에 누적 점수 업데이트
            current_scores = self.redis_client.hgetall(
                f"heal7:survey:session:{session_uuid}:keywords"
            )
            
            updated_scores = {}
            
            for keyword_id, impact_data in keyword_impacts.items():
                current_score = float(current_scores.get(f"keyword_{keyword_id}", 0.0))
                impact_score = impact_data['impact_score']
                
                # 누적 점수 계산 (가중 평균 방식)
                if current_score == 0.0:
                    new_score = impact_score
                else:
                    weight_decay = 0.9  # 기존 점수 가중치
                    new_score = (current_score * weight_decay) + (impact_score * (1 - weight_decay))
                
                # 점수 범위 정규화 (-1.0 ~ 1.0)
                new_score = max(-1.0, min(1.0, new_score))
                
                updated_scores[f"keyword_{keyword_id}"] = json.dumps({
                    'score': new_score,
                    'confidence': impact_data['confidence'],
                    'last_updated': datetime.now().isoformat(),
                    'update_count': int(current_scores.get(f"keyword_{keyword_id}_count", 0)) + 1
                })
            
            # Redis 업데이트
            if updated_scores:
                self.redis_client.hmset(
                    f"heal7:survey:session:{session_uuid}:keywords",
                    updated_scores
                )
            
            logger.info(f"세션 {session_uuid} 키워드 점수 업데이트 완료")
            
        except Exception as e:
            logger.error(f"세션 키워드 점수 업데이트 실패: {e}")
    
    async def get_session_scores(self, session_uuid: str) -> dict:
        """세션의 현재 키워드 점수 조회"""
        
        try:
            scores_data = self.redis_client.hgetall(
                f"heal7:survey:session:{session_uuid}:keywords"
            )
            
            scores = {}
            for key, value in scores_data.items():
                if key.startswith('keyword_') and not key.endswith('_count'):
                    scores[key] = json.loads(value)
            
            return scores
            
        except Exception as e:
            logger.error(f"세션 키워드 점수 조회 실패: {e}")
            return {}
    
    async def finalize_session_scores(self, session_uuid: str) -> dict:
        """세션 완료 시 최종 키워드 점수 계산"""
        
        try:
            # 현재 점수 조회
            current_scores = await self.get_session_scores(session_uuid)
            
            # 최종 점수 계산 (추가 로직 적용 가능)
            final_scores = current_scores.copy()
            
            # 키워드 의존성 네트워크 전파 효과 적용
            final_scores = await self.apply_dependency_effects(final_scores)
            
            return final_scores
            
        except Exception as e:
            logger.error(f"최종 키워드 점수 계산 실패: {e}")
            return {}
    
    async def apply_dependency_effects(self, scores: dict) -> dict:
        """키워드 의존성 네트워크 효과 적용"""
        
        # 임시 구현 - 실제로는 keyword_dependencies 테이블 활용
        return scores
    
    def get_top_keywords(self, keyword_scores: dict, limit: int = 10) -> List[Dict]:
        """상위 키워드 추출"""
        
        scored_keywords = []
        for keyword_id, data in keyword_scores.items():
            if isinstance(data, dict) and 'score' in data:
                scored_keywords.append({
                    'keyword_id': keyword_id,
                    'score': data['score'],
                    'confidence': data.get('confidence', 0.0)
                })
        
        # 점수 순 정렬
        scored_keywords.sort(key=lambda x: abs(x['score']), reverse=True)
        
        return scored_keywords[:limit]
    
    def aggregate_by_groups(self, keyword_scores: dict) -> dict:
        """키워드 점수를 A/B/C 그룹별로 집계"""
        
        # 임시 구현 - 실제로는 keywords 테이블과 연동
        group_scores = {
            "A": {"positive": 0.0, "negative": 0.0, "count": 0},
            "B": {"positive": 0.0, "negative": 0.0, "count": 0}, 
            "C": {"positive": 0.0, "negative": 0.0, "count": 0}
        }
        
        return group_scores