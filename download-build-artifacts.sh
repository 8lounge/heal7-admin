#!/bin/bash

# HEAL7 GitHub Actions 빌드 결과물 자동 다운로드 스크립트
# 사용법: ./download-build-artifacts.sh [repo-owner] [repo-name] [workflow-run-id]

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 기본값 설정
REPO_OWNER=${1:-"heal7"}
REPO_NAME=${2:-"heal7-project"}
WORKFLOW_RUN_ID=$3

echo -e "${BLUE}🚀 HEAL7 빌드 결과물 다운로드 시작${NC}"
echo "========================================"

# GitHub CLI 설치 확인
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh)가 설치되지 않았습니다.${NC}"
    echo -e "${YELLOW}💡 설치 방법:${NC}"
    echo "   sudo apt update && sudo apt install gh"
    echo "   또는 https://cli.github.com/ 참조"
    exit 1
fi

# GitHub 인증 확인
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ GitHub 인증이 필요합니다.${NC}"
    echo -e "${YELLOW}💡 인증 방법:${NC}"
    echo "   gh auth login"
    exit 1
fi

# 워크플로우 실행 ID가 제공되지 않은 경우 최신 실행 찾기
if [ -z "$WORKFLOW_RUN_ID" ]; then
    echo -e "${YELLOW}🔍 최신 워크플로우 실행 검색 중...${NC}"
    
    WORKFLOW_RUN_ID=$(gh run list \
        --repo "$REPO_OWNER/$REPO_NAME" \
        --workflow "HEAL7 Build and Deploy" \
        --status completed \
        --limit 1 \
        --json databaseId \
        --jq '.[0].databaseId')
    
    if [ -z "$WORKFLOW_RUN_ID" ]; then
        echo -e "${RED}❌ 완료된 워크플로우 실행을 찾을 수 없습니다.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 워크플로우 실행 ID: $WORKFLOW_RUN_ID${NC}"
fi

# 다운로드 디렉토리 생성
DOWNLOAD_DIR="/home/ubuntu/build-artifacts/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DOWNLOAD_DIR"
cd "$DOWNLOAD_DIR"

echo -e "${BLUE}📁 다운로드 위치: $DOWNLOAD_DIR${NC}"

# 사용 가능한 아티팩트 목록 가져오기
echo -e "${YELLOW}🔍 사용 가능한 아티팩트 검색 중...${NC}"
ARTIFACTS=$(gh run view "$WORKFLOW_RUN_ID" --repo "$REPO_OWNER/$REPO_NAME" --json artifacts --jq '.artifacts[].name')

if [ -z "$ARTIFACTS" ]; then
    echo -e "${RED}❌ 다운로드할 아티팩트가 없습니다.${NC}"
    exit 1
fi

echo -e "${GREEN}📦 발견된 아티팩트:${NC}"
echo "$ARTIFACTS" | while read -r artifact; do
    echo "  - $artifact"
done

# 각 아티팩트 다운로드
echo -e "${YELLOW}⬇️  아티팩트 다운로드 시작...${NC}"
echo "$ARTIFACTS" | while read -r artifact; do
    if [ -n "$artifact" ]; then
        echo -e "${BLUE}📥 다운로드 중: $artifact${NC}"
        gh run download "$WORKFLOW_RUN_ID" \
            --repo "$REPO_OWNER/$REPO_NAME" \
            --name "$artifact" \
            --dir "$DOWNLOAD_DIR/$artifact"
    fi
done

# 빌드 결과물 압축 해제 및 배포 준비
echo -e "${YELLOW}📦 압축 해제 및 배포 준비...${NC}"

# heal7-admin 빌드 처리
if [ -d "$DOWNLOAD_DIR/heal7-admin-build-18" ] || [ -d "$DOWNLOAD_DIR/heal7-admin-build-20" ]; then
    echo -e "${BLUE}🔧 heal7-admin 빌드 처리 중...${NC}"
    
    # Node.js 20 빌드를 우선 사용 (있는 경우)
    ADMIN_BUILD_DIR="$DOWNLOAD_DIR/heal7-admin-build-20"
    if [ ! -d "$ADMIN_BUILD_DIR" ]; then
        ADMIN_BUILD_DIR="$DOWNLOAD_DIR/heal7-admin-build-18"
    fi
    
    if [ -d "$ADMIN_BUILD_DIR" ]; then
        cd "$ADMIN_BUILD_DIR"
        find . -name "*.tar.gz" -exec tar -xzf {} \;
        
        # 배포 디렉토리로 복사
        if [ -d ".next" ]; then
            echo -e "${GREEN}✅ heal7-admin .next 디렉토리 준비 완료${NC}"
            mkdir -p "/home/ubuntu/deployed-builds/heal7-admin"
            cp -r .next "/home/ubuntu/deployed-builds/heal7-admin/"
            
            if [ -d "out" ]; then
                cp -r out "/home/ubuntu/deployed-builds/heal7-admin/"
            fi
        fi
    fi
fi

# heal7-index 빌드 처리
if [ -d "$DOWNLOAD_DIR/heal7-index-build" ]; then
    echo -e "${BLUE}🔧 heal7-index 빌드 처리 중...${NC}"
    
    cd "$DOWNLOAD_DIR/heal7-index-build"
    find . -name "*.tar.gz" -exec tar -xzf {} \;
    
    # 배포 디렉토리로 복사
    if [ -d "dist" ]; then
        echo -e "${GREEN}✅ heal7-index dist 디렉토리 준비 완료${NC}"
        mkdir -p "/home/ubuntu/deployed-builds/heal7-index"
        cp -r dist "/home/ubuntu/deployed-builds/heal7-index/"
    fi
fi

echo ""
echo -e "${GREEN}🎉 빌드 결과물 다운로드 및 배포 준비 완료!${NC}"
echo "========================================"
echo -e "${BLUE}📍 다운로드 위치:${NC} $DOWNLOAD_DIR"
echo -e "${BLUE}📍 배포 준비 위치:${NC} /home/ubuntu/deployed-builds/"
echo ""
echo -e "${YELLOW}📝 다음 단계:${NC}"
echo "1. 현재 서비스 중지"
echo "2. 빌드 결과물을 프로덕션 디렉토리로 복사"
echo "3. 서비스 재시작"
echo ""
echo -e "${BLUE}💡 빠른 배포 명령어:${NC}"
echo "   sudo systemctl stop nginx"
echo "   cp -r /home/ubuntu/deployed-builds/heal7-admin/.next /home/ubuntu/project/heal7-admin/frontend/"
echo "   cp -r /home/ubuntu/deployed-builds/heal7-index/dist /home/ubuntu/project/heal7-index/frontend/"
echo "   sudo systemctl start nginx"