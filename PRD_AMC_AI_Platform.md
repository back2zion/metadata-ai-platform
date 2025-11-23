# 서울아산병원 AI 데이터 분석 플랫폼 PRD (Product Requirements Document)

## 1. 프로젝트 개요

### 1.1 프로젝트 명
서울아산병원 AI 기반 통합 데이터 분석 플랫폼 구축

### 1.2 프로젝트 목표
상용 솔루션과 자체 개발 AI 기술을 결합한 통합 포털을 구축하여, 의료진과 연구진의 데이터 기반 의사결정을 지원하는 차세대 분석 환경 제공

### 1.3 핵심 가치 제안
- **Best-of-Breed 전략:** 검증된 상용 솔루션(BI, ETL, DM)과 최첨단 AI 기술의 시너지
- **통합 포털:** React 기반 단일 웹 인터페이스를 통해 모든 데이터 기능에 Seamless 접근
- **AI 기반 혁신:** Text2SQL, GraphRAG 등 병원 특화 AI 기능을 통한 연구 및 분석 효율 극대화
- **지능형 데이터 패브릭:** LangGraph 기반 에이전트 시스템을 통한 데이터 민주화 실현

## 2. 기능 요구사항 (RFP 기반)

### 2.1 AI 데이터 분석환경 제공 (SFR-006)
(기존 내용과 동일)
#### 2.1.1 사용자 분석 환경
**기본 분석 도구**
- JupyterLab 기반 웹 분석 환경
- 파이썬, 스칼라 등 다양한 분석 언어 지원
- 딥러닝/머신러닝 라이브러리 통합 (TensorFlow, PyTorch, scikit-learn 등)
- GPU 연산 지원 아키텍처
**리소스 관리**
- 프로젝트별 CPU/Memory/GPU 자원 할당
- 실시간 사용량 모니터링 대시보드
- 사용자별 권한 기반 자원 접근 제어
**템플릿 기반 분석**
- 탐색적 데이터 분석 템플릿
- 자연어 분석 템플릿
- 공간분석 기능 템플릿
- 의료 데이터 전용 분석 템플릿
#### 2.1.2 생성형 AI 분석 기능
**핵심 LLM 통합**
- SOTA 오픈소스 LLM 도입 (Qwen3-8B 등)
- GraphRAG 기반 지식 그래프 검색 증강 생성
- 온톨로지(OWL) 표준 기반 구조화
**에이전트 시스템**
- LangGraph 프레임워크 기반
- 다중 LLM 및 도구 상호작용
- 지능형 데이터 패브릭 아키텍처
**특화 기능**
- 회의록, 처방전, 기록지 자동 메타화
- 진료데이터와 EDW 데이터 연계
- R&D 보고서, 내부방침 등 학습데이터 전처리
- X-RAY 이미지 검색 기능 (멀티모달 시범적용)
- 온톨로지 기반 Text to SQL 변환

### 2.2 AI 활용을 위한 설계 (AAR-001)
(기존 내용과 동일)
#### 2.2.1 아키텍처 설계
**모듈형 구조**
- 마이크로서비스 아키텍처 기반
- MCP(Machine learning/AI Control Platform) 구조
- AI 기능 추가/개선 용이성 확보
**인프라 확장성**
- GPU, 고속 저장소, AI 전용 노드 지원
- 클러스터링 지원 인프라
- Docker/Kubernetes 기반 컨테이너 관리
**계층별 AI 연계**
- 데이터 취득/저장/분석/시각화 각 계층 API 연결성
- 예측 모델 변경/튜닝 유연성
- 지식그래프 기반 시맨틱 검색

