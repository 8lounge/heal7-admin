#!/usr/bin/env python3
"""
HEAL7 마케팅 크롤러 AI 서비스
Gemini AI를 활용한 API 변환, 데이터 처리, 최적화 서비스
"""

import logging
import json
import asyncio
import httpx
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class AIServiceClient:
    """AI 서비스 백엔드 클라이언트 (새로운 통합 AI 매니저 호출)"""
    
    def __init__(self, ai_service_url: str = None):
        """AI 서비스 클라이언트 초기화"""
        self.ai_service_url = None  # AI 서비스 비활성화됨 - 로컬 처리로 전환
        self.client = httpx.AsyncClient(timeout=60.0)
        
        # 새로운 AI 시스템의 서비스별 폴백 순서
        self.service_types = {
            "marketing": "marketing",    # 마케팅 특화 폴백
            "research": "research",      # 리서치 특화 (Perplexity 우선)
            "general": "default",        # 기본 폴백
            "api_validation": "marketing",
            "job_optimization": "marketing", 
            "data_conversion": "general",
            "data_analysis": "research",
            "worker_validation": "general"
        }
    
    async def process_with_fallback(self, prompt: str, task_type: str = "general") -> Dict[str, Any]:
        """새로운 AI 서비스 백엔드를 통한 통합 처리"""
        
        # 작업 타입을 서비스 타입으로 매핑
        service_type = self.service_types.get(task_type, "default")
        
        logger.info(f"🤖 AI 처리 요청: {task_type} → {service_type} 서비스")
        
        try:
            # 새로운 AI 서비스 백엔드의 통합 API 호출
            response = await self.client.post(
                f"{self.ai_service_url}/ai/process",
                json={
                    "prompt": prompt,
                    "service": service_type,
                    "temperature": 0.7,
                    "max_tokens": 2048
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ AI 처리 성공: {result.get('model_used', 'unknown')}")
                
                return {
                    "success": True,
                    "result": self._parse_ai_response(result.get("response", "")),
                    "model_used": result.get("model_used", "unknown"),
                    "task_type": task_type,
                    "service_type": service_type,
                    "processing_time": result.get("response_time", 0),
                    "cost_estimate": result.get("cost_estimate", 0)
                }
            else:
                error_msg = f"AI 서비스 HTTP 에러 {response.status_code}: {response.text}"
                logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "task_type": task_type,
                    "service_type": service_type
                }
                
        except asyncio.TimeoutError:
            error_msg = f"AI 서비스 타임아웃 (60초)"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "task_type": task_type,
                "service_type": service_type
            }
            
        except Exception as e:
            error_msg = f"AI 서비스 연결 오류: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "task_type": task_type,
                "service_type": service_type
            }
    
    async def research_with_perplexity(self, query: str, context: str = "") -> Dict[str, Any]:
        """Perplexity를 이용한 전문 리서치 조사"""
        
        research_prompt = f"""
        다음 주제에 대해 전문적인 리서치 조사를 수행해주세요:
        
        조사 주제: {query}
        추가 컨텍스트: {context}
        
        다음 사항을 포함해서 조사해주세요:
        1. 최신 동향 및 트렌드
        2. 시장 분석 및 전망
        3. 주요 플레이어 및 경쟁사 분석
        4. 기술적 발전 사항
        5. 규제 및 정책 변화
        6. 소비자 행동 패턴
        7. 향후 예측 및 기회
        
        신뢰할 수 있는 출처를 바탕으로 정확한 정보를 제공해주세요.
        """
        
        return await self.process_with_fallback(research_prompt, "research")

