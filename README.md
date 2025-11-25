# Metadata AI Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-18.0-blue.svg)](https://reactjs.org/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.0-green.svg)](https://spring.io/projects/spring-boot)
[![AI](https://img.shields.io/badge/AI-Text2SQL-purple.svg)](https://github.com/back2zion/metadata-ai-platform)

## 📋 프로젝트 개요

K-BANK 데이터관리 솔루션 고도화 프로젝트의 완전한 개발 설계 패키지입니다. 메타데이터 관리, 데이터 흐름 시각화, AI 기반 자연어 질의 등을 포함한 엔터프라이즈 급 데이터 거버넌스 플랫폼을 위한 포괄적인 설계 문서를 제공합니다.

## 🎯 주요 기능

### 🏗️ 메타데이터 관리
- 테이블/컬럼 메타정보 통합 관리
- 스키마 수집 및 자동 동기화
- DDL 형상관리 및 배포 자동화
- 데이터 계보 추적 및 영향도 분석

### 📊 데이터 표준화
- 단어/용어/도메인/코드 표준 관리
- 표준화 승인 워크플로우
- 표준 준수율 실시간 모니터링
- 자동 검증 룰 엔진

### 🎨 데이터 모델링
- 시각적 ERD 편집기 (드래그 앤 드롭)
- 논리/물리 모델 매핑
- 모델 버전 관리
- 협업 기반 모델링 환경

### 🌊 데이터 흐름 시각화
- 소스코드 자동 분석 (Java/Python/SQL)
- 대화형 데이터 흐름도
- 실시간 영향도 분석
- CRUD 매트릭스 자동 생성

### 🤖 AI 기반 자연어 질의
- Text-to-SQL 자동 변환
- RAG 기반 메타데이터 검색
- 멀티 LLM 환경 지원 (GPT-4, Claude, LLaMA)
- 지능형 데이터 추천 시스템

## 🏛️ 아키텍처

### 시스템 아키텍처
```
Frontend (React 18 + TypeScript + Ant Design)
            ↕ HTTPS/WebSocket
API Gateway (Spring Cloud Gateway + JWT)
            ↕ gRPC/REST
Microservices (Spring Boot 3.0 + Python FastAPI)
            ↕ JPA/HTTP
Data Layer (EDB + Redis + Elasticsearch + Vector DB)
```

### 기술 스택
- **Frontend**: React 18, TypeScript, Ant Design, Redux Toolkit
- **Backend**: Spring Boot 3.0, Python FastAPI, Node.js
- **Database**: EDB, Redis, Elasticsearch, Chroma Vector DB
- **AI/ML**: OpenAI GPT-4, Anthropic Claude, LangChain, Sentence Transformers
- **Infrastructure**: Docker, Kubernetes, JEUS 8, Linux RHEL

## 📁 프로젝트 구조

```
K-BANK-Metadata-AI-Platform/
│
├── 📋 docs/                       # 📚 설계 문서
│   ├── PRD.md                     # 제품 요구사항 정의서
│   ├── TECHNICAL_ARCHITECTURE_DESIGN.md  # 기술 아키텍처 설계서
│   ├── DATABASE_DESIGN.md         # 데이터베이스 설계서
│   ├── API_DESIGN.md             # API 설계서
│   ├── SECURITY_COMPLIANCE_DESIGN.md    # 보안 컴플라이언스 설계서
│   ├── DEVELOPMENT_PLAN.md       # 개발 계획서
│   ├── SIDEBAR_MENU_PLAN.md      # 사이드바 메뉴 기획서
│   ├── SCREEN_WIREFRAME_PLAN.md  # 화면 와이어프레임 기획서
│   └── KBANK_CORPORATE_COLORS.md # K-BANK 브랜드 가이드
│
├── 🎨 frontend/                   # React 18 + TypeScript
│   ├── src/
│   │   ├── components/           # 재사용 컴포넌트 (Layout, AI, Custom)
│   │   ├── pages/               # 페이지 컴포넌트 (Dashboard, ETL, etc.)
│   │   ├── services/            # API 서비스 레이어
│   │   ├── contexts/            # React Context (Auth 등)
│   │   └── types/               # TypeScript 타입 정의
│   ├── public/                  # 정적 파일
│   ├── package.json             # 의존성 관리
│   └── tailwind.config.js       # TailwindCSS 설정
│
├── ⚡ backend/                    # FastAPI + Python 3.9+
│   ├── app/
│   │   ├── api/v1/              # REST API 엔드포인트
│   │   ├── application/         # Application Layer (DTO, Use Cases)
│   │   ├── domain/              # Domain Layer (Entities, Value Objects)
│   │   ├── services/            # Business Logic Services
│   │   ├── core/                # 설정 및 유틸리티
│   │   └── main.py              # FastAPI 애플리케이션 진입점
│   ├── data/kbank_synthetic/    # K-BANK 테스트 데이터
│   ├── tests/                   # 테스트 코드 (Unit, Integration, E2E)
│   └── requirements.txt         # Python 의존성
│
├── 🚀 scripts/                   # 실행 스크립트
│   ├── start-dev.sh             # 개발환경 시작
│   └── start.sh                 # 프로덕션 시작
│
├── 🐳 Docker & Configuration      # 컨테이너 설정
│   ├── Dockerfile               # 메인 Docker 이미지
│   ├── docker-compose.yml       # 전체 스택 orchestration
│   └── requirements.txt         # 루트 의존성 파일
│
├── 📄 Project Files              # 프로젝트 파일
│   ├── README.md                # 프로젝트 가이드 (현재 파일)
│   └── rfp.txt                  # 원본 RFP 요구사항
│
└── 🔧 Configuration              # 설정 파일들
    └── .gitignore               # Git 무시 파일
```

## 🚀 빠른 시작

### 필요 조건
- Node.js 18+
- Python 3.9+
- Docker & Docker Compose

### 설치 및 실행

1. **저장소 클론**
```bash
git clone https://github.com/back2zion/metadata-ai-platform.git
cd metadata-ai-platform
```

2. **프론트엔드 실행**
```bash
cd frontend
npm install
npm start
```

3. **백엔드 실행**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

4. **브라우저에서 접속**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📚 문서

### 설계 문서
- [제품 요구사항 정의서 (PRD)](./PRD.md)
- [기술 아키텍처 설계서](./TECHNICAL_ARCHITECTURE_DESIGN.md)
- [데이터베이스 설계서](./DATABASE_DESIGN.md)
- [API 설계서](./API_DESIGN.md)
- [보안 컴플라이언스 설계서](./SECURITY_COMPLIANCE_DESIGN.md)
- [개발 계획서](./DEVELOPMENT_PLAN.md)

### UI/UX 기획
- [사이드바 메뉴 기획서](./SIDEBAR_MENU_PLAN.md)
- [화면 와이어프레임 기획서](./SCREEN_WIREFRAME_PLAN.md)

## 🎯 개발 로드맵

### Phase 1: 핵심 인프라 및 메타데이터 관리 (Month 1-2)
- ✅ 시스템 인프라 구축
- ✅ 메타데이터 관리 시스템
- ✅ 사용자 인증 및 권한 관리

### Phase 2: 데이터 표준 관리 및 모델링 (Month 2-3)
- ✅ 데이터 표준 관리
- ✅ ERD 모델링 도구
- ✅ 품질 관리 시스템

### Phase 3: 데이터 흐름 시각화 (Month 3-4)
- ✅ 흐름 분석 엔진
- ✅ 시각화 대시보드
- ✅ 영향도 분석

### Phase 4: AI 환경 및 자연어 질의 (Month 4-5)
- ✅ AI 플랫폼 구축
- ✅ Text-to-SQL 엔진
- ✅ AI 어시스턴트

### Phase 5: 시스템 연계 및 통합 (Month 5-6)
- ✅ 외부 시스템 연계
- ✅ 모니터링 시스템
- ✅ 운영 체계 구축

## 🔐 보안 및 컴플라이언스

- **인증**: SAML 2.0 기반 SSO, JWT 토큰
- **권한**: RBAC (Role-Based Access Control)
- **암호화**: TLS 1.3, AES-256 데이터 암호화
- **감사**: 전체 사용자 활동 로깅
- **컴플라이언스**: 금융 보안 표준 준수

## 📊 성능 지표

- **시스템 가용성**: 99.9% 이상
- **응답 시간**: 3초 이내 (95% 요청)
- **동시 사용자**: 1,200명 지원
- **AI 질의 정확도**: 85% 이상
- **표준화율**: 90% 이상

## 🤝 기여 방법

1. Fork 프로젝트
2. Feature 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 Push (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 연락처

프로젝트 관련 문의: [GitHub Issues](https://github.com/back2zion/metadata-ai-platform/issues)

---

**⚡ Enterprise-grade Data Governance Platform with AI-powered Natural Language Querying**