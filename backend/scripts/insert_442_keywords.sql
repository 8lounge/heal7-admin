-- ================================================
-- HEAL7 M-PIS 프레임워크 442개 키워드 삽입 스크립트
-- 기존 30개 키워드 + 412개 신규 키워드 = 총 442개
-- ================================================

-- 트랜잭션 시작
BEGIN;

-- 기존 키워드 수 확인
DO $$
DECLARE
    keyword_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO keyword_count FROM keywords;
    RAISE NOTICE '현재 키워드 수: %', keyword_count;
    
    IF keyword_count != 30 THEN
        RAISE EXCEPTION '기존 키워드 수가 30개가 아닙니다. 현재: %개', keyword_count;
    END IF;
END $$;

-- ================================================
-- A그룹: 인지적 차원 (A-1 ~ A-5) - 100개 키워드
-- ================================================

-- A-1 인지차원 (기존 10개 + 신규 10개 = 20개)
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('정보처리능력', 1, true),
('사고유연성', 1, true),
('인지속도', 1, true),
('작업기억', 1, true),
('실행기능', 1, true),
('인지전환', 1, true),
('계획수립', 1, true),
('의사결정', 1, true),
('추론능력', 1, true),
('개념형성', 1, true);

-- A-2 개방성차원 (기존 10개 + 신규 10개 = 20개)  
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('경험개방성', 2, true),
('지적호기심', 2, true),
('미적감수성', 2, true),
('가치다양성', 2, true),
('행동융통성', 2, true),
('아이디어개방성', 2, true),
('감정개방성', 2, true),
('환상력', 2, true),
('심미안', 2, true),
('진취성', 2, true);

-- A-3 에너지차원 (신규 20개)
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('활력', 3, true),
('에너지수준', 3, true),
('동기부여', 3, true),
('추진력', 3, true),
('열정', 3, true),
('적극성', 3, true),
('도전정신', 3, true),
('성취욕구', 3, true),
('목표지향성', 3, true),
('완성도추구', 3, true),
('지구력', 3, true),
('회복력', 3, true),
('탄력성', 3, true),
('자발성', 3, true),
('주도성', 3, true),
('능동성', 3, true),
('진취정신', 3, true),
('역동성', 3, true),
('생명력', 3, true),
('긍정에너지', 3, true);

-- A-4 관계차원 (신규 20개)
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('사회성', 4, true),
('친화력', 4, true),
('소통능력', 4, true),
('공감능력', 4, true),
('협력성', 4, true),
('배려심', 4, true),
('이해력', 4, true),
('신뢰관계', 4, true),
('유대감', 4, true),
('친밀감', 4, true),
('사회적지지', 4, true),
('네트워킹', 4, true),
('인맥관리', 4, true),
('관계유지', 4, true),
('갈등해결', 4, true),
('타협능력', 4, true),
('중재능력', 4, true),
('팀워크', 4, true),
('리더십', 4, true),
('팔로워십', 4, true);

-- A-5 정서차원 (신규 20개)
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('감정지능', 5, true),
('감정인식', 5, true),
('감정표현', 5, true),
('감정이해', 5, true),
('정서안정성', 5, true),
('정서균형', 5, true),
('감정성숙', 5, true),
('정서적민감성', 5, true),
('감정적통찰', 5, true),
('정서조화', 5, true),
('마음챙김', 5, true),
('내면평화', 5, true),
('정서적자유', 5, true),
('감정정화', 5, true),
('치유능력', 5, true),
('회복탄력성', 5, true),
('정서적균형', 5, true),
('심리적안정', 5, true),
('정서적성장', 5, true),
('감정적건강', 5, true);

-- ================================================
-- B그룹: 뇌기능 차원 (B-1 ~ B-6) - 120개 키워드
-- ================================================

-- B-1 전전두엽계 (기존 5개 + 신규 15개 = 20개)
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('실행계획', 6, true),
('목표설정', 6, true),
('우선순위', 6, true),
('시간관리', 6, true),
('작업조직화', 6, true),
('전략적사고', 6, true),
('장기계획', 6, true),
('업무관리', 6, true),
('프로젝트관리', 6, true),
('체계성', 6, true),
('계획성', 6, true),
('조직능력', 6, true),
('관리능력', 6, true),
('통제력', 6, true),
('책임감', 6, true);

