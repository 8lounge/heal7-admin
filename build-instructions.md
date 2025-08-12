# 🚀 HEAL7 Admin GitHub Actions 빌드 가이드

## 📋 개요
로컬 서버의 메모리 제약으로 인해 GitHub Actions를 활용한 원격 빌드 시스템을 구축했습니다.

## 🎯 빌드 프로세스

### 1단계: 코드 푸시
```bash
git add .
git commit -m "Your commit message"
git push origin master
```

### 2단계: GitHub Actions 자동 빌드
- 푸시 시 자동으로 빌드 시작
- Node.js 18/20 환경에서 매트릭스 빌드
- 4GB 메모리 할당으로 안정적인 빌드

### 3단계: GitHub 인증 (최초 1회만)
```bash
# 인증 토큰 방식 (권장)
gh auth login --with-token

# 또는 브라우저 인증
gh auth login
```

### 4단계: 빌드 결과물 다운로드
```bash
# 최신 빌드 자동 다운로드
./download-build-artifacts.sh

# 특정 워크플로우 실행 다운로드
./download-build-artifacts.sh your-username heal7-admin 12345
```

### 5단계: 배포
```bash
# 서비스 중지
sudo systemctl stop nginx

# 빌드 파일 교체
cp -r /home/ubuntu/deployed-builds/heal7-admin/.next /home/ubuntu/project/heal7-admin/frontend/

# Next.js 서버 재시작
cd /home/ubuntu/project/heal7-admin/frontend
npm run start &

# nginx 재시작
sudo systemctl start nginx
```

## 🔧 트러블슈팅

### GitHub 인증 문제
```bash
# 인증 상태 확인
gh auth status

# 재인증
gh auth logout
gh auth login
```

### 빌드 실패 시
1. GitHub Actions 로그 확인
2. package.json 의존성 검토
3. TypeScript 에러 확인

### 아티팩트 다운로드 실패 시
```bash
# 사용 가능한 워크플로우 확인
gh run list --repo your-username/heal7-admin

# 특정 실행 상세 정보
gh run view RUN_ID --repo your-username/heal7-admin
```

## 📊 빌드 상태 확인
- GitHub 저장소의 Actions 탭에서 실시간 빌드 상태 확인
- 빌드 완료 시 아티팩트 다운로드 링크 제공

## 💡 팁
1. **퍼블릭 저장소**: 무제한 무료 빌드
2. **프라이빗 저장소**: 월 2,000분 (33시간) 무료
3. **빌드 캐시**: 의존성 설치 시간 단축
4. **매트릭스 빌드**: Node.js 18/20 동시 빌드로 호환성 확인

## 🔄 자동화 스크립트
- `download-build-artifacts.sh`: 빌드 결과물 자동 다운로드
- `build-and-deploy.yml`: GitHub Actions 워크플로우
- 빌드 통계 및 배포 가이드 자동 생성