### 2.3 AI 활용 기능 개발 (AAR-002)
(기존 내용과 동일)
#### 2.3.1 기본 AI 기능
- 질의응답 시스템
- 텍스트 마이닝
- 예측 모델링
- 이미지 분석
- 자연어 기반 데이터 탐색 및 요약
#### 2.3.2 병원 운영 AI 기능
- 병상 배정 최적화
- 검사 우선순위 판단
- 진료 스케줄링 자동화
- 환자 흐름 최적화
#### 2.3.3 고급 RAG 및 검색 기능
**문서 처리**
- PDF, HWP/HWPX, DOC/DOCX 자동 파싱
- 텍스트, 표, 이미지 추출
- 문서 구조 및 관계 파악
- 메타정보 자동 생성
**온톨로지 구축**
- 개체 및 관계 정보 추출
- 문서/개체 간 관계 및 인과성 추출
- 데이터 카탈로그 연계
#### 2.3.4 AI 고급 기능
- 생성형 AI 기반 문서 요약/레포트 작성
- EMR/검사기록/진료기록에서 인사이트 추출
- X-ray, CT 이미지 기반 예측 모델
- 멀티모달 AI (텍스트+영상+문서) 통합 분석

### 2.4 AI 자원 관리 (AAR-003)
(기존 내용과 동일)
#### 2.4.1 모델 운영 관리
- 지속적 성능 평가 (90% 이상 정확도 유지)
- Fine-tuning 및 RAG corpus 갱신
- 학습/응답 이력 저장 및 성능 비교
- 모델 버전 관리 및 복원 시스템
#### 2.4.2 자원 모니터링
- GPU/CPU/Memory 실시간 모니터링
- 사용량 기반 스케줄링
- 우선순위 설정 시스템
#### 2.4.3 장애 대응
- 모델 장애 시 대체 응답 시나리오
- 학습데이터/모델 백업 체계

## 3. 비기능 요구사항 (RFP 기반)

### 3.1 성능 요구사항 (PER)
- 생성형 AI 시스템 정확도 90% 이상
- 실시간 자원 모니터링 및 알림
- 멀티모달 검색 응답 시간 5초 이내
- 10초 이상 소요되는 작업에 대한 사전 경고 및 비동기 처리

### 3.2 보안 요구사항 (SER)
- 의료법, 개인정보보호법 등 관련 법령 및 병원 정보보호 정책 완벽 준수
- **OWASP 보안 가이드라인 준수**
- **입력 데이터 검증 및 SQL 인젝션, XSS, CSRF 방지**
- **AES-256** 표준 암호화 알고리즘 적용
- **의료 데이터 접근 로깅 및 감사 추적** (최소 6개월 이상 보관)
- 역할 기반 접근 제어(RBAC) 및 제로 트러스트 원칙 적용
- 안전한 세션 관리 및 토큰 기반 인증 보안

### 3.3 확장성 요구사항
- 클라우드 네이티브 아키텍처 기반 탄력적 자원 확장
- 새로운 AI 모델 및 상용 솔루션 추가가 용이한 플러그인 구조
- 다양한 의료 시스템(EMR, PACS 등)과의 표준 API(HL7, FHIR) 연계 지원

### 3.4 개발 품질 요구사항 (QUR & TER)
#### 3.4.1 테스트 주도 개발 (TDD)
- **단위 테스트 커버리지 85% 이상 유지**
- **CI/CD 파이프라인 연계 통합/E2E 테스트 자동화**
- **의료 AI 모델 정확도 및 편향성 검증 테스트 케이스 필수 구현**
- **성능 및 부하 테스트 자동화 (PER-001 충족 검증)**
- BDD(Behavior-Driven Development) 적용 검토
#### 3.4.2 유지보수 용이성
- **클린 아키텍처 (Hexagonal Architecture) 적용**
- **SOLID 원칙 및 의존성 주입(DI) 패턴 적용**
- **자동화된 코드 품질 관리 (SonarQube, ESLint)**
- **API 문서화 자동화 (OpenAPI/Swagger)**
- **UV 기반 Python 가상환경 표준화 (빠른 의존성 해결 및 재현성)**

## 4. 사용자 인터페이스 (UI/UX)