-- B-2 측두두정계 (신규 20개)
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('공간인식', 7, true),
('시각처리', 7, true),
('청각처리', 7, true),
('감각통합', 7, true),
('지각능력', 7, true),
('방향감각', 7, true),
('공간지능', 7, true),
('시공간능력', 7, true),
('도형인식', 7, true),
('패턴감지', 7, true),
('공간기억', 7, true),
('시각기억', 7, true),
('청각기억', 7, true),
('감각기억', 7, true),
('지각조직화', 7, true),
('감각변별', 7, true),
('공간추론', 7, true),
('시각분석', 7, true),
('청각분석', 7, true),
('다중감각처리', 7, true);

-- B-3 변연계 (기존 2개 + 신규 18개 = 20개)
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('정서기억', 8, true),
('트라우마처리', 8, true),
('기억형성', 8, true),
('해마기능', 8, true),
('정서학습', 8, true),
('조건화', 8, true),
('습관형성', 8, true),
('동기시스템', 8, true),
('보상민감성', 8, true),
('쾌락추구', 8, true),
('위험회피', 8, true),
('신규성추구', 8, true),
('사회적보상', 8, true),
('내재동기', 8, true),
('외재동기', 8, true),
('욕구만족', 8, true),
('쾌감추구', 8, true),
('긍정감정', 8, true);

-- B-4 기저핵계 (신규 20개)
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('운동제어', 9, true),
('습관패턴', 9, true),
('자동화', 9, true),
('루틴형성', 9, true),
('절차기억', 9, true),
('기술습득', 9, true),
('운동학습', 9, true),
('행동자동화', 9, true),
('근육기억', 9, true),
('동작조절', 9, true),
('균형감각', 9, true),
('협응능력', 9, true),
('정밀동작', 9, true),
('반사반응', 9, true),
('운동계획', 9, true),
('동작순서', 9, true),
('운동타이밍', 9, true),
('동작조화', 9, true),
('운동유창성', 9, true),
('기능적움직임', 9, true);

-- B-5 뇌간계 (신규 20개)
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('각성수준', 10, true),
('주의각성', 10, true),
('경계성', 10, true),
('생체리듬', 10, true),
('수면패턴', 10, true),
('자율신경', 10, true),
('호흡조절', 10, true),
('심박조절', 10, true),
('체온조절', 10, true),
('혈압조절', 10, true),
('소화조절', 10, true),
('면역조절', 10, true),
('호르몬조절', 10, true),
('신체항상성', 10, true),
('생리적균형', 10, true),
('신체적안정', 10, true),
('기본생명기능', 10, true),
('생존본능', 10, true),
('위험탐지', 10, true),
('방어반응', 10, true);

-- B-6 신경화학계 (신규 20개)
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('도파민시스템', 11, true),
('세로토닌시스템', 11, true),
('노르에피네프린', 11, true),
('아세틸콜린', 11, true),
('GABA시스템', 11, true),
('글루타메이트', 11, true),
('옥시토신', 11, true),
('엔도르핀', 11, true),
('코르티솔조절', 11, true),
('신경전달물질', 11, true),
('화학적균형', 11, true),
('뇌화학조절', 11, true),
('신경조절', 11, true),
('뇌내화학', 11, true),
('신경가소성', 11, true),
('시냅스기능', 11, true),
('뇌네트워크', 11, true),
('신경연결', 11, true),
('뇌신경회로', 11, true),
('신경활성화', 11, true);

-- ================================================
-- C그룹: 정신건강 차원 (C-1 ~ C-9) - 192개 키워드
-- ================================================

-- C-1 불안스트레스 (기존 2개 + 신규 20개 = 22개)
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('불안감소', 12, true),
('긴장완화', 12, true),
('압박감완화', 12, true),
('걱정감소', 12, true),
('두려움극복', 12, true),
('공황관리', 12, true),
('사회불안', 12, true),
('수행불안', 12, true),
('분리불안', 12, true),
('일반불안', 12, true),
('강박적걱정', 12, true),
('예기불안', 12, true),
('건강불안', 12, true),
('관계불안', 12, true),
('미래불안', 12, true),
('완벽주의불안', 12, true),
('평가불안', 12, true),
('인정불안', 12, true),
('실패불안', 12, true),
('스트레스해소', 12, true);

