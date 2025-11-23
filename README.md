# 서울아산병원 통합 데이터 플랫폼 (IDP) POC v2.0

## 🏥 프로젝트 개요

서울아산병원 AI 기반 통합 데이터 분석 플랫폼 POC 프로젝트입니다. React 기반 프론트엔드와 FastAPI 백엔드로 구성되어 있으며, HumanLayer를 활용한 Human-in-the-Loop AI 에이전트를 통합하여 의료 데이터 분석 및 의사결정을 지원합니다.

## ✨ 주요 업데이트 (v2.0)

- **React 프론트엔드**: Streamlit에서 React + TypeScript로 전면 전환
- **통합 POC 컴포넌트**: 기존 POC 폴더의 모든 기능 통합
- **향상된 UI/UX**: Ant Design 기반 전문적인 엔터프라이즈 UI
- **LangGraph 에이전트**: 의료 전문 AI 에이전트 시스템
- **GraphRAG 통합**: 지식 그래프 기반 검색 증강 생성

## 🚀 주요 기능 (7개 SFR)

### 구현 완료 ✅

1. **SFR-002**: 분석 데이터마트 설계 및 구축
   - Star Schema 기반 데이터마트 관리
   - 데이터 품질 모니터링
   - 자동 갱신 스케줄링

2. **SFR-004**: OLAP 다차원 분석 포탈
   - 슬라이스 & 다이스 분석
   - 피벗 테이블
   - 드릴다운/롤업 기능
   - 다차원 시각화

3. **SFR-005**: ETL 파이프라인 개발
   - 실시간 파이프라인 모니터링
   - 작업 스케줄링
   - 병렬 처리 최적화

4. **SFR-006**: AI 데이터 분석환경 제공
   - JupyterHub 컨테이너 환경
   - GPU 리소스 관리 (RTX 3090)
   - 분석 템플릿 제공

5. **SFR-007**: CDW 데이터 추출 및 Text2SQL 🔥
   - 자연어 → SQL 변환 (한국어 지원)
   - 연구 데이터셋 추출
   - 데이터 카탈로그

### 개발 예정

6. **SFR-001**: 공통 요구사항 (플랫폼 Foundation)
7. **SFR-003**: BI (Business Intelligence) 기능

## 🛠 기술 스택

### Frontend (React)
- **React 18** + **TypeScript**
- **Ant Design 5**: 엔터프라이즈 UI 컴포넌트
- **TailwindCSS 3**: 유틸리티 기반 CSS 프레임워크
- **React Query**: 서버 상태 관리
- **Recharts & Plotly**: 데이터 시각화
- **AG-Grid**: 고성능 데이터 그리드
- **Lucide React**: 모던 아이콘 라이브러리

### Backend
- **FastAPI**: REST API 서버
- **PostgreSQL**: 주 데이터베이스
- **Redis**: 캐싱 및 세션 관리
- **Qdrant**: 벡터 데이터베이스 (RAG)
- **DuckDB**: In-process OLAP

### AI/ML
- **LangChain & LangGraph**: LLM 오케스트레이션
- **HumanLayer**: Human-in-the-Loop AI 에이전트
- **OpenAI/Anthropic**: LLM 서비스
- **GraphRAG**: 지식 그래프 기반 검색

## 📁 프로젝트 구조

```
asan/
├── frontend/                  # React 프론트엔드
│   ├── src/
│   │   ├── pages/            # 페이지 컴포넌트
│   │   │   ├── Dashboard.tsx
│   │   │   ├── DataMart.tsx
│   │   │   ├── OLAP.tsx
│   │   │   ├── ETL.tsx
│   │   │   ├── AIEnvironment.tsx
│   │   │   ├── CDWResearch.tsx
│   │   │   └── AIAgents.tsx
│   │   ├── components/       # 재사용 컴포넌트
│   │   ├── services/         # API 서비스
│   │   ├── contexts/         # React Context
│   │   └── index.css         # TailwindCSS 메인 스타일
│   ├── tailwind.config.js    # TailwindCSS 설정
│   ├── postcss.config.js     # PostCSS 설정
│   └── package.json
├── backend/                   # FastAPI 백엔드
│   ├── app/
│   │   ├── api/v1/          # API 엔드포인트
│   │   ├── services/        # 비즈니스 로직
│   │   │   ├── humanlayer_service.py
│   │   │   ├── text2sql_service.py
│   │   │   ├── langgraph_agent.py
│   │   │   └── graph_rag.py
│   │   └── core/            # 설정 및 DB
│   └── requirements.txt
├── humanlayer/               # HumanLayer 클론
├── docker-compose.yml        # Docker 구성
└── README.md
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone https://github.com/back2zion/asan.git
cd asan

# Python 가상환경 (Backend)
source .venv/bin/activate
uv pip install -r backend/requirements.txt

# Node.js 의존성 (Frontend)
cd frontend
npm install

# 환경 변수 설정
cd ..
cp .env.example .env
# .env 파일을 편집하여 API 키 등 설정
```

