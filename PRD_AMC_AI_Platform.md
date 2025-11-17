# 서울아산병원 AI 데이터 분석 플랫폼 PRD (Product Requirements Document)

## 1. 프로젝트 개요

### 1.1 프로젝트 명
서울아산병원 AI 기반 통합 데이터 분석 플랫폼 구축

### 1.2 프로젝트 목표
컨테이너 기반의 AI 데이터 분석 환경을 제공하여 의료진과 연구진이 효율적인 데이터 분석 및 의사결정을 지원하는 통합 플랫폼 구축

### 1.3 핵심 가치 제안
- 생성형 AI 기반의 지능형 의료 데이터 분석
- GraphRAG와 온톨로지 기반의 고도화된 검색 증강 생성
- 멀티모달 AI를 활용한 의료 영상 및 텍스트 통합 분석
- 의료진 친화적 자연어 기반 질의응답 시스템

## 2. 기능 요구사항

### 2.1 AI 데이터 분석환경 제공 (SFR-006)

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
- SOTA 오픈소스 LLM 도입 (Cohere Command R+, Qwen2-72B 등)
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

## 3. 비기능 요구사항

### 3.1 성능 요구사항
- 생성형 AI 시스템 정확도 90% 이상
- 실시간 자원 모니터링 및 알림
- 멀티모달 검색 응답 시간 5초 이내

### 3.2 보안 요구사항 (시큐어 코딩)
- 데이터 활용 권한별 응답 필터링
- 개인정보 보호 정책 반영
- 의료정보 보호법 준수
- 사용자별 접근 권한 관리
- **OWASP 보안 가이드라인 준수**
- **입력 데이터 검증 및 SQL 인젝션 방지**
- **XSS(Cross-Site Scripting) 방지 구현**
- **CSRF(Cross-Site Request Forgery) 보호**
- **암호화 알고리즘 표준 준수 (AES-256)**
- **의료 데이터 접근 로깅 및 감사 추적**
- **세션 관리 및 토큰 기반 인증 보안**

### 3.3 확장성 요구사항
- 클라우드 기반 탄력적 자원 확장
- 새로운 AI 모델 추가 용이성
- 다양한 의료 시스템 연계 가능성

### 3.4 개발 품질 요구사항 (TDD & 유지보수성)

#### 3.4.1 테스트 주도 개발 (TDD)
- **단위 테스트 커버리지 85% 이상 유지**
- **통합 테스트 자동화 파이프라인 구축**
- **엔드투엔드 테스트 시나리오 구현**
- **의료 AI 모델 정확도 검증 테스트**
- **성능 테스트 및 부하 테스트 자동화**
- **BDD(Behavior-Driven Development) 적용**
- **테스트 데이터 관리 및 Mock 데이터 활용**

#### 3.4.2 유지보수 용이성
- **클린 아키텍처 적용 (Hexagonal Architecture)**
- **SOLID 원칙 준수**
- **의존성 주입(Dependency Injection) 패턴 적용**
- **코드 리뷰 프로세스 의무화**
- **자동화된 코드 품질 검사 (SonarQube, ESLint 등)**
- **API 문서화 자동화 (OpenAPI/Swagger)**
- **버전 관리 전략 및 브랜치 정책 수립**
- **로깅 및 모니터링 표준화**
- **설정 관리 및 환경 분리 (Dev/Staging/Production)**
- **컨테이너화 및 Infrastructure as Code (IaC)**
- **UV 기반 Python 패키지 관리 (빠른 의존성 해결 및 재현 가능한 빌드)**
- **Python 가상환경 표준화 (uv venv 활용)**

## 4. 사용자 인터페이스

### 4.1 웹 기반 분석 환경
- JupyterLab 통합 인터페이스
- 자연어 질의 입력창
- 시각화 결과 대시보드
- 프로젝트 관리 패널

