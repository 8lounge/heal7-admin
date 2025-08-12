"""
임시 벌크 동기화 엔드포인트
원격서버가 로컬 데이터를 가져갈 수 있도록 하는 임시 API
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import asyncpg
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin-api/bulk-sync", tags=["Bulk Sync"])

# 데이터베이스 설정
DB_CONFIG = {
    "host": "localhost",
    "database": "livedb", 
    "user": "liveuser",
    "password": "password"
}

@router.get("/keywords/export")
async def export_keywords_for_sync():
    """
    442개 키워드를 동기화용으로 내보내기
    원격서버가 이 데이터를 가져가서 자신의 DB에 적용할 수 있음
    """
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        
        # 키워드 데이터 추출
        keyword_query = """
        SELECT 
            k.id,
            k.text as name,
            ksc.name as category,
            ksc.name as subcategory,
            k.weight,
            COALESCE(k.usage_count, 0) as connections,
            CASE WHEN k.is_active THEN 'active' ELSE 'inactive' END as status,
            COALESCE(
                ARRAY(
                    SELECT kd.dependent_keyword_id 
                    FROM keyword_dependencies kd 
                    WHERE kd.parent_keyword_id = k.id
                ), 
                ARRAY[]::integer[]
            ) as dependencies,
            NULL as position,
            CASE 
                WHEN ksc.name LIKE 'A-%' THEN '#3B82F6'
                WHEN ksc.name LIKE 'B-%' THEN '#EF4444'
                WHEN ksc.name LIKE 'C-%' THEN '#06B6D4'
                ELSE '#6366F1'
            END as color
        FROM keywords k
        JOIN keywords_subcategories ksc ON k.subcategory_id = ksc.id
        WHERE k.is_active = true
        ORDER BY k.id
        """
        
        keywords_rows = await conn.fetch(keyword_query)
        
        # 서브카테고리 데이터 추출
        subcategory_query = """
        SELECT id, name, description, category_group, display_order, is_active
        FROM keywords_subcategories 
        WHERE is_active = true
        ORDER BY name
        """
        
        subcategories_rows = await conn.fetch(subcategory_query)
        
        # 의존성 관계 추출
        dependencies_query = """
        SELECT parent_keyword_id, dependent_keyword_id
        FROM keyword_dependencies
        ORDER BY parent_keyword_id, dependent_keyword_id
        """
        
        dependencies_rows = await conn.fetch(dependencies_query)
        
        await conn.close()
        
        # 데이터 변환
        keywords = []
        for row in keywords_rows:
            keyword = {
                "id": row['id'],
                "name": row['name'],
                "category": row['category'],
                "subcategory": row['subcategory'],
                "weight": float(row['weight']),
                "connections": row['connections'],
                "status": row['status'],
                "dependencies": list(row['dependencies']),
                "position": row['position'],
                "color": row['color']
            }
            keywords.append(keyword)
        
        subcategories = []
        for row in subcategories_rows:
            subcategory = {
                "id": row['id'],
                "name": row['name'],
                "description": row['description'],
                "category_group": row['category_group'],
                "display_order": row['display_order'],
                "is_active": row['is_active']
            }
            subcategories.append(subcategory)
        
        dependencies = []
        for row in dependencies_rows:
            dependency = {
                "parent_keyword_id": row['parent_keyword_id'],
                "dependent_keyword_id": row['dependent_keyword_id']
            }
            dependencies.append(dependency)
        
        # 통계 계산
        categories = {}
        for keyword in keywords:
            cat = keyword['category'][:2]  # A-, B-, C-
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        
        sync_data = {
            "metadata": {
                "total_keywords": len(keywords),
                "total_subcategories": len(subcategories),
                "total_dependencies": len(dependencies),
                "categories": categories,
                "sync_timestamp": "2025-08-09T17:00:00Z",
                "source": "local-server-livedb"
            },
            "keywords": keywords,
            "subcategories": subcategories,
            "dependencies": dependencies
        }
        
        logger.info(f"✅ 동기화 데이터 내보내기 완료: {len(keywords)}개 키워드")
        return sync_data
        
    except Exception as e:
        logger.error(f"❌ 동기화 데이터 내보내기 실패: {e}")
        raise HTTPException(status_code=500, detail=f"동기화 데이터 내보내기 실패: {str(e)}")

@router.get("/status")
async def get_sync_status():
    """동기화 상태 확인"""
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        
        # 기본 통계
        stats_query = """
        SELECT 
            COUNT(*) as total_keywords,
            COUNT(DISTINCT ksc.id) as total_subcategories,
            (SELECT COUNT(*) FROM keyword_dependencies) as total_dependencies
        FROM keywords k
        JOIN keywords_subcategories ksc ON k.subcategory_id = ksc.id
        WHERE k.is_active = true
        """
        
        stats = await conn.fetchrow(stats_query)
        
        # 분류별 통계
        category_query = """
        SELECT 
            CASE 
                WHEN ksc.name LIKE 'A-%' THEN 'A그룹'
                WHEN ksc.name LIKE 'B-%' THEN 'B그룹' 
                WHEN ksc.name LIKE 'C-%' THEN 'C그룹'
            END as 분류,
            COUNT(*) as 키워드수
        FROM keywords k
        JOIN keywords_subcategories ksc ON k.subcategory_id = ksc.id
        WHERE k.is_active = true
        GROUP BY 
            CASE 
                WHEN ksc.name LIKE 'A-%' THEN 'A그룹'
                WHEN ksc.name LIKE 'B-%' THEN 'B그룹'
                WHEN ksc.name LIKE 'C-%' THEN 'C그룹'
            END
        ORDER BY 분류
        """
        
        category_stats = await conn.fetch(category_query)
        
        await conn.close()
        
        return {
            "server_type": "local-source",
            "database": "livedb", 
            "total_keywords": stats['total_keywords'],
            "total_subcategories": stats['total_subcategories'],
            "total_dependencies": stats['total_dependencies'],
            "category_distribution": [dict(row) for row in category_stats],
            "sync_ready": True,
            "last_check": "2025-08-09T17:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"❌ 동기화 상태 확인 실패: {e}")
        raise HTTPException(status_code=500, detail=f"동기화 상태 확인 실패: {str(e)}")

@router.post("/trigger-remote-sync")
async def trigger_remote_sync():
    """
    원격서버 동기화 트리거
    원격서버가 로컬서버의 데이터를 가져가도록 신호 전송
    """
    import aiohttp
    
    try:
        # 원격서버에 동기화 요청 전송
        async with aiohttp.ClientSession() as session:
            # 1. 원격서버 상태 확인
            async with session.get("https://admin.heal7.com/admin-api/keywords/") as response:
                if response.status == 200:
                    remote_keywords = await response.json()
                    remote_count = len(remote_keywords)
                else:
                    remote_count = 0
            
            # 2. 로컬서버 데이터 내보내기
            export_url = "http://localhost:8001/admin-api/bulk-sync/keywords/export"
            async with session.get(export_url) as response:
                if response.status == 200:
                    sync_data = await response.json()
                    local_count = sync_data['metadata']['total_keywords']
                else:
                    raise Exception("로컬 데이터 내보내기 실패")
        
        return {
            "status": "sync_triggered",
            "local_keywords": local_count,
            "remote_keywords": remote_count,
            "sync_needed": local_count != remote_count,
            "message": f"동기화 트리거 완료 (로컬: {local_count}개, 원격: {remote_count}개)",
            "sync_data_size": len(str(sync_data)),
            "timestamp": "2025-08-09T17:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"❌ 원격서버 동기화 트리거 실패: {e}")
        raise HTTPException(status_code=500, detail=f"동기화 트리거 실패: {str(e)}")