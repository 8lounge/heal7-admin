"""
HEAL7 JSON 직렬화 유틸리티
PostgreSQL 데이터를 JSON 직렬화 가능하도록 변환
"""

import json
import decimal
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional, Union
import uuid
import logging

logger = logging.getLogger("heal7.json_serializer")

class JSONSerializer:
    """PostgreSQL 데이터를 JSON 직렬화 가능하게 변환하는 유틸리티"""
    
    @staticmethod
    def serialize_value(value: Any) -> Any:
        """단일 값을 JSON 직렬화 가능하게 변환"""
        if value is None:
            return None
            
        # 기본 타입들은 그대로 반환
        if isinstance(value, (str, int, float, bool)):
            return value
            
        # datetime 객체 처리
        if isinstance(value, datetime):
            return value.isoformat()
            
        if isinstance(value, date):
            return value.isoformat()
            
        if isinstance(value, timedelta):
            return value.total_seconds()
            
        # UUID 처리
        if isinstance(value, uuid.UUID):
            return str(value)
            
        # Decimal 처리
        if isinstance(value, decimal.Decimal):
            return float(value)
            
        # 리스트 처리
        if isinstance(value, (list, tuple)):
            return [JSONSerializer.serialize_value(item) for item in value]
            
        # 딕셔너리 처리
        if isinstance(value, dict):
            return {key: JSONSerializer.serialize_value(val) for key, val in value.items()}
            
        # PostgreSQL의 RealDictRow 처리
        if hasattr(value, '_asdict'):
            return JSONSerializer.serialize_value(dict(value))
            
        # 기타 객체들은 문자열로 변환
        try:
            return str(value)
        except Exception as e:
            logger.warning(f"값 직렬화 실패, None으로 변환: {value} - {e}")
            return None
    
    @staticmethod
    def serialize_row(row: Any) -> Dict[str, Any]:
        """PostgreSQL 행 데이터를 JSON 직렬화 가능한 딕셔너리로 변환"""
        if row is None:
            return {}
            
        # RealDictCursor의 결과를 딕셔너리로 변환
        if hasattr(row, '_asdict'):
            row_dict = dict(row)
        elif isinstance(row, dict):
            row_dict = row
        else:
            logger.warning(f"알 수 없는 행 타입: {type(row)}")
            return {}
        
        # 각 필드를 직렬화
        serialized = {}
        for key, value in row_dict.items():
            try:
                serialized[key] = JSONSerializer.serialize_value(value)
            except Exception as e:
                logger.error(f"필드 '{key}' 직렬화 실패: {e}")
                serialized[key] = None
                
        return serialized
    
    @staticmethod
    def serialize_rows(rows: List[Any]) -> List[Dict[str, Any]]:
        """PostgreSQL 행 목록을 JSON 직렬화 가능한 딕셔너리 목록으로 변환"""
        if not rows:
            return []
            
        return [JSONSerializer.serialize_row(row) for row in rows]
    
    @staticmethod
    def handle_jsonb_fields(data: Dict[str, Any], jsonb_fields: List[str]) -> Dict[str, Any]:
        """JSONB 필드들을 안전하게 처리"""
        for field in jsonb_fields:
            if field in data:
                value = data[field]
                if isinstance(value, str):
                    try:
                        data[field] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"JSONB 필드 '{field}' 파싱 실패: {value}")
                        data[field] = {}
                elif value is None:
                    data[field] = {}
        return data
    
    @staticmethod
    def safe_json_dumps(obj: Any, **kwargs) -> str:
        """안전한 JSON 문자열 변환"""
        try:
            serialized = JSONSerializer.serialize_value(obj)
            return json.dumps(serialized, ensure_ascii=False, **kwargs)
        except Exception as e:
            logger.error(f"JSON 직렬화 실패: {e}")
            return "{}"
    
    @staticmethod
    def create_response_data(data: Any, success: bool = True, message: Optional[str] = None) -> Dict[str, Any]:
        """API 응답용 데이터 생성"""
        response = {
            "success": success,
            "data": JSONSerializer.serialize_value(data)
        }
        
        if message:
            response["message"] = message
            
        response["timestamp"] = datetime.now().isoformat()
        
        return response

# 편의 함수들
def serialize_for_json(obj: Any) -> Any:
    """단일 객체 JSON 직렬화"""
    return JSONSerializer.serialize_value(obj)

def serialize_db_row(row: Any) -> Dict[str, Any]:
    """데이터베이스 행 JSON 직렬화"""
    return JSONSerializer.serialize_row(row)

def serialize_db_rows(rows: List[Any]) -> List[Dict[str, Any]]:
    """데이터베이스 행 목록 JSON 직렬화"""
    return JSONSerializer.serialize_rows(rows)

def create_api_response(data: Any, success: bool = True, message: Optional[str] = None) -> Dict[str, Any]:
    """API 응답 생성"""
    return JSONSerializer.create_response_data(data, success, message)

def safe_dumps(obj: Any, **kwargs) -> str:
    """안전한 JSON 문자열 변환"""
    return JSONSerializer.safe_json_dumps(obj, **kwargs)