### 4.1 통합 포털 UI/UX
React 기반의 단일 웹 포털을 통해 모든 데이터 분석 기능을 제공하며, 일관되고 직관적인 사용자 경험을 목표로 합니다.

- **Main Layout:** Ant Design Pro의 `ProLayout`을 활용하여 GNB(Global Navigation Bar)와 SNB(Side Navigation Bar)를 구성합니다. 아산병원 브랜드 가이드라인을 적용하여 신뢰감 있는 인터페이스를 제공합니다.
- **Home Dashboard:** 포털 접속 시 가장 먼저 보게 될 화면으로, 주요 시스템 현황, 데이터마트 요약, 최근 사용한 AI 기능 바로가기 등을 위젯 형태로 제공합니다.
- **상용 솔루션 연동 화면 (`CommercialSolutionWrapper`):**
  - `<iframe>`을 사용하여 각 상용 솔루션(TeraONE, i-MATRIX 등)을 포털 내에 완벽하게 임베딩합니다.
  - SSO(Single Sign-On)를 통해 사용자는 별도 로그인 없이 각 솔루션을 바로 사용할 수 있습니다.
  - 포털의 헤더와 사이드 메뉴는 유지되어, 사용자가 다른 시스템으로 이동했음을 인지하지 못하도록 Seamless한 경험을 제공합니다.
- **자체 개발 AI 기능 화면 (SFR-006, SFR-007):**
  - **Text2SQL:** 자연어 질의 입력창, 생성된 SQL 표시, 실행 결과 테이블, 시각화 차트 등을 포함하는 전용 인터페이스를 제공합니다.
  - **AI 분석 환경:** JupyterHub 컨테이너 생성/관리, 리소스 모니터링, 분석 템플릿 선택 등을 위한 관리자 및 사용자 대시보드를 제공합니다.

### 4.2 관리자 인터페이스
- **자원 모니터링 대시보드:** AI 기능 서버의 GPU/CPU/Memory 사용 현황을 실시간으로 모니터링합니다.
- **모델 성능 관리 패널:** Text2SQL 등 AI 모델의 정확도, 응답 시간 등 성능 지표를 추적하고 관리합니다.
- **사용자/권한 관리:** 포털 접근 및 각 메뉴(상용 솔루션 포함)에 대한 사용자별 역할 기반 접근 제어(RBAC)를 설정합니다.

## 5. 기술 스택 (확정)

### 5.1 통합 포털 (Frontend)
- **Core:** React 18 (TypeScript), Vite
- **UI Framework:** Ant Design 5, Ant Design ProComponents
- **State Management:** Zustand
- **Data Fetching:** React Query (TanStack Query)
- **API Client:** Axios
- **Visualization:** Recharts, ECharts for React

### 5.2 AI 기능 서버 (Backend)
- **Core:** Python 3.11+, FastAPI
- **AI/ML Framework:** LangGraph, LangChain, PyTorch
- **Vector DB:** Qdrant
- **Async Task:** Celery with Redis
- **ORM:** SQLAlchemy (필요시)
- **Package Manager:** **UV** (RFP 명시)

### 5.3 인프라 (Infrastructure)
- **Containerization:** Docker, Kubernetes
- **Database:** PostgreSQL (메타데이터, 로그), Redis (캐시)
- **CI/CD:** Jenkins, GitHub Actions
- **Monitoring:** Prometheus, Grafana

### 5.4 연동 대상 상용 솔루션
- **ETL:** 데이터스트림즈 `테라스트림 (Terastream)`
- **Data Mart:** 데이터스트림즈 `테라원 (Tera ONE)`
- **BI / OLAP:** 비아이매트릭스 `i-MATRIX`, `i-STREAM`

## 6. 프로젝트 일정 (수정)

### Phase 1 (Week 1-2): 통합 포털 기반 구축
- **Goal:** React 포털 뼈대 및 AI 백엔드 서버 구축
- **Tasks:**
  - React + Vite 프로젝트 생성 및 Ant Design ProLayout 적용
  - FastAPI 기본 서버 설정 및 Dockerfile 작성
  - CI/CD 파이프라인 초기 구축
  - GNB/SNB 메뉴 구조 설계 (RFP SFR 기준)