### 4.2 관리자 인터페이스
- 자원 사용량 모니터링 대시보드
- 모델 성능 관리 패널
- 사용자/권한 관리 시스템

## 5. 기술 스택

### 5.1 AI/ML Framework
- LangGraph, LangChain
- TensorFlow, PyTorch
- Hugging Face Transformers
- OpenAI API 호환 인터페이스

### 5.2 Infrastructure
- Docker/Kubernetes
- NVIDIA GPU 지원
- Apache Kafka (데이터 스트리밍)
- Redis (캐싱)
- **UV 가상환경 관리 (Python 패키지 관리 최적화)**

### 5.3 Database
- 벡터 데이터베이스 (Chroma, Pinecone)
- Graph Database (Neo4j)
- Time Series DB (InfluxDB)

## 6. 프로젝트 일정

### Phase 1 (개발 환경 구축): 2개월
- 인프라 셋업
- 기본 분석 환경 구축
- 기본 LLM 통합

### Phase 2 (핵심 AI 기능): 3개월
- GraphRAG 구현
- 문서 처리 시스템
- 멀티모달 기능

### Phase 3 (운영 최적화): 1개월
- 성능 튜닝
- 모니터링 시스템
- 사용자 교육

## 7. 성공 지표

### 7.1 기술적 지표
- AI 모델 정확도 90% 이상
- 시스템 가용률 99.5% 이상
- 평균 응답 시간 5초 이내

### 7.2 사용성 지표
- 월간 활성 사용자 100명 이상
- 사용자 만족도 4.0/5.0 이상
- 분석 프로젝트 완료율 80% 이상

## 8. 브랜드 가이드라인

### 8.1 아산사회복지재단 브랜드 아이덴티티