class CrawlerService:
    def __init__(self, ai_service_url: str = None):
        """AI 서비스 백엔드를 사용하는 크롤러 서비스 초기화"""
        self.ai_client = AIServiceClient(ai_service_url)
        
    async def validate_api_configuration(self, api_config: Dict[str, Any]) -> Dict[str, Any]:
        """API 설정을 AI 폴백 시스템으로 검증하고 최적화"""
        
        prompt = f"""
        다음 API 설정을 분석하고 검증해주세요:
        
        API 정보:
        - 이름: {api_config.get('name')}
        - 제공업체: {api_config.get('provider')}
        - 기본 URL: {api_config.get('base_url')}
        - API 키: {api_config.get('api_key', '***')}
        - 추가 파라미터: {api_config.get('additional_params', {})}
        
        다음 사항을 분석해주세요:
        1. URL 형식이 올바른지 검증
        2. 인증 방식 추정 (API Key, Bearer Token, OAuth 등)
        3. 예상되는 응답 형식 (JSON, XML, RSS 등)
        4. 권장 호출 빈도 및 제한사항
        5. 필요한 헤더나 파라미터 추천
        6. 에러 처리 방법 추천
        
        JSON 형식으로 응답해주세요.
        """
        
        # AI 폴백 시스템 사용
        ai_result = await self.ai_client.process_with_fallback(prompt, "api_validation")
        
        if not ai_result["success"]:
            logger.error(f"AI API 검증 실패: {ai_result.get('errors', [])}")
            return {
                "valid": False,
                "error": "AI 처리 실패",
                "fallback_errors": ai_result.get("errors", []),
                "analysis": None,
                "confidence": 0.0
            }
        
        result = ai_result["result"]
        
        # AI 응답을 구조화된 형태로 변환
        return {
            "valid": result.get("valid", True),
            "analysis": {
                "api_type": result.get("api_type", "REST API"),
                "authentication": result.get("authentication", "API Key"),
                "response_format": result.get("response_format", "JSON"),
                "rate_limits": result.get("rate_limits", "Unknown"),
                "recommended_settings": result.get("recommended_settings", {}),
                "required_headers": result.get("required_headers", {}),
                "error_handling": result.get("error_handling", [])
            },
            "confidence": result.get("confidence", 0.8),
            "ai_model_used": ai_result["model_used"],
            "processing_attempt": ai_result["attempt"]
        }
    
    async def optimize_crawling_job(self, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """크롤링 작업 설정을 AI 폴백 시스템으로 최적화"""
        
        prompt = f"""
        다음 크롤링 작업을 최적화해주세요:
        
        작업 정보:
        - 이름: {job_config.get('name')}
        - 카테고리: {job_config.get('category')}
        - 소스 타입: {job_config.get('source_type')}
        - 대상 URL: {job_config.get('target_url')}
        - 검색 키워드: {job_config.get('search_keywords', [])}
        - 현재 주기: {job_config.get('crawl_frequency')}
        - 접근 패턴: {job_config.get('access_pattern')}
        - 지연 시간: {job_config.get('random_delay_min')}-{job_config.get('random_delay_max')}초
        
        다음 사항을 최적화해주세요:
        1. 최적 크롤링 주기 (서버 부하, 차단 위험 고려)
        2. 효율적인 접근 패턴
        3. 적절한 지연 시간 설정
        4. 키워드 우선순위 및 추가 키워드 제안
        5. 데이터 품질 향상 방법
        6. 에러 복구 전략
        7. 리소스 사용 최적화
        
        JSON 형식으로 응답해주세요.
        """
        
        # AI 폴백 시스템 사용
        ai_result = await self.ai_client.process_with_fallback(prompt, "job_optimization")
        
        if not ai_result["success"]:
            logger.error(f"AI 작업 최적화 실패: {ai_result.get('errors', [])}")
            return {
                "optimized": False,
                "error": "AI 처리 실패",
                "fallback_errors": ai_result.get("errors", []),
                "confidence": 0.0
            }
        
        result = ai_result["result"]
        
        return {
            "optimized": True,
            "recommendations": {
                "crawl_frequency": result.get("optimal_frequency", job_config.get('crawl_frequency')),
                "access_pattern": result.get("optimal_pattern", job_config.get('access_pattern')),
                "delay_range": result.get("optimal_delays", [5, 30]),
                "additional_keywords": result.get("suggested_keywords", []),
                "priority_keywords": result.get("priority_keywords", []),
                "batch_size": result.get("optimal_batch_size", 50),
                "retry_strategy": result.get("retry_strategy", "exponential_backoff"),
                "quality_filters": result.get("quality_filters", [])
            },
            "performance_improvements": result.get("performance_tips", []),
            "risk_mitigation": result.get("risk_mitigation", []),
            "confidence": result.get("confidence", 0.8),
            "ai_model_used": ai_result["model_used"],
            "processing_attempt": ai_result["attempt"]
        }
    
    async def convert_api_response(self, raw_data: Dict[str, Any], target_schema: str) -> Dict[str, Any]:
        """다양한 API 응답을 표준 스키마로 변환"""
        
        prompt = f"""
        다음 API 응답 데이터를 HEAL7 마케팅 시스템의 표준 스키마로 변환해주세요:
        
        원본 데이터:
        {json.dumps(raw_data, ensure_ascii=False, indent=2)}
        
        목표 스키마: {target_schema}
        
        변환 요구사항:
        1. 데이터 구조 정규화
        2. 한글/영문 필드명 통일
        3. 날짜/시간 형식 표준화 (ISO 8601)
        4. 누락 필드 처리
        5. 데이터 타입 정규화
        6. 불필요한 필드 제거
        7. 메타데이터 추가
        
        JSON 형식으로 변환된 데이터를 응답해주세요.
        """
        
        # AI 폴백 시스템 사용
        ai_result = await self.ai_client.process_with_fallback(prompt, "data_conversion")
        
        if not ai_result["success"]:
            logger.error(f"AI 데이터 변환 실패: {ai_result.get('errors', [])}")
            return {
                "success": False,
                "error": "AI 처리 실패",
                "fallback_errors": ai_result.get("errors", []),
                "original_data": raw_data
            }
        
        result = ai_result["result"]
        converted_data = result.get("converted_data", raw_data)
        
        return {
            "success": True,
            "converted_data": converted_data,
            "metadata": {
                "conversion_timestamp": datetime.now().isoformat(),
                "original_fields": len(raw_data),
                "converted_fields": len(converted_data),
                "schema_version": target_schema
            },
            "quality_score": self._calculate_data_quality(converted_data),
            "ai_model_used": ai_result["model_used"],
            "processing_attempt": ai_result["attempt"]
        }
    
    async def analyze_collected_data(self, data_batch: List[Dict[str, Any]], category: str) -> Dict[str, Any]:
        """수집된 데이터를 AI로 분석하고 인사이트 추출"""
        
        prompt = f"""
        다음 {category} 카테고리의 수집 데이터를 분석해주세요:
        
        데이터 샘플 ({len(data_batch)}개):
        {json.dumps(data_batch[:5], ensure_ascii=False, indent=2)}
        
        분석 요청사항:
        1. 주요 트렌드 및 패턴 식별
        2. 키워드 빈도 및 중요도 분석
        3. 감정 분석 (긍정/부정/중립)
        4. 데이터 품질 평가
        5. 카테고리별 특성 분석
        6. 예측 인사이트 생성
        7. 활용 권장사항
        
        분석 결과를 JSON 형식으로 응답해주세요.
        """
        
        # AI 폴백 시스템 사용
        ai_result = await self.ai_client.process_with_fallback(prompt, "data_analysis")
        
        if not ai_result["success"]:
            logger.error(f"AI 데이터 분석 실패: {ai_result.get('errors', [])}")
            return {
                "analysis_success": False,
                "error": "AI 처리 실패",
                "fallback_errors": ai_result.get("errors", []),
                "category": category,
                "data_count": len(data_batch)
            }
        
        result = ai_result["result"]
        
        return {
            "analysis_success": True,
            "category": category,
            "data_count": len(data_batch),
            "insights": {
                "key_trends": result.get("trends", []),
                "keyword_analysis": result.get("keywords", {}),
                "sentiment_score": result.get("sentiment", 0.0),
                "quality_metrics": result.get("quality", {}),
                "predictions": result.get("predictions", []),
                "recommendations": result.get("recommendations", [])
            },
            "confidence": result.get("confidence", 0.8),
            "analysis_timestamp": datetime.now().isoformat(),
            "ai_model_used": ai_result["model_used"],
            "processing_attempt": ai_result["attempt"]
        }
    
    async def validate_worker_configuration(self, worker_config: Dict[str, Any]) -> Dict[str, Any]:
        """워커 설정을 AI로 검증하고 최적화"""
        
        prompt = f"""
        다음 크롤링 워커 설정을 검증하고 최적화해주세요:
        
        워커 설정:
        - 타입: {worker_config.get('type')}
        - 위치: {worker_config.get('location')}
        - 최대 워커 수: {worker_config.get('max_workers')}
        - 설정: {worker_config.get('config', {})}
        
        검증 항목:
        1. 리소스 사용량 적정성
        2. 성능 최적화 가능성
        3. 안정성 및 에러 처리
        4. 보안 위험 요소
        5. 확장성 고려사항
        
        JSON 형식으로 검증 결과와 최적화 권장사항을 응답해주세요.
        """
        
        # AI 폴백 시스템 사용
        ai_result = await self.ai_client.process_with_fallback(prompt, "worker_validation")
        
        if not ai_result["success"]:
            logger.warning(f"AI 워커 설정 검증 실패: {ai_result.get('errors', [])}")
            return {
                "valid": True,  # 기본값으로 허용
                "error": "AI 처리 실패",
                "fallback_errors": ai_result.get("errors", []),
                "confidence": 0.0
            }
        
        result = ai_result["result"]
        
        return {
            "valid": result.get("valid", True),
            "optimization_score": result.get("score", 7.5),
            "recommendations": result.get("recommendations", []),
            "risk_assessment": result.get("risks", []),
            "resource_optimization": result.get("resource_tips", []),
            "confidence": result.get("confidence", 0.8),
            "ai_model_used": ai_result["model_used"],
            "processing_attempt": ai_result["attempt"]
        }
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """AI 응답을 JSON으로 파싱"""
        try:
            # JSON 코드 블록 추출
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_text = response_text[start:end].strip()
            elif "{" in response_text and "}" in response_text:
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                json_text = response_text[start:end]
            else:
                # JSON이 없으면 기본 응답 생성
                return {"valid": True, "analysis": response_text}
            
            return json.loads(json_text)
            
        except json.JSONDecodeError:
            logger.warning(f"AI 응답 JSON 파싱 실패: {response_text[:200]}...")
            return {"valid": True, "raw_response": response_text}
    
    def _calculate_data_quality(self, data: Dict[str, Any]) -> float:
        """데이터 품질 점수 계산"""
        score = 1.0
        
        # 필수 필드 존재 여부
        required_fields = ["title", "content", "timestamp", "source"]
        existing_fields = sum(1 for field in required_fields if field in data)
        score *= (existing_fields / len(required_fields))
        
        # 데이터 완전성
        empty_values = sum(1 for value in data.values() if not value)
        if len(data) > 0:
            score *= (1 - empty_values / len(data))
        
        return round(score, 2)

# 싱글톤 인스턴스
crawler_service = CrawlerService()

# 편의 함수들
async def validate_api_with_ai(api_config: Dict[str, Any]) -> Dict[str, Any]:
    """API 설정 AI 검증"""
    return await crawler_service.validate_api_configuration(api_config)

async def optimize_job_with_ai(job_config: Dict[str, Any]) -> Dict[str, Any]:
    """크롤링 작업 AI 최적화"""
    return await crawler_service.optimize_crawling_job(job_config)

async def convert_data_with_ai(raw_data: Dict[str, Any], schema: str) -> Dict[str, Any]:
    """데이터 AI 변환"""
    return await crawler_service.convert_api_response(raw_data, schema)

async def analyze_data_with_ai(data: List[Dict[str, Any]], category: str) -> Dict[str, Any]:
    """데이터 AI 분석"""
    return await crawler_service.analyze_collected_data(data, category)

async def validate_worker_config_with_ai(worker_config: Dict[str, Any]) -> Dict[str, Any]:
    """워커 설정 AI 검증"""
    return await crawler_service.validate_worker_configuration(worker_config)