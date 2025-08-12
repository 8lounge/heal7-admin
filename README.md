# 🏥 HEAL7 관리자 시스템

## 📋 프로젝트 개요
HEAL7 관리자 대시보드 - 사주명리학 기반 진단 시스템의 백엔드 관리 도구

## 🏗️ 아키텍처
- **프론트엔드**: Next.js 14 + React 18 + Tailwind CSS
- **백엔드**: FastAPI + PostgreSQL + Redis
- **배포**: GitHub Actions + nginx

## 🚀 빠른 시작

### 로컬 개발
```bash
# 프론트엔드
cd frontend
npm install
npm run dev

# 백엔드
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### GitHub Actions 빌드
1. 코드 수정 후 푸시
2. GitHub Actions 자동 빌드
3. 빌드 결과물 다운로드
```bash
./download-build-artifacts.sh
```

## 📁 프로젝트 구조
```
heal7-admin/
├── frontend/          # Next.js 프론트엔드
│   ├── src/
│   ├── public/
│   └── package.json
├── backend/           # FastAPI 백엔드
│   ├── routes/
│   ├── services/
│   └── main.py
└── logs/              # 로그 파일
```

## 🔧 주요 기능
- 🔮 사주명리학 분석 관리
- 📊 키워드 매트릭스 시각화
- 📝 설문 시스템 관리
- 📈 실시간 분석 대시보드

## 🌐 서비스 포트
- **프론트엔드**: 5173 (admin.heal7.com)
- **백엔드 API**: 8001 (/admin-api/ 프리픽스)

## 📝 라이센스
HEAL7 Internal Use Only