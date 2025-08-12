#!/usr/bin/env python3
"""
HEAL7 원격서버 API 동기화 스크립트
SSH 연결이 불가능한 경우를 위한 API 기반 동기화
"""

import asyncio
import json
import aiohttp
import asyncpg
import sys
from datetime import datetime
from typing import List, Dict, Any

# 데이터베이스 설정
DB_CONFIG = {
    "host": "localhost",
    "database": "livedb",
    "user": "liveuser", 
    "password": "password"
}

REMOTE_SERVER = "https://admin.heal7.com"

async def get_local_keywords() -> List[Dict]:
    """로컬 데이터베이스에서 442개 키워드 추출"""
    print("📤 로컬 데이터베이스에서 키워드 데이터 추출 중...")
    
    conn = await asyncpg.connect(**DB_CONFIG)
    try:
        query = """
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
        
        rows = await conn.fetch(query)
        keywords = []
        
        for row in rows:
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
            
        print(f"✅ {len(keywords)}개 키워드 추출 완료")
        return keywords
        
    finally:
        await conn.close()

async def get_remote_keyword_count() -> int:
    """원격서버 현재 키워드 수 확인"""
    print("🔍 원격서버 현재 키워드 수 확인 중...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{REMOTE_SERVER}/admin-api/keywords/") as response:
                if response.status == 200:
                    data = await response.json()
                    count = len(data)
                    print(f"원격서버 현재 키워드: {count}개")
                    return count
                else:
                    print(f"❌ 원격서버 연결 실패: {response.status}")
                    return 0
        except Exception as e:
            print(f"❌ 원격서버 연결 오류: {e}")
            return 0

async def create_sync_endpoint_data(keywords: List[Dict]) -> Dict:
    """동기화용 데이터 구조 생성"""
    print("📋 동기화 데이터 구조 생성 중...")
    
    # 분류별 통계
    categories = {}
    for keyword in keywords:
        cat = keyword['category'][:2]  # A-, B-, C-
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    
    # 의존성 관계 통계
    total_dependencies = sum(len(kw['dependencies']) for kw in keywords)
    
    sync_data = {
        "metadata": {
            "total_keywords": len(keywords),
            "categories": categories,
            "total_dependencies": total_dependencies,
            "sync_timestamp": datetime.now().isoformat()
        },
        "keywords": keywords
    }
    
    print(f"✅ 동기화 데이터 준비 완료:")
    print(f"   - 총 키워드: {len(keywords)}개")
    print(f"   - 분류: {categories}")
    print(f"   - 의존성 관계: {total_dependencies}개")
    
    return sync_data

async def save_sync_data_to_file(sync_data: Dict, filename: str = "/tmp/remote_sync_data.json"):
    """동기화 데이터를 파일로 저장"""
    print(f"💾 동기화 데이터를 {filename}에 저장 중...")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(sync_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 동기화 데이터 저장 완료")
    return filename

async def check_remote_server_sync(expected_count: int = 442) -> bool:
    """원격서버 동기화 상태 확인"""
    print(f"🔍 원격서버 동기화 확인 (예상: {expected_count}개)...")
    
    current_count = await get_remote_keyword_count()
    
    if current_count == expected_count:
        print(f"✅ 동기화 성공: {current_count}개 키워드 확인됨")
        return True
    else:
        print(f"⚠️  동기화 필요: 현재 {current_count}개, 목표 {expected_count}개")
        return False

async def main():
    """메인 동기화 프로세스"""
    print("🚀 HEAL7 원격서버 API 동기화 시작")
    print(f"원격서버: {REMOTE_SERVER}")
    print(f"로컬 DB: {DB_CONFIG['host']}:{DB_CONFIG['database']}")
    print()
    
    try:
        # 1. 원격서버 현재 상태 확인
        await get_remote_keyword_count()
        
        # 2. 로컬 키워드 데이터 추출
        keywords = await get_local_keywords()
        
        if not keywords:
            print("❌ 로컬 키워드 데이터가 없습니다.")
            sys.exit(1)
        
        # 3. 동기화 데이터 구조 생성
        sync_data = await create_sync_endpoint_data(keywords)
        
        # 4. 동기화 데이터 파일 저장
        sync_file = await save_sync_data_to_file(sync_data)
        
        print()
        print("📋 동기화 요약:")
        print(f"   - 로컬 추출: {len(keywords)}개 키워드")
        print(f"   - 분류 시스템: A1-A5, B1-B6, C1-C9")
        print(f"   - 의존성 관계: {sync_data['metadata']['total_dependencies']}개")
        print(f"   - 동기화 파일: {sync_file}")
        print()
        
        # 5. 원격서버 동기화 상태 재확인
        is_synced = await check_remote_server_sync()
        
        if not is_synced:
            print()
            print("📝 수동 동기화 방법:")
            print("1. SSH 접근이 가능한 경우:")
            print(f"   scp {sync_file} ubuntu@43.200.203.115:/tmp/")
            print("   ssh ubuntu@43.200.203.115")
            print("   # 원격서버에서 데이터베이스 업데이트")
            print()
            print("2. 관리자 페이지에서:")
            print(f"   {sync_file} 파일을 이용해 수동 업로드")
            print()
            print("3. API 엔드포인트가 있는 경우:")
            print(f"   POST {REMOTE_SERVER}/admin-api/keywords/bulk-sync")
        
        print("🎉 동기화 준비 완료!")
        
    except Exception as e:
        print(f"❌ 동기화 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())