### Phase 2 (Week 3-6): 핵심 기능 개발 및 PoC
- **Goal:** 가장 중요한 AI 기능(Text2SQL) 프로토타입 개발 및 상용 솔루션 1차 연동
- **Tasks:**
  - **[AI]** Text2SQL MVP 개발 (UI, API, LangGraph 체인)
  - **[Portal]** `CommercialSolutionWrapper` 컴포넌트 개발
  - **[Integration]** BI 솔루션(`i-MATRIX`) `<iframe>` 임베딩 및 SSO 연동 PoC 수행

### Phase 3 (Week 7-8): 전체 통합 및 안정화
- **Goal:** 모든 기능 통합 및 테스트
- **Tasks:**
  - **[Integration]** 나머지 상용 솔루션(ETL, DM, OLAP) 연동 완료
  - **[AI]** JupyterHub 연동 및 AI 리소스 관리 대시보드 개발
  - **[Test]** RFP 테스트 요구사항(TER) 기반 통합 테스트 및 성능/보안 테스트 수행
  - **[Docs]** 최종 산출물 및 사용자/운영자 매뉴얼 작성

## 7. 성공 지표 (KPI)

### 7.1 기술적 지표
- **Text2SQL 정확도:** 85% 이상 (생성된 SQL이 의도에 맞게 실행되는 비율)
- **시스템 가용률:** 99.9% (포털 및 AI API 서버)
- **API 평균 응답 시간:** 500ms 미만 (AI 기능 제외)
- **단위 테스트 커버리지:** 85% 이상

### 7.2 사용성 지표
- **사용자 만족도:** 4.0 / 5.0 이상
- **기능별 월간 활성 사용자(MAU):** 100명 이상
- **SSO 연동 성공률:** 99.9%
- **셀프 서비스 데이터 추출 비율:** 사용자의 데이터 요청 중 Text2SQL을 통한 해결 비율 50% 이상

## 8. 브랜드 가이드라인 적용