#### 8.1.1 브랜드 색상 (Brand Colors)
**주요 색상 (Primary Colors)**
- **ASAN GREEN**: C100, M15, Y45, K40 (HEX: #1a5d3a)
  - 신뢰감과 안정감을 나타내는 아산병원의 대표 색상
  - 의료진의 전문성과 환자에 대한 배려를 상징
  - UI 주요 버튼, 헤더, 포인트 컬러로 사용

**보조 색상 (Secondary Colors)**
- **ASAN Orange**: C0, M65, Y100, K0 (HEX: #ff6600)
  - 활력과 따뜻함을 표현하는 보조 색상
  - 알림, 경고, 액센트 요소에 활용

**뉴트럴 색상 (Neutral Colors)**
- White: #ffffff (배경, 카드 배경)
- Light Gray: #f5f5f5 (섹션 구분, 비활성 요소)
- Medium Gray: #999999 (부가 정보, 설명 텍스트)
- Dark Gray: #333333 (본문 텍스트)

#### 8.1.2 기관명 표기 기준
**공식 명칭**
- 한국어: "서울아산병원" (Seoul Asan Medical Center)
- 영문: "Asan Medical Center" 또는 "Seoul Asan Medical Center"

**로고 및 브랜딩 원칙**
- 의료 십자 심볼과 ASAN GREEN 그라데이션 조합
- 브랜드 색상 일관성 유지
- 가독성과 접근성을 고려한 색상 대비율 확보

#### 8.1.3 UI/UX 적용 가이드라인
**색상 적용 우선순위**
1. Primary Action: ASAN GREEN (#1a5d3a)
2. Background Gradient: ASAN GREEN variations
3. Card Borders: Light green tints (#e6f4ea)
4. Shadows: ASAN GREEN with opacity
5. Hover States: Darker ASAN GREEN (#165030)

**타이포그래피**
- 제목: 한국어 - 나눔고딕, 영문 - Roboto
- 본문: 시스템 폰트 스택 활용
- 브랜드 컬러(#1a5d3a)를 제목 및 중요 요소에 적용

## 9. 위험 요소 및 대응 방안

### 9.1 기술적 위험
- GPU 자원 부족: 클라우드 기반 확장 대안 마련
- 모델 성능 저하: A/B 테스트 및 지속적 튜닝

### 9.2 규제적 위험
- 의료정보 보호법 준수: 법무팀과 협업하여 컴플라이언스 확보
- 개인정보 처리 방침: 데이터 마스킹 및 익명화 처리

### 9.3 운영적 위험  
- 사용자 교육 부족: 단계적 교육 프로그램 운영
- 시스템 장애: 24/7 모니터링 및 백업 체계 구축

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

### 10.2 7개 기능요구사항(SFR) 상세

#### 10.2.1 SFR-001: 공통 요구사항 (플랫폼 Foundation)
**핵심 내용:**
- 목표시스템 아키텍처 설계 및 구성 방안
- CDW/EDW 통합 모델 및 주제영역 구성
- 비정형 데이터를 고려한 ODS/DW/DM 설계
- 웹 기반 BI 보고서 포털 시스템
- 향후 확장성을 고려한 설계

**구현 우선순위:** ⭐⭐⭐⭐⭐ (최우선)
**이유:** 전체 시스템의 아키텍처 청사진이자 다른 모든 SFR의 기반

#### 10.2.2 SFR-002: 분석DM(데이터마트) 설계 및 구축
**핵심 내용:**
- CDW/EDW 통합 모델 기반 일원화된 분석 서비스
- 운영계 시스템과의 데이터 정합성 확보
- OLAP 지원을 위한 효율적인 정보전달 체계
- 특정 질환/분석 목적별 최적화된 데이터마트 모델링 (Cohort, K-CURE 등)
- 재활용 가능하고 결합 가능한 마트 구조 설계

**구현 우선순위:** ⭐⭐⭐⭐⭐ (최우선)
**이유:** 데이터 활용의 핵심 기반 구조이며, BI/OLAP/AI 모든 기능의 데이터 소스

**특이사항:** 
- EMR 기록지와 같은 구조화된 서식지의 데이터마트 모델링 필요
- 반정형/비정형 데이터의 정형화/구조화 처리 환경 필수

#### 10.2.3 SFR-003: BI(Business Intelligence) 기능
**핵심 내용:**
- BI 솔루션 적용 (상용 솔루션 또는 자체 개발)
- 대시보드 기능: 라디오버튼, 체크박스, 풀다운 등 선택 컨트롤
- 자유로운 레이아웃 구성 및 탭 형태 다중 화면
- 개체 공유: 리포트, 연산식, 필터, 지표 등의 재사용
- 조직개편/인사발령 자동 반영

**구현 우선순위:** ⭐⭐⭐⭐ (높음)
**이유:** 사용자 직접 접점이며 셀프-BI 구현의 핵심

#### 10.2.4 SFR-004: 다차원 분석(OLAP) 포탈 및 시각화 ✅ **완료**
**구현 상태:**
- OLAP 엔진: 큐브, 슬라이스/다이스, 드릴다운/롤업 구현
- Streamlit 기반 UI: 4개 탭 구조
- Plotly 인터랙티브 차트 및 히트맵
- 시계열/기여도/비교 분석 기능

**통합 방향:**
- 이 모듈을 전체 통합 대시보드의 하나의 탭으로 편입
- SFR-003 BI 기능과 UI/UX 일관성 유지
- 데이터 소스를 실제 AI-Hub 헬스케어 데이터로 전환

#### 10.2.5 SFR-005: ETL 개발 (데이터 파이프라인)
**핵심 내용:**
- ETL 솔루션 적용 (상용 또는 자체 개발)
- 기존 ETL 프로세스 병목 현상 식별 및 최적화
- 대용량 데이터 처리: 세션 레벨 + 테이블 레벨 병렬 적재
- 준실시간 데이터 처리 (30분 간격)
- 이기종 소스 지원: DBMS, File, Log 등
- 오류 발생 시 Alert 및 선택적 재실행
- GUI 환경의 신속한 개발 도구
- 스케줄링 및 모니터링 체계

**구현 우선순위:** ⭐⭐⭐⭐⭐ (최우선)
**이유:** 데이터 수집의 시작점이자 전체 플랫폼의 혈관

**기술 스택 제안:**
- Apache Airflow (워크플로우 오케스트레이션)
- Apache Spark (대용량 병렬 처리)
- Debezium (CDC, Change Data Capture)
- Great Expectations (데이터 품질 검증)

#### 10.2.6 SFR-006: AI 데이터 분석환경 제공
**핵심 내용:**

**[사용자 분석 환경]**
- 웹 기반 JupyterLab 분석 도구
- 딥러닝/기계학습을 위한 GPU 연산 아키텍처
- Python, Scala 등 다양한 언어/버전 지원
- 머신러닝/딥러닝/시각화 라이브러리 사전 탑재
- 프로젝트별 자원(CPU/Memory/GPU) 관리 및 모니터링
- 템플릿 기반 분석: 탐색적 분석, 자연어 분석, 공간 분석
- 분석 작업 공유 및 협업 기능

**[컨테이너 기반 관리]**
- Docker/Kubernetes 기반 컨테이너 환경
- 운영자 승인 시 자동 컨테이너 생성
- 사용자별 CPU/Memory/DISK/GPU 자원 할당
- GPU 가상화를 통한 다중 사용자 지원
- 컨테이너 생성/소멸/시작/중단 제어
- 스케줄링 및 로드 밸런싱

**[생성형 AI 분석 기능]**
- 최신 SOTA 오픈소스 LLM (Qwen3-Next, MiniMax M1 등) 도입
- GraphRAG 기반 검색증강생성 기술
- LangGraph 프레임워크 활용 에이전트 시스템
- 지능형 데이터 패브릭 아키텍처

**구현 우선순위:** ⭐⭐⭐⭐ (높음)
**이유:** AI 기반 연구 환경의 핵심이며 차별화 요소

**기술 스택 제안:**
- JupyterHub (멀티 사용자 환경)
- Kubernetes + KubeFlow (ML 오케스트레이션)
- NVIDIA GPU Operator (GPU 가상화)
- MLflow (모델 관리 및 추적)

#### 10.2.7 SFR-007: CDW 데이터 추출 및 연구 지원
**핵심 내용:**

**[CDW 화면 UI/UX]**
- 기존 사용자 편의성 유지
- 조회 쿼리, 필터, 차트 데이터 활용 가능 구조

**[데이터 모델 호환성]**
- 주요 Fact/Dimension 구조 유지
- 코드 체계 유지: KCD, 처방코드, 검사코드
- 지표/용어 정의 변경 최소화

**[메타데이터 및 품질 관리]**
- 메타데이터 관리 및 표준 용어 매핑
- 데이터 품질관리 자동화: 누락/이상치/중복 탐지
- 품질 이슈 자동 리포트 생성

**[연구 데이터셋 추출]**
- 기존 권한/승인 프로세스 유지
- 연구자 인증 기반 데이터 추출 요청/승인/이력 관리

**[🔥 핵심 AI 기능: Text2SQL/Speech2SQL]**
- **자연어 질의 → SQL 자동 생성 → 결과 데이터 추출**
- CDW 담당자와 협의하여 질의 인터페이스 설계
- LLM 기반 대화형 데이터 조회 시스템

**구현 우선순위:** ⭐⭐⭐⭐⭐ (최우선)
**이유:** 병원의 가장 큰 pain point이자 AI 적용의 킬러 애플리케이션

**기술 스택 제안:**
- LangChain/LangGraph (LLM 오케스트레이션)
- Few-shot Learning + RAG (스키마 이해 및 SQL 생성)
- Vector DB (Qdrant, Chroma) for 스키마 임베딩
- SQL Validation 및 Query Optimization 모듈

### 10.3 POC 구현 전략 및 로드맵

#### 10.3.1 Phase 1: 기반 인프라 구축 (Week 1-2)
**목표:** 7개 SFR을 통합할 수 있는 기본 프레임워크 구축

**통합 웹 애플리케이션 프레임워크 구조:**
```
C:\projects\datastreams\asan\
├── app.py                    # 메인 애플리케이션 엔트리포인트
├── config/
│   ├── settings.py          # 전역 설정
│   └── database.py          # DB 연결 설정
├── modules/
│   ├── sfr001_common/       # 공통 요구사항
│   ├── sfr002_datamart/     # 분석DM
│   ├── sfr003_bi/           # BI 기능
│   ├── sfr004_olap/         # OLAP (기존 모듈 통합)
│   ├── sfr005_etl/          # ETL 개발
│   ├── sfr006_ai_env/       # AI 분석환경
│   └── sfr007_cdw/          # CDW 연구 지원
├── data/                     # AI-Hub 데이터
│   ├── raw/
│   ├── processed/
│   └── catalog/
├── utils/
│   ├── auth.py              # 인증/권한
│   ├── logging.py           # 로깅
│   └── helpers.py
└── requirements.txt
```

**기술 선택:**
- **Backend:** FastAPI (고성능 REST API)
- **Frontend:** Streamlit + React (하이브리드)
  - Streamlit: 신속한 프로토타이핑
  - React: 복잡한 대시보드 UI
- **Database:** 
  - PostgreSQL (구조화 데이터)
  - MongoDB (비정형 데이터)
  - Redis (캐싱)
- **Data Processing:** 
  - Pandas, Polars (데이터 처리)
  - DuckDB (in-process OLAP)

#### 10.3.2 Phase 2: 핵심 모듈 구현 (Week 3-6)

**Step 1: SFR-002 (분석DM 설계) + SFR-005 (ETL)**
- ETL 파이프라인으로 AI-Hub 데이터를 데이터마트로 적재
- Star Schema 기반 차원/사실 테이블 설계
- 예시 데이터마트:
  - **환자 차원 (DIM_PATIENT):** 연령대, 성별, 지역 등
  - **진단 차원 (DIM_DIAGNOSIS):** KCD 코드, 질병 분류
  - **시간 차원 (DIM_TIME):** 년/분기/월/일
  - **진료 사실 (FACT_VISIT):** 환자 ID, 진단 ID, 시간 ID, 측정값

**Step 2: SFR-003 (BI 기능) + SFR-004 (OLAP 통합)**
- 기존 OLAP 모듈을 BI 대시보드에 통합
- 공통 UI 컴포넌트 라이브러리 구축
- 대시보드 개체 공유 메커니즘

**Step 3: SFR-007 (CDW 연구 지원) - Text2SQL 구현** 🔥
- 이것이 이 프로젝트의 **킬러 애플리케이션**
- 아키텍처:
  - 사용자 자연어 질의 → LLM + RAG (스키마 이해) → SQL 생성 및 검증 → 쿼리 실행 및 결과 반환 → 자연어 설명 생성

**Step 4: SFR-006 (AI 데이터 분석환경)**
- JupyterHub 컨테이너 환경 구축
- GPU 리소스 할당 시스템
- 사전 구성된 노트북 템플릿

#### 10.3.3 Phase 3: 통합 및 최적화 (Week 7-8)
- 모듈 간 통합 및 데이터 흐름 검증
- API 인터페이스 표준화
- 성능 최적화 (쿼리 최적화, 캐싱, 부하 테스트)
- 보안 및 거버넌스 (데이터 비식별화, 접근 권한, 감사 로그)

### 10.4 실제 데이터 연동 계획

#### 10.4.1 AI-Hub 헬스케어 데이터셋 활용
현재 `C:\projects\datastreams\asan\data`에 다운로드된 3개 데이터셋:

1. **필수의료 의학지식 데이터 (136MB)**
   - 일반적인 질병/증상 정보
   - 진단 코드 매핑

2. **전문 의학지식 데이터 (197MB)**
   - 전문적인 임상 정보
   - 치료 프로토콜

3. **심리상담 데이터 (73MB)**
   - 환자 상담 기록
   - 정신건강 관련 데이터

### 10.5 핵심 기술 스택 종합

#### 10.5.1 Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI (REST API), Streamlit (UI)
- **Task Queue:** Celery + Redis
- **Workflow:** Apache Airflow

#### 10.5.2 Database & Storage
- **RDBMS:** PostgreSQL 15+ (데이터마트)
- **OLAP:** ClickHouse (실시간 분석)
- **Document Store:** MongoDB (비정형 데이터)
- **Cache:** Redis
- **Vector DB:** Chroma, Qdrant (RAG)

#### 10.5.3 Data Processing
- **ETL:** Apache Spark, Pandas
- **Real-time:** Apache Kafka
- **Data Quality:** Great Expectations

#### 10.5.4 AI/ML
- **LLM Orchestration:** LangChain, LangGraph
- **ML Framework:** PyTorch, TensorFlow
- **Model Serving:** MLflow
- **Vector Embeddings:** OpenAI Embeddings, HuggingFace

#### 10.5.5 Container & Orchestration
- **Container:** Docker
- **Orchestration:** Kubernetes
- **ML Platform:** KubeFlow
- **Notebook:** JupyterHub

#### 10.5.6 Monitoring & Logging
- **Metrics:** Prometheus + Grafana
- **Logging:** ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing:** Jaeger

### 10.6 성공 지표 (KPI)

#### 10.6.1 기술적 지표
- **데이터 처리 성능**
  - ETL 처리량: 1M records/hour
  - OLAP 쿼리 응답시간: <3초
  - Text2SQL 정확도: >85%
- **시스템 안정성**
  - 가용성: 99.9%
  - 데이터 품질: >95% (Great Expectations)
  - API 응답시간: <500ms
- **AI 모델 성능**
  - SQL 생성 정확도: >85%
  - 자연어 이해도: >90%
  - 쿼리 최적화율: >30% 성능 향상

#### 10.6.2 비즈니스 지표
- **사용성**
  - 사용자 교육 시간: <2시간
  - 셀프 서비스 비율: >70%
  - 사용자 만족도: >4.0/5.0
- **효율성**
  - 데이터 조회 시간 단축: >50%
  - 리포트 생성 자동화: >80%
  - 연구 데이터 추출 시간: <10분

### 10.7 위험 요소 및 대응 방안

#### 10.7.1 기술적 위험
**Risk 1: LLM의 SQL 생성 정확도 부족**
- **대응:** Few-shot Learning + RAG + 검증 레이어 다중화
- **백업:** 하이브리드 접근 (반자동 SQL 생성 + 사용자 수정)

**Risk 2: 대용량 데이터 처리 성능 이슈**
- **대응:** Spark 병렬 처리 + 파티셔닝 + 인덱스 최적화
- **백업:** 데이터마트 크기 제한 + 증분 처리

**Risk 3: GPU 리소스 부족 (RTX 3090 2대)**
- **대응:** 컨테이너 기반 GPU 가상화 + 스케줄링
- **백업:** 클라우드 GPU (AWS/Azure) 하이브리드

#### 10.7.2 프로젝트 위험
**Risk 4: 의료 데이터 보안 규제 미준수**
- **대응:** 개인정보보호법/HIPAA 준수 체크리스트
- **조치:** 비식별화 검증 + 접근 로그 + 감사 시스템

**Risk 5: 범위 확대 (Scope Creep)**
- **대응:** POC 범위 명확히 정의 + 변경 관리 프로세스
- **원칙:** MVP 우선 → 점진적 확장