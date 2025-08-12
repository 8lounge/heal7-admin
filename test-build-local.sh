#!/bin/bash

# 로컬 빌드 테스트 스크립트 (GitHub Actions 시뮬레이션)

echo "🧪 HEAL7 Admin 로컬 빌드 테스트"
echo "================================"
echo ""

# 현재 메모리 상태 출력
echo "📊 현재 시스템 메모리 상태:"
free -h
echo ""

# Node.js 메모리 제한 설정
export NODE_OPTIONS='--max-old-space-size=1024'
echo "🔧 Node.js 메모리 제한: 1GB (로컬 테스트용)"
echo ""

# 프론트엔드 디렉토리로 이동
cd /home/ubuntu/project/heal7-admin/frontend

# 현재 의존성 상태 확인
echo "📦 package.json 확인 중..."
if [ -f "package.json" ]; then
    echo "✅ package.json 존재"
    echo "   프로젝트: $(grep -o '"name": "[^"]*"' package.json | cut -d'"' -f4)"
    echo "   버전: $(grep -o '"version": "[^"]*"' package.json | cut -d'"' -f4)"
else
    echo "❌ package.json 없음"
    exit 1
fi
echo ""

# node_modules 상태 확인
echo "📁 의존성 설치 상태 확인..."
if [ -d "node_modules" ]; then
    NODE_MODULES_SIZE=$(du -sh node_modules | cut -f1)
    echo "✅ node_modules 존재 (크기: $NODE_MODULES_SIZE)"
else
    echo "❌ node_modules 없음 - 의존성 설치 필요"
    echo "🔄 npm install 실행 중..."
    
    # 메모리 사용량 모니터링
    (
        while true; do
            MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
            if [ "$MEMORY_USAGE" -gt 85 ]; then
                echo "⚠️  메모리 사용량 위험: ${MEMORY_USAGE}%"
            fi
            sleep 2
        done
    ) &
    MONITOR_PID=$!
    
    # 실제 설치 시도
    timeout 300 npm install --prefer-offline --no-audit
    INSTALL_RESULT=$?
    
    # 모니터링 프로세스 종료
    kill $MONITOR_PID 2>/dev/null
    
    if [ $INSTALL_RESULT -ne 0 ]; then
        echo "❌ npm install 실패 (메모리 부족 또는 타임아웃)"
        echo ""
        echo "🔄 대안: GitHub Actions 빌드 사용을 권장합니다"
        exit 1
    fi
fi
echo ""

# TypeScript 컴파일 테스트
echo "🔍 TypeScript 컴파일 테스트..."
if npm run type-check; then
    echo "✅ TypeScript 컴파일 성공"
else
    echo "❌ TypeScript 컴파일 실패"
    echo "🔧 타입 오류를 수정하고 다시 시도하세요"
    exit 1
fi
echo ""

# Next.js 빌드 시도
echo "🏗️  Next.js 빌드 테스트 시작..."
echo "⏰ 예상 시간: 5-15분 (메모리 상황에 따라)"
echo ""

# 빌드 시작 시간 기록
BUILD_START_TIME=$(date +%s)

# 메모리 모니터링 백그라운드 프로세스
(
    MAX_MEMORY=0
    while kill -0 $$ 2>/dev/null; do
        CURRENT_MEMORY=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
        if [ "$CURRENT_MEMORY" -gt "$MAX_MEMORY" ]; then
            MAX_MEMORY=$CURRENT_MEMORY
        fi
        
        if [ "$CURRENT_MEMORY" -gt 90 ]; then
            echo "🚨 메모리 사용량 위험: ${CURRENT_MEMORY}%"
        elif [ "$CURRENT_MEMORY" -gt 80 ]; then
            echo "⚠️  메모리 사용량 높음: ${CURRENT_MEMORY}%"
        fi
        
        sleep 5
    done
    echo "📊 최대 메모리 사용량: ${MAX_MEMORY}%"
) &
MEMORY_MONITOR_PID=$!

# 실제 빌드 실행 (타임아웃 20분)
timeout 1200 npm run build
BUILD_RESULT=$?

# 메모리 모니터링 종료
kill $MEMORY_MONITOR_PID 2>/dev/null

# 빌드 종료 시간 계산
BUILD_END_TIME=$(date +%s)
BUILD_DURATION=$((BUILD_END_TIME - BUILD_START_TIME))
BUILD_MINUTES=$((BUILD_DURATION / 60))
BUILD_SECONDS=$((BUILD_DURATION % 60))

echo ""
echo "🏁 빌드 테스트 결과"
echo "=================="
echo "⏱️  소요 시간: ${BUILD_MINUTES}분 ${BUILD_SECONDS}초"

if [ $BUILD_RESULT -eq 0 ]; then
    echo "✅ 로컬 빌드 성공!"
    echo ""
    
    # 빌드 결과물 확인
    if [ -d ".next" ]; then
        NEXT_SIZE=$(du -sh .next | cut -f1)
        echo "📁 .next 디렉토리 크기: $NEXT_SIZE"
    fi
    
    if [ -d "out" ]; then
        OUT_SIZE=$(du -sh out | cut -f1)
        echo "📁 out 디렉토리 크기: $OUT_SIZE"
    fi
    
    echo ""
    echo "🎉 로컬 환경에서도 빌드가 가능합니다!"
    echo "💡 하지만 GitHub Actions를 사용하면 더 빠르고 안정적입니다."
    
elif [ $BUILD_RESULT -eq 124 ]; then
    echo "❌ 빌드 타임아웃 (20분 초과)"
    echo ""
    echo "🔧 해결 방안:"
    echo "1. 물리 메모리 증설"
    echo "2. GitHub Actions 빌드 사용 (권장)"
    
else
    echo "❌ 빌드 실패 (메모리 부족 가능성 높음)"
    echo ""
    echo "🔧 해결 방안:"
    echo "1. GitHub Actions 빌드 사용 (권장)"
    echo "2. 스왑 메모리 활용도 증가"
    echo "3. 빌드 과정 최적화"
fi

echo ""
echo "🚀 GitHub Actions 빌드 사용을 강력히 권장합니다:"
echo "   - 7GB RAM 환경"
echo "   - 3-5분 빌드 시간"
echo "   - 100% 안정성"
echo "   - 무료 (퍼블릭 저장소)"