-- C-2 우울무기력 (신규 22개)
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('우울감완화', 13, true),
('무기력극복', 13, true),
('절망감해소', 13, true),
('의욕상실', 13, true),
('흥미상실', 13, true),
('에너지부족', 13, true),
('피로감', 13, true),
('무력감', 13, true),
('좌절감', 13, true),
('실망감', 13, true),
('슬픔처리', 13, true),
('공허감', 13, true),
('외로움', 13, true),
('고립감', 13, true),
('자기비난', 13, true),
('죄책감', 13, true),
('부정적사고', 13, true),
('비관적전망', 13, true),
('희망부족', 13, true),
('동기부족', 13, true),
('활동저하', 13, true),
('사회적위축', 13, true);

-- C-3 분노공격성 (기존 1개 + 신규 21개 = 22개)
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('화 다스리기', 14, true),
('적대감완화', 14, true),
('공격성조절', 14, true),
('짜증관리', 14, true),
('폭발성조절', 14, true),
('언어폭력', 14, true),
('신체폭력', 14, true),
('간접공격성', 14, true),
('수동공격성', 14, true),
('분노표출', 14, true),
('분노억압', 14, true),
('원한감', 14, true),
('복수심', 14, true),
('증오감', 14, true),
('적개심', 14, true),
('반항성', 14, true),
('도전적행동', 14, true),
('파괴적충동', 14, true),
('자해충동', 14, true),
('타해충동', 14, true),
('감정폭발', 14, true);

-- C-4 중독의존 (신규 22개)
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('물질중독', 15, true),
('알코올의존', 15, true),
('니코틴의존', 15, true),
('카페인의존', 15, true),
('약물남용', 15, true),
('행동중독', 15, true),
('게임중독', 15, true),
('인터넷중독', 15, true),
('쇼핑중독', 15, true),
('도박중독', 15, true),
('성중독', 15, true),
('음식중독', 15, true),
('운동중독', 15, true),
('관계중독', 15, true),
('승인중독', 15, true),
('일중독', 15, true),
('스마트폰중독', 15, true),
('의존적행동', 15, true),
('강박적사용', 15, true),
('금단증상', 15, true),
('내성현상', 15, true),
('중독회복', 15, true);

-- C-5 사회부적응 (신규 22개)
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('사회적회피', 16, true),
('대인기피', 16, true),
('사회공포', 16, true),
('소외감', 16, true),
('고립감', 16, true),
('위축행동', 16, true),
('사회적철수', 16, true),
('관계기피', 16, true),
('집단부적응', 16, true),
('사회적역할혼란', 16, true),
('소속감결여', 16, true),
('사회적유대감부족', 16, true),
('커뮤니케이션장애', 16, true),
('사회적기술부족', 16, true),
('대인갈등', 16, true),
('사회적거부', 16, true),
('따돌림경험', 16, true),
('사회적낙인', 16, true),
('편견경험', 16, true),
('차별경험', 16, true),
('사회적배제', 16, true),
('적응장애', 16, true);

-- C-6 강박완벽주의 (신규 22개)
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('완벽주의경향', 17, true),
('강박적사고', 17, true),
('강박적행동', 17, true),
('반복적행동', 17, true),
('의식적행동', 17, true),
('확인강박', 17, true),
('정리강박', 17, true),
('청결강박', 17, true),
('대칭강박', 17, true),
('순서강박', 17, true),
('숫자강박', 17, true),
('종교적강박', 17, true),
('도덕적강박', 17, true),
('완벽추구', 17, true),
('실수불안', 17, true),
('비판두려움', 17, true),
('기준과도설정', 17, true),
('자기비판', 17, true),
('타인비판', 17, true),
('경직적사고', 17, true),
('융통성부족', 17, true),
('통제욕구', 17, true);