- **일관성:** 포털의 헤더, 사이드바, 폰트, 기본 컴포넌트(버튼, 테이블 등)에 **ASAN GREEN (#1a5d3a)** 색상을 일관되게 적용하여, `<iframe>`으로 임베딩된 상용 솔루션 화면과도 조화를 이루도록 합니다.
- **로고:** 사이드바 상단에 서울아산병원 로고를 명확히 표시하여 포털의 아이덴티티를 강화합니다.
- **가독성:** 데이터 시각화 시 브랜드 색상 외에 정보 전달력을 높일 수 있는 보조 색상 팔레트를 정의하고 적용하여 가독성을 확보합니다.

## 9. 위험 요소 및 대응 방안

### 9.1 기술적 위험
- **Risk 1: 상용 솔루션-포털 간 SSO 연동 실패**
  - **Mitigation:** 프로젝트 2주차 내에 각 솔루션별 기술 지원팀과 협력하여 SSO 연동 PoC를 최우선으로 진행하고, 기술적 제약 발생 시 대안(예: JWT 토큰 교환 방식)을 모색합니다.
- **Risk 2: `<iframe>`의 사용자 경험 저하 (세션 끊김, UI 이질감 등)**
  - **Mitigation:** 각 솔루션이 제공하는 Embedding 전용 API나 SDK가 있는지 확인하고, 없을 경우 Keep-alive 스크립트와 CSS 스타일 오버라이딩을 통해 이질감을 최소화하는 전략을 수립합니다.
- **Risk 3: LLM의 SQL 생성 정확도(Hallucination) 문제**
  - **Mitigation:** RAG(Retrieval-Augmented Generation) 기술을 고도화하여 DB 스키마 정보를 LLM에 정확히 제공하고, 생성된 SQL을 실행 전 검증하는 단계를 파이프라인에 추가합니다.

### 9.2 프로젝트 위험
- **Risk 4: 상용 솔루션 업체의 기술 지원 지연**
  - **Mitigation:** 프로젝트 착수 시점에 각 솔루션 업체와 명확한 SLA(Service Level Agreement)를 포함한 기술 지원 협약을 체결하고, 정기적인 협력 회의를 통해 이슈를 사전에 관리합니다.
- **Risk 5: 범위 확대 (Scope Creep)**
  - **Mitigation:** 본 PRD에 명시된 기능과 연동 범위를 MVP(Minimum Viable Product)로 명확히 하고, 모든 추가 요구사항은 공식적인 변경 관리 프로세스(Change Request)를 통해서만 진행합니다.

---

## 10. 서울아산병원 IDP 구축 사업 요구사항 분석

### 10.1 사업 핵심 목표
#### 10.1.1 시스템 통합 관점
- 현재 분리 운영 중인 **EDW**(Enterprise Data Warehouse, 행정/경영 데이터)와 **CDW**(Clinical Data Warehouse, 연구/진료 데이터)의 완전한 통합
- 데이터 중복 저장 방지 및 일원화된 데이터 거버넌스 체계 구축
- 병원 내 산재된 정형/비정형 데이터의 통합 레이크하우스 아키텍처 구현
#### 10.1.2 서비스 패러다임 전환
- **지표 중심 리포팅**에서 **데이터 Product 중심 셀프-BI**로의 전환
- 사용자 주도의 탐색적 데이터 분석(EDA) 환경 제공
- 데이터 카탈로그 기반의 자율적 데이터 탐색 및 활용 체계
#### 10.1.3 AI 기반 지능화
- **자연어 기반 질의응답**(Text2SQL, Speech2SQL) 시스템 구축
- LLM 기반 연구 전주기 지원(연구 기획 → 데이터 탐색 → 분석 → 해석)
- GraphRAG와 같은 지식 그래프 기반 검색증강생성(RAG) 기술 적용

### 10.2 7개 기능요구사항(SFR) 상세 분석 및 구현 방향

#### 10.2.1 SFR-001: 공통 요구사항 (플랫폼 Foundation)
- **핵심 내용:** 목표시스템 아키텍처, CDW/EDW 통합 모델, 웹 기반 포털, 확장성 설계.
- **구현 방향:** **[자체 개발]** React 기반의 통합 포털을 구축하여 전체 시스템의 관문(Gateway) 역할을 수행. 모든 SFR 기능은 이 포털을 통해 접근.

#### 10.2.2 SFR-002: 분석DM(데이터마트) 설계 및 구축
- **핵심 내용:** CDW/EDW 통합 모델 기반, OLAP 지원, 특정 질환/분석 목적별 최적화된 데이터마트.
- **구현 방향:** **[상용 솔루션 연동]** 데이터스트림즈 `Tera ONE` 솔루션을 활용. 포털 내에서 데이터마트 설계, 관리, 모니터링 화면을 임베딩하여 제공.

#### 10.2.3 SFR-003: BI(Business Intelligence) 기능
- **핵심 내용:** 대시보드, 자유로운 레이아웃, 개체 공유, 스케줄링, 권한 관리 등.
- **구현 방향:** **[상용 솔루션 연동]** 비아이매트릭스 `i-MATRIX` 솔루션을 활용. 사용자가 포털 내에서 보고서 작성, 대시보드 조회 등 BI 기능을 직접 수행할 수 있도록 연동.

#### 10.2.4 SFR-004: 다차원 분석(OLAP) 포탈 및 시각화
- **핵심 내용:** BI 포털, 다양한 시각화 차트, 드릴다운/롤업 등 Self 분석 환경.
- **구현 방향:** **[상용 솔루션 연동]** 비아이매트릭스 `i-STREAM` 솔루션을 활용. 고성능 다차원 분석 기능을 포털을 통해 제공하여 BI 기능과 시너지를 창출.

#### 10.2.5 SFR-005: ETL 개발 (데이터 파이프라인)
- **핵심 내용:** 대용량/준실시간 데이터 처리, 이기종 소스 지원, GUI 기반 개발, 스케줄링 및 모니터링.
- **구현 방향:** **[상용 솔루션 연동]** 데이터스트림즈 `테라스트림 (Terastream)` 솔루션을 활용. 데이터 파이프라인의 설계, 실행, 모니터링 기능을 포털에 통합.

#### 10.2.6 SFR-006: AI 데이터 분석환경 제공
- **핵심 내용:** JupyterLab 기반 사용자 분석 환경, 컨테이너 기반 자원 관리, 생성형 AI 분석 기능.
- **구현 방향:** **[자체 개발 + 오픈소스 연동]**
  - JupyterHub를 별도 서버에 구축하고, SSO 연동을 통해 포털에서 사용자의 개인 분석 환경으로 안전하게 접근.
  - Kubernetes 기반으로 컨테이너 자원(GPU, CPU, Memory)을 관리하며, 관련 현황을 포털 내 관리자 대시보드에서 모니터링.
  - LangGraph 기반의 생성형 AI 분석 기능은 자체 개발하여 API 형태로 제공.

#### 10.2.7 SFR-007: CDW 데이터 추출 및 연구 지원
- **핵심 내용:** 기존 CDW 편의성 유지, 메타데이터 관리, 연구 데이터셋 추출, 그리고 핵심 AI 기능인 Text2SQL.
- **구현 방향:** **[자체 개발]**
  - 이 프로젝트의 **핵심 차별화 기능**으로, React와 FastAPI를 사용하여 UI부터 AI 백엔드까지 전체 스택을 직접 개발.
  - 자연어 질의를 SQL로 변환하고 실행 결과를 시각화하는 전용 페이지를 포털 내에 구축하여 병원의 가장 큰 Pain Point를 해결.

### 10.3 POC 구현 전략 및 로드맵 ( **수정됨** )

#### 10.3.1 Phase 1: 통합 포털 기반 구축 (Week 1-2)
**목표:** 7개 SFR을 통합 전시할 수 있는 React 기반 웹 포털의 기본 구조와 AI 백엔드 서버 구축

**통합 포털 아키텍처:**
```
asan-idp/
├── frontend/             # React 기반 통합 포털
│   ├── src/
│   │   ├── layouts/      # 공통 레이아웃 (GNB, SNB)
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── CommercialSolutionWrapper.tsx # 상용 솔루션 임베딩
│   │   │   ├── sfr006_ai/      # AI 분석 환경 (SFR-006 관련)
│   │   │   └── sfr007_cdw/ # Text2SQL 등 자체개발 UI (SFR-007 관련)
│   │   ├── components/         # 공통 컴포넌트
│   │   │   ├── ai/             # AI 관련 컴포넌트
│   │   │   └── custom/         # 기타 재활용 가능 컴포넌트
│   │   ├── services/       # AI API 연동
│   │   └── types/          # TypeScript 타입 정의
│   └── package.json
│
├── backend/              # FastAPI 기반 AI 기능 서버
│   ├── app/
│   │   ├── api/v1/       # Text2SQL, RAG 등 API
│   │   └── services/     # LangGraph 에이전트 로직, Vector Store (Qdrant)
│   └── requirements.txt
```

**기술 선택:**
- **Backend:** **FastAPI** (고성능 AI-Serving REST API)
- **Frontend:** **React (TypeScript)** (엔터프라이즈급 단일 페이지 애플리케이션)
- **Database (For AI):** PostgreSQL, Redis, Qdrant
- **Data Processing:** Pandas, Polars
- **Python Env:** **UV** (RFP 요구사항)

#### 10.3.2 Phase 2: 상용 솔루션 연동 및 핵심 AI 기능 프로토타이핑 (Week 3-6)

**Step 1: 상용 솔루션 연동 (SFR-002, 003, 004, 005)**
- **목표:** 데이터마트, ETL, BI, OLAP 상용 솔루션 화면을 포털 내에 `<iframe>`과 SSO를 통해 통합.
- **연동 대상:**
  - **SFR-002 (데이터마트):** 데이터스트림즈 Tera ONE
  - **SFR-005 (ETL):** 데이터스트림즈 테라스트림
  - **SFR-003 (BI):** 비아이매트릭스 i-MATRIX
  - **SFR-004 (OLAP):** 비아이매트릭스 i-STREAM
- **구현:** `CommercialSolutionWrapper.tsx` 컴포넌트를 통해 각 솔루션 URL을 임베딩하고, JWT 기반 SSO 연동을 통해 사용자 경험을 일관성 있게 유지.

**Step 2: 핵심 AI 기능 프로토타입 개발 (SFR-007 Text2SQL)** 🔥
- **목표:** 이 프로젝트의 **킬러 애플리케이션**인 Text2SQL 기능의 MVP(Minimum Viable Product) 개발.
- **아키텍처:**
  - **Frontend:** React 기반 질의 입력 및 결과 표시 UI 개발 (`sfr007_cdw/` 페이지)
  - **Backend:** FastAPI 엔드포인트 `/api/v1/text2sql/generate` 구현.
  - **AI Logic:** LangChain/LangGraph을 사용하여 '자연어 질의 → RAG(DB 스키마 조회) → LLM(SQL 생성) → SQL 검증 → 결과 반환' 파이프라인 구축.

#### 10.3.3 Phase 3: AI 분석 환경 연동 및 통합 테스트 (Week 7-8)
**목표:** 컨테이너 기반 AI 분석 환경을 포털에 통합하고, 전체 시스템의 안정성을 검증.

**Step 1: SFR-006 (AI 데이터 분석환경)**
- JupyterHub 컨테이너 환경을 별도 서버에 구축.
- React 포털에서 'AI 분석환경' 메뉴 클릭 시, SSO 연동을 통해 사용자의 JupyterLab 환경으로 리디렉션.
- KubeFlow/MLflow와 연계하여 모델 및 리소스 관리 기능 API를 개발하고, 포털 내 관리자 페이지에 연동.

**Step 2: 통합 및 최적화**
- 전체 모듈(상용 솔루션 + 자체 개발 AI) 간 데이터 흐름 및 사용자 인증 흐름 검증.
- Text2SQL 성능 최적화 (쿼리 정확도 85% 이상 목표).
- RFP의 보안(SER) 및 품질(QUR) 요구사항에 대한 최종 점검 및 테스트.

### 10.4 실제 데이터 연동 계획

#### 10.4.1 AI-Hub 헬스케어 데이터셋 활용
현재 `C:\projects\datastreams\asan\data`에 다운로드된 3개 데이터셋:

1.  **필수의료 의학지식 데이터 (136MB)**
    -   일반적인 질병/증상 정보
    -   진단 코드 매핑

2.  **전문 의학지식 데이터 (197MB)**
    -   전문적인 임상 정보
    -   치료 프로토콜

3.  **심리상담 데이터 (73MB)**
    -   환자 상담 기록
    -   정신건강 관련 데이터

### 10.5 핵심 기술 스택 종합

#### 10.5.1 Backend (AI Feature Development)
-   **Language:** Python 3.11+
-   **Framework:** FastAPI (REST API)
-   **Task Queue:** Celery + Redis
-   **Workflow:** Apache Airflow (for complex AI pipelines, otherwise commercial ETL is used)
-   **ORM:** SQLAlchemy (for custom DB interactions)

#### 10.5.2 Database & Storage (for AI Features & Platform Metadata)
-   **RDBMS:** PostgreSQL 15+ (AI feature metadata, audit logs)
-   **Cache:** Redis (API caching, Celery broker)
-   **Vector DB:** Qdrant (RAG, knowledge base)

#### 10.5.3 Data Processing (for AI Data Prep)
-   **ETL:** Apache Spark, Pandas (for AI-specific data transformations; main ETL via commercial solution)
-   **Real-time:** Apache Kafka (if AI features require stream processing)
-   **Data Quality:** Great Expectations (for AI training data validation)

#### 10.5.4 AI/ML
-   **LLM Orchestration:** LangChain, LangGraph
-   **ML Framework:** PyTorch, TensorFlow
-   **Model Serving:** MLflow
-   **Vector Embeddings:** OpenAI Embeddings, HuggingFace

#### 10.5.5 Container & Orchestration
-   **Container:** Docker
-   **Orchestration:** Kubernetes
-   **ML Platform:** KubeFlow (for MLOps)
-   **Notebook:** JupyterHub (for AI development environment)
-   **Python Env Management:** **UV** (RFP 명시, 빠른 의존성 해결 및 재현 가능한 빌드)

#### 10.5.6 Monitoring & Logging
-   **Metrics:** Prometheus + Grafana
-   **Logging:** ELK Stack (Elasticsearch, Logstash, Kibana)
-   **Tracing:** Jaeger

### 10.6 성공 지표 (KPI)

#### 10.6.1 기술적 지표
-   **Text2SQL 정확도:** 85% 이상 (생성된 SQL이 의도에 맞게 실행되는 비율)
-   **시스템 가용률:** 99.9% (포털 및 AI API 서버)
-   **API 평균 응답 시간:** 500ms 미만 (AI 기능 제외)
-   **단위 테스트 커버리지:** 85% 이상

#### 10.6.2 사용성 지표
-   **사용자 만족도:** 4.0 / 5.0 이상
-   **기능별 월간 활성 사용자(MAU):** 100명 이상
-   **SSO 연동 성공률:** 99.9%
-   **셀프 서비스 데이터 추출 비율:** 사용자의 데이터 요청 중 Text2SQL을 통한 해결 비율 50% 이상

### 10.7 위험 요소 및 대응 방안

#### 10.7.1 기술적 위험
-   **Risk 1: 상용 솔루션-포털 간 SSO 연동 실패**
    -   **Mitigation:** 프로젝트 2주차 내에 각 솔루션별 기술 지원팀과 협력하여 SSO 연동 PoC를 최우선으로 진행하고, 기술적 제약 발생 시 대안(예: JWT 토큰 교환 방식)을 모색합니다.
-   **Risk 2: `<iframe>`의 사용자 경험 저하 (세션 끊김, UI 이질감 등)**
    -   **Mitigation:** 각 솔루션이 제공하는 Embedding 전용 API나 SDK가 있는지 확인하고, 없을 경우 Keep-alive 스크립트와 CSS 스타일 오버라이딩을 통해 이질감을 최소화하는 전략을 수립합니다.
-   **Risk 3: LLM의 SQL 생성 정확도(Hallucination) 문제**
    -   **Mitigation:** RAG(Retrieval-Augmented Generation) 기술을 고도화하여 DB 스키마 정보를 LLM에 정확히 제공하고, 생성된 SQL을 실행 전 검증하는 단계를 파이프라인에 추가합니다.

#### 10.7.2 프로젝트 위험
-   **Risk 4: 상용 솔루션 업체의 기술 지원 지연**
    -   **Mitigation:** 프로젝트 착수 시점에 각 솔루션 업체와 명확한 SLA(Service Level Agreement)를 포함한 기술 지원 협약을 체결하고, 정기적인 협력 회의를 통해 이슈를 사전에 관리합니다.
-   **Risk 5: 범위 확대 (Scope Creep)**
    -   **Mitigation:** 본 PRD에 명시된 기능과 연동 범위를 MVP(Minimum Viable Product)로 명확히 하고, 모든 추가 요구사항은 공식적인 변경 관리 프로세스(Change Request)를 통해서만 진행합니다.

---