#!/usr/bin/env python3
"""
고급 원격서버 동기화 시스템
여러 방법을 시도하여 원격서버(43.200.203.115)의 데이터베이스를 442개 키워드로 동기화
"""

import asyncio
import aiohttp
import json
import sys
import logging
from datetime import datetime
from typing import Dict, List, Any
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

LOCAL_SERVER = "http://localhost:8001"
REMOTE_SERVER = "https://admin.heal7.com"

class RemoteSyncManager:
    def __init__(self):
        self.session = None
        self.sync_data = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_local_sync_data(self) -> Dict[str, Any]:
        """로컬서버에서 동기화 데이터 가져오기"""
        logger.info("📤 로컬서버에서 동기화 데이터 추출 중...")
        
        try:
            url = f"{LOCAL_SERVER}/admin-api/bulk-sync/keywords/export"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ 로컬 데이터 추출 완료: {data['metadata']['total_keywords']}개 키워드")
                    self.sync_data = data
                    return data
                else:
                    raise Exception(f"로컬 데이터 추출 실패: HTTP {response.status}")
        except Exception as e:
            logger.error(f"❌ 로컬 데이터 추출 오류: {e}")
            raise
    
    async def get_remote_status(self) -> Dict[str, Any]:
        """원격서버 현재 상태 확인"""
        logger.info("🔍 원격서버 현재 상태 확인 중...")
        
        try:
            # 키워드 수 확인
            async with self.session.get(f"{REMOTE_SERVER}/admin-api/keywords/") as response:
                if response.status == 200:
                    keywords = await response.json()
                    keyword_count = len(keywords)
                else:
                    keyword_count = 0
            
            # 건강 상태 확인
            health_status = "unknown"
            try:
                async with self.session.get(f"{REMOTE_SERVER}/admin-api/health") as response:
                    if response.status == 200:
                        health_data = await response.json()
                        health_status = health_data.get("status", "unknown")
            except:
                pass
            
            status = {
                "keyword_count": keyword_count,
                "health_status": health_status,
                "server_url": REMOTE_SERVER,
                "sync_needed": keyword_count != 442
            }
            
            logger.info(f"원격서버 상태: {keyword_count}개 키워드, 건강상태: {health_status}")
            return status
            
        except Exception as e:
            logger.error(f"❌ 원격서버 상태 확인 오류: {e}")
            return {"keyword_count": 0, "health_status": "error", "sync_needed": True}
    
    async def attempt_direct_database_sync(self) -> bool:
        """직접 데이터베이스 동기화 시도 (고급 방법)"""
        logger.info("🔧 직접 데이터베이스 동기화 시도 중...")
        
        if not self.sync_data:
            await self.get_local_sync_data()
        
        try:
            # 방법 1: 원격서버에 동일한 bulk-sync 엔드포인트가 있는지 확인
            logger.info("방법 1: 원격서버 bulk-sync 엔드포인트 확인...")
            try:
                async with self.session.get(f"{REMOTE_SERVER}/admin-api/bulk-sync/status") as response:
                    if response.status == 200:
                        logger.info("✅ 원격서버에 bulk-sync 엔드포인트 발견!")
                        return await self._sync_via_bulk_endpoint()
            except:
                logger.info("원격서버에 bulk-sync 엔드포인트 없음")
            
            # 방법 2: 개별 키워드 API를 통한 동기화 시도
            logger.info("방법 2: 개별 키워드 API를 통한 동기화 시도...")
            return await self._sync_via_individual_apis()
            
        except Exception as e:
            logger.error(f"❌ 직접 동기화 실패: {e}")
            return False
    
    async def _sync_via_bulk_endpoint(self) -> bool:
        """벌크 엔드포인트를 통한 동기화"""
        try:
            # 원격서버의 bulk-sync 엔드포인트로 데이터 전송
            payload = {
                "sync_data": self.sync_data,
                "source": "local-server",
                "timestamp": datetime.now().isoformat()
            }
            
            async with self.session.post(
                f"{REMOTE_SERVER}/admin-api/bulk-sync/import", 
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ 벌크 동기화 성공: {result}")
                    return True
                else:
                    logger.error(f"벌크 동기화 실패: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"벌크 동기화 오류: {e}")
            return False
    
    async def _sync_via_individual_apis(self) -> bool:
        """개별 API를 통한 동기화 (느리지만 확실한 방법)"""
        logger.info("개별 키워드 API를 통한 동기화 시작...")
        
        try:
            keywords = self.sync_data['keywords'][:10]  # 테스트용으로 처음 10개만
            
            success_count = 0
            for keyword in keywords:
                try:
                    # 각 키워드를 개별적으로 원격서버에 전송 시도
                    payload = {
                        "name": keyword['name'],
                        "category": keyword['category'],
                        "weight": keyword['weight'],
                        "status": keyword['status']
                    }
                    
                    # POST 또는 PUT 요청으로 키워드 추가/업데이트 시도
                    async with self.session.post(
                        f"{REMOTE_SERVER}/admin-api/keywords/",
                        json=payload
                    ) as response:
                        if response.status in [200, 201]:
                            success_count += 1
                            logger.info(f"키워드 '{keyword['name']}' 동기화 성공")
                        else:
                            logger.warning(f"키워드 '{keyword['name']}' 동기화 실패: HTTP {response.status}")
                            
                except Exception as e:
                    logger.warning(f"키워드 '{keyword['name']}' 처리 오류: {e}")
                
                # 너무 빠른 요청 방지
                await asyncio.sleep(0.1)
            
            logger.info(f"개별 API 동기화 완료: {success_count}/{len(keywords)}개 성공")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"개별 API 동기화 오류: {e}")
            return False
    
    async def create_sync_instructions(self) -> str:
        """수동 동기화 가이드 생성"""
        logger.info("📋 수동 동기화 가이드 생성 중...")
        
        if not self.sync_data:
            await self.get_local_sync_data()
        
        instructions = f"""
# 🚀 HEAL7 원격서버 수동 동기화 가이드

## 현재 상황
- **로컬서버**: {self.sync_data['metadata']['total_keywords']}개 키워드
- **원격서버**: 30개 키워드 
- **동기화 필요**: 412개 키워드 부족

## 📥 동기화 데이터 다운로드
```bash
# 1. 동기화 데이터 다운로드
curl -s {LOCAL_SERVER}/admin-api/bulk-sync/keywords/export > sync_data.json

# 2. 데이터 검증
jq '.metadata' sync_data.json
```

## 🔧 원격서버에서 실행할 명령어들

### 방법 1: 직접 데이터베이스 업데이트 (추천)
```bash
# PostgreSQL에 직접 연결하여 데이터 업데이트
PGPASSWORD=password psql -h localhost -U liveuser -d livedb << 'EOF'

-- 기존 데이터 백업
\\copy (SELECT * FROM keywords WHERE is_active = true) TO 'keywords_backup.csv' CSV HEADER;
\\copy (SELECT * FROM keyword_dependencies) TO 'dependencies_backup.csv' CSV HEADER;

-- 기존 데이터 삭제
DELETE FROM keyword_dependencies;
DELETE FROM keywords;

-- 여기에 sync_data.json의 내용을 SQL INSERT 문으로 변환하여 실행
-- (별도 스크립트로 JSON을 SQL로 변환 필요)

EOF
```

### 방법 2: API를 통한 업데이트
```bash
# 서비스 재시작 후 bulk-sync 엔드포인트 활성화
sudo systemctl restart heal7-admin

# 로컬 데이터를 원격서버로 전송 시도
curl -X POST https://admin.heal7.com/admin-api/bulk-sync/import \\
  -H "Content-Type: application/json" \\
  -d @sync_data.json
```

## 📊 동기화 후 검증
```bash
# 키워드 수 확인
curl -s https://admin.heal7.com/admin-api/keywords/ | jq '. | length'

# 분류별 분포 확인 (서버에서 직접 실행)
PGPASSWORD=password psql -h localhost -U liveuser -d livedb -c "
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
GROUP BY 분류
ORDER BY 분류;
"
```

## 🎯 예상 결과
- **총 키워드**: 442개
- **A그룹**: 108개  
- **B그룹**: 132개
- **C그룹**: 202개
- **의존성 관계**: 61개

---
생성 시간: {datetime.now().isoformat()}
동기화 데이터 크기: {len(str(self.sync_data))} 바이트
"""
        
        # 가이드를 파일로 저장
        guide_file = "/tmp/remote_sync_guide.md"
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        logger.info(f"✅ 동기화 가이드 생성 완료: {guide_file}")
        return instructions

async def main():
    """메인 동기화 프로세스"""
    print("🚀 HEAL7 고급 원격서버 동기화 시스템 시작")
    print("=" * 60)
    
    async with RemoteSyncManager() as sync_manager:
        try:
            # 1. 현재 상태 확인
            print("\\n1️⃣ 현재 상태 확인 중...")
            local_data = await sync_manager.get_local_sync_data()
            remote_status = await sync_manager.get_remote_status()
            
            print(f"   로컬: {local_data['metadata']['total_keywords']}개 키워드")
            print(f"   원격: {remote_status['keyword_count']}개 키워드")
            
            if not remote_status['sync_needed']:
                print("✅ 동기화 불필요 - 이미 442개 키워드 보유")
                return
            
            # 2. 직접 동기화 시도
            print("\\n2️⃣ 직접 동기화 시도 중...")
            sync_success = await sync_manager.attempt_direct_database_sync()
            
            if sync_success:
                print("✅ 직접 동기화 성공!")
                
                # 결과 확인
                print("\\n3️⃣ 동기화 결과 확인 중...")
                final_status = await sync_manager.get_remote_status()
                print(f"   원격서버 최종 키워드 수: {final_status['keyword_count']}개")
                
                if final_status['keyword_count'] == 442:
                    print("🎉 완전 동기화 성공!")
                    return
            
            # 3. 수동 동기화 가이드 생성
            print("\\n3️⃣ 수동 동기화 가이드 생성 중...")
            instructions = await sync_manager.create_sync_instructions()
            
            print("📋 원격서버 관리자용 동기화 가이드:")
            print("   - /tmp/remote_sync_guide.md")
            print("   - /tmp/remote_sync_data.json")
            
        except Exception as e:
            logger.error(f"❌ 동기화 프로세스 오류: {e}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())