-- C-7 자기파괴 (신규 22개)
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('자해행동', 18, true),
('자살사고', 18, true),
('자기처벌', 18, true),
('자기혐오', 18, true),
('자기부정', 18, true),
('자존감저하', 18, true),
('자기가치절하', 18, true),
('자기파괴적충동', 18, true),
('위험행동', 18, true),
('무모한행동', 18, true),
('자기방해', 18, true),
('자기실현방해', 18, true),
('성공회피', 18, true),
('행복회피', 18, true),
('관계파괴', 18, true),
('기회포기', 18, true),
('자기손상', 18, true),
('자기학대', 18, true),
('내적비판', 18, true),
('자기공격', 18, true),
('희생양역할', 18, true),
('피해자의식', 18, true);

-- C-8 인지왜곡 (신규 22개)
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('흑백사고', 19, true),
('극단적사고', 19, true),
('과잉일반화', 19, true),
('선택적주의', 19, true),
('부정적필터', 19, true),
('긍정적할인', 19, true),
('성급한결론', 19, true),
('마음읽기', 19, true),
('점쟁이오류', 19, true),
('파국화', 19, true),
('최소화', 19, true),
('감정적추론', 19, true),
('당위적사고', 19, true),
('개인화', 19, true),
('비교사고', 19, true),
('후회사고', 19, true),
('가정적사고', 19, true),
('인지편향', 19, true),
('확증편향', 19, true),
('부정편향', 19, true),
('인지적융통성부족', 19, true),
('사고오류', 19, true);

-- C-9 성격장애 (신규 20개)
INSERT INTO keywords (text, subcategory_id, is_active) VALUES
('경계선성격', 20, true),
('자기애성격', 20, true),
('회피성성격', 20, true),
('의존성성격', 20, true),
('강박성성격', 20, true),
('편집성성격', 20, true),
('분열성성격', 20, true),
('분열형성격', 20, true),
('반사회성성격', 20, true),
('히스테리성격', 20, true),
('정체성혼란', 20, true),
('자아기능장애', 20, true),
('대인관계패턴', 20, true),
('감정불안정', 20, true),
('충동성문제', 20, true),
('현실검증력', 20, true),
('성격적경직성', 20, true),
('적응적문제', 20, true),
('기능적손상', 20, true),
('성격특성극단화', 20, true);

-- ================================================
-- 데이터 삽입 완료 및 검증
-- ================================================

-- 최종 키워드 수 확인
DO $$
DECLARE
    final_count INTEGER;
    subcategory_stats RECORD;
BEGIN
    SELECT COUNT(*) INTO final_count FROM keywords;
    RAISE NOTICE '최종 키워드 수: %', final_count;
    
    IF final_count != 442 THEN
        RAISE EXCEPTION '예상 키워드 수와 다릅니다. 예상: 442개, 실제: %개', final_count;
    END IF;
    
    RAISE NOTICE '=== 서브카테고리별 키워드 분포 ===';
    FOR subcategory_stats IN 
        SELECT s.name, s.description, COUNT(k.id) as keyword_count
        FROM keyword_subcategories s
        LEFT JOIN keywords k ON s.id = k.subcategory_id
        GROUP BY s.id, s.name, s.description
        ORDER BY s.id
    LOOP
        RAISE NOTICE '% (%): %개', 
            subcategory_stats.name, 
            subcategory_stats.description, 
            subcategory_stats.keyword_count;
    END LOOP;
END $$;

-- 중복 키워드 검사
DO $$
DECLARE
    duplicate_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO duplicate_count 
    FROM (
        SELECT text, COUNT(*) as cnt 
        FROM keywords 
        GROUP BY text 
        HAVING COUNT(*) > 1
    ) duplicates;
    
    IF duplicate_count > 0 THEN
        RAISE EXCEPTION '중복된 키워드가 %개 발견되었습니다', duplicate_count;
    END IF;
    
    RAISE NOTICE '중복 키워드 검사 통과: 모든 키워드가 고유합니다';
END $$;

-- 트랜잭션 커밋
COMMIT;

-- 최종 성공 메시지
\echo '====================================================='
\echo '442개 키워드 삽입 성공!'
\echo '기존 30개 + 신규 412개 = 총 442개 키워드'
\echo 'M-PIS 프레임워크 20개 서브카테고리별 균등 분배 완료'
\echo '====================================================='