### 2. 개발 모드 실행

#### 방법 1: 개별 실행

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm start
```

#### 방법 2: 통합 실행 스크립트

```bash
./start-dev.sh
```

### 3. Docker Compose 실행

```bash
# 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

## 🔗 접속 URL

- **React 대시보드**: http://localhost:3000
- **FastAPI 문서**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Qdrant**: http://localhost:6333/dashboard

## 🎯 주요 기능 사용법

### Text2SQL (SFR-007)

자연어 질의를 SQL로 자동 변환:

1. CDW 연구 메뉴 접속
2. 한국어로 질문 입력 (예: "2023년 당뇨병 환자 수는?")
3. AI가 SQL 생성 및 실행
4. 결과 테이블 및 시각화 확인

### OLAP 분석 (SFR-004)

다차원 데이터 분석:

1. OLAP 메뉴 접속
2. 차원(Dimension)과 지표(Metric) 선택
3. 슬라이스/다이스, 드릴다운 수행
4. 인터랙티브 차트로 결과 확인

### AI 에이전트 (HumanLayer 통합)

Human-in-the-Loop AI 작업:

1. AI 에이전트 메뉴 접속
2. 작업 생성 (데이터 분석, ETL, 쿼리 생성 등)
3. 승인 대기 목록에서 검토
4. 승인/거부 결정
5. Claude Code 세션 관리

## 🤖 LangGraph 의료 에이전트

```python
# 의료 전문 AI 에이전트 사용 예시
from backend.app.services.langgraph_agent import medical_agent

# 환자 질의
result = await medical_agent.process_query(
    query="고혈압이 있는데 어떤 약을 복용해야 하나요?",
    user_type="patient"
)

# 의사 질의
result = await medical_agent.process_query(
    query="ACE 억제제와 ARB의 차이점을 알려주세요",
    user_type="doctor"
)
```

## 📊 GraphRAG 지식 그래프

- 의료 지식베이스 구축
- 온톨로지 기반 구조화
- 벡터 + 그래프 하이브리드 검색
- 컨텍스트 증강 생성

## 🔒 보안 고려사항

- 의료 데이터 비식별화 처리
- OWASP 보안 가이드라인 준수
- API 키 환경 변수 관리
- 역할 기반 접근 제어 (RBAC)
- 감사 로그 및 모니터링

## 📝 개발 로드맵

### 완료 ✅
- [x] POC 컴포넌트 통합
- [x] React 프론트엔드 전환
- [x] 7개 SFR 페이지 구현
- [x] TailwindCSS 3 및 PostCSS 설정
- [x] HumanLayer 에이전트 통합
- [x] LangGraph 의료 에이전트
- [x] Text2SQL 한국어 지원

### 진행 중 🔄
- [ ] GraphRAG 최적화
- [ ] 실제 의료 데이터 연동
- [ ] 프로덕션 배포 준비

### 계획 📋
- [ ] SFR-001 공통 요구사항
- [ ] SFR-003 BI 대시보드
- [ ] 멀티모달 AI (영상+텍스트)
- [ ] 실시간 알림 시스템

## 🛠 개발 명령어

### Frontend

```bash
cd frontend
npm start          # 개발 서버 시작
npm run build      # 프로덕션 빌드
npm test          # 테스트 실행
```

### Backend

```bash
cd backend
uvicorn app.main:app --reload  # 개발 서버
pytest                          # 테스트 실행
alembic upgrade head           # DB 마이그레이션
```

### Docker

```bash
docker-compose up -d           # 백그라운드 실행
docker-compose logs -f backend # 백엔드 로그
docker-compose logs -f frontend # 프론트엔드 로그
docker-compose down -v         # 완전 종료
```

## 🤝 기여 방법

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📜 라이센스

이 프로젝트는 Apache 2.0 라이센스를 따릅니다.

## 📧 문의

- 프로젝트 관련: datastreams@example.com
- 기술 지원: support@humanlayer.dev
- 의료 AI 자문: ai-team@amc.seoul.kr

## 🙏 감사의 말

- HumanLayer 팀의 Human-in-the-Loop AI 프레임워크
- 서울아산병원 데이터 혁신팀
- AI-Hub 헬스케어 데이터셋
- React 및 FastAPI 커뮤니티

---

**© 2025 Seoul Asan Medical Center IDP POC Project v2.0**
**Powered by React + FastAPI + HumanLayer**