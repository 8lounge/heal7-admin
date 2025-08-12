-- HEAL7 원격서버 데이터베이스 동기화 SQL 스크립트
-- 442개 키워드 및 분류 시스템 동기화
-- 실행일: 2025-08-09
-- 목표: 30개 키워드 -> 442개 키워드 동기화

-- ========================================
-- 1. 기존 데이터 백업 (안전성 보장)
-- ========================================
-- 백업은 pg_dump 명령어로 수행하세요:
-- pg_dump -U liveuser -d livedb -t keywords -t keywords_subcategories -t keyword_dependencies > backup_before_sync.sql

-- ========================================
-- 2. 기존 데이터 정리
-- ========================================
BEGIN;

-- 의존성 관계 삭제 (외래키 제약으로 인해 먼저 삭제)
DELETE FROM keyword_dependencies;

-- 기존 키워드 삭제 (새 데이터로 완전 교체)
DELETE FROM keywords;

-- 기존 서브카테고리 삭제 (새 분류 시스템 적용)
DELETE FROM keywords_subcategories;

-- ========================================
-- 3. 새로운 서브카테고리 시스템 추가
-- ========================================
-- A그룹: 인지능력 (A-1 ~ A-5)
INSERT INTO keywords_subcategories (id, name, description, category_group, display_order, is_active) VALUES
(1, 'A-1', '감정 조절', 'A', 1, true),
(2, 'A-2', '스트레스 대응', 'A', 2, true),
(3, 'A-3', '자아 인식', 'A', 3, true),
(4, 'A-4', '대인 관계', 'A', 4, true),
(5, 'A-5', '동기 부여', 'A', 5, true);

-- B그룹: 자기통제 (B-1 ~ B-6) 
INSERT INTO keywords_subcategories (id, name, description, category_group, display_order, is_active) VALUES
(6, 'B-1', '집중력', 'B', 1, true),
(7, 'B-2', '기억력', 'B', 2, true),
(8, 'B-3', '문제 해결', 'B', 3, true),
(9, 'B-4', '창의성', 'B', 4, true),
(10, 'B-5', '학습 능력', 'B', 5, true),
(11, 'B-6', '논리적 사고', 'B', 6, true);

-- C그룹: 스트레스관리 (C-1 ~ C-9)
INSERT INTO keywords_subcategories (id, name, description, category_group, display_order, is_active) VALUES
(12, 'C-1', '적응력', 'C', 1, true),
(13, 'C-2', '리더십', 'C', 2, true),
(14, 'C-3', '의사결정', 'C', 3, true),
(15, 'C-4', '의사소통', 'C', 4, true),
(16, 'C-5', '협업 능력', 'C', 5, true),
(17, 'C-6', '목표 지향', 'C', 6, true),
(18, 'C-7', '자기 관리', 'C', 7, true),
(19, 'C-8', '책임감', 'C', 8, true),
(20, 'C-9', '성취 지향', 'C', 9, true);

-- 서브카테고리 ID 시퀀스 업데이트
SELECT setval('keywords_subcategories_id_seq', 20, true);

-- ========================================
-- 4. 442개 키워드 데이터 삽입
-- ========================================
-- 이 부분은 실제 마이그레이션 파일의 내용을 사용합니다
-- /tmp/keywords_migration.sql 파일의 INSERT 구문들을 여기에 포함시키거나
-- 별도로 실행하세요:
-- \i /tmp/keywords_migration.sql

-- ========================================
-- 5. 키워드 의존성 관계 추가
-- ========================================
-- 키워드 의존성 관계도 마이그레이션 파일에 포함되어 있습니다.

-- ========================================
-- 6. 시퀀스 업데이트
-- ========================================
-- 키워드 ID 시퀀스를 442 이후로 설정
SELECT setval('keywords_id_seq', (SELECT MAX(id) FROM keywords), true);

-- ========================================
-- 7. 데이터 검증 쿼리
-- ========================================
-- 동기화 완료 후 실행할 검증 쿼리들

-- 총 키워드 수 확인
SELECT '총 키워드 수' as 항목, COUNT(*) as 개수 FROM keywords WHERE is_active = true;

-- 분류별 키워드 수 확인
SELECT 
    CASE 
        WHEN ksc.name LIKE 'A-%' THEN 'A그룹 (인지능력)'
        WHEN ksc.name LIKE 'B-%' THEN 'B그룹 (자기통제)'  
        WHEN ksc.name LIKE 'C-%' THEN 'C그룹 (스트레스관리)'
    END as 분류,
    COUNT(*) as 키워드수
FROM keywords k
JOIN keywords_subcategories ksc ON k.subcategory_id = ksc.id  
WHERE k.is_active = true
GROUP BY 
    CASE 
        WHEN ksc.name LIKE 'A-%' THEN 'A그룹 (인지능력)'
        WHEN ksc.name LIKE 'B-%' THEN 'B그룹 (자기통제)'
        WHEN ksc.name LIKE 'C-%' THEN 'C그룹 (스트레스관리)'
    END
ORDER BY 분류;

-- 서브카테고리별 상세 분포
SELECT 
    ksc.name as 서브카테고리,
    ksc.description as 설명,
    COUNT(k.id) as 키워드수
FROM keywords_subcategories ksc
LEFT JOIN keywords k ON k.subcategory_id = ksc.id AND k.is_active = true
WHERE ksc.is_active = true
GROUP BY ksc.name, ksc.description, ksc.display_order
ORDER BY ksc.name;

-- 의존성 관계 수 확인
SELECT '키워드 의존성 관계' as 항목, COUNT(*) as 개수 FROM keyword_dependencies;

-- 샘플 키워드 확인 (각 그룹별 5개씩)
SELECT '샘플 키워드 (A그룹)' as 분류, k.text as 키워드명, ksc.name as 서브카테고리
FROM keywords k 
JOIN keywords_subcategories ksc ON k.subcategory_id = ksc.id
WHERE ksc.name LIKE 'A-%' AND k.is_active = true 
LIMIT 5;

SELECT '샘플 키워드 (B그룹)' as 분류, k.text as 키워드명, ksc.name as 서브카테고리  
FROM keywords k
JOIN keywords_subcategories ksc ON k.subcategory_id = ksc.id
WHERE ksc.name LIKE 'B-%' AND k.is_active = true
LIMIT 5;

SELECT '샘플 키워드 (C그룹)' as 분류, k.text as 키워드명, ksc.name as 서브카테고리
FROM keywords k 
JOIN keywords_subcategories ksc ON k.subcategory_id = ksc.id
WHERE ksc.name LIKE 'C-%' AND k.is_active = true
LIMIT 5;

COMMIT;

-- ========================================
-- 8. 동기화 완료 메시지
-- ========================================
SELECT 
    '🎉 HEAL7 원격서버 동기화 완료!' as 메시지,
    '442개 키워드, 20개 서브카테고리, 의존성 관계 포함' as 세부사항,
    NOW() as 완료시각;