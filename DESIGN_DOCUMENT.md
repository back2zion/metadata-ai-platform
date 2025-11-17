# 서울아산병원 AI 플랫폼 TDD 설계 문서

## 📋 프로젝트 개요

### 목표
- 기존 AMC 플랫폼을 TDD 방법론으로 확장
- HumanLayer 에이전트 기반 승인 워크플로우 통합
- AI Hub 헬스케어 데이터와 연동하여 실제 의료 데이터 분석 지원

### 핵심 원칙
- **TDD First**: 테스트 작성 → 구현 → 리팩토링 사이클
- **Clean Architecture**: 헥사고날 아키텍처 적용
- **Human-in-the-Loop**: 모든 중요한 AI 작업에 승인 프로세스 적용

## 🏗️ 시스템 아키텍처

### 전체 구조
```
AMC AI Platform
├── Frontend (React + Ant Design)
├── Backend (FastAPI + Clean Architecture)
│   ├── Domain Layer
│   ├── Application Layer (Use Cases)
│   ├── Infrastructure Layer
│   └── Interface Layer (REST API)
├── AI Services
│   ├── Text2SQL Engine
│   ├── GraphRAG System
│   └── Vector Store
├── HumanLayer Integration
│   ├── Approval Workflows
│   ├── Agent Task Management
│   └── Real-time Feedback
└── Data Sources
    ├── AI Hub Healthcare Data
    ├── Mock Medical Database
    └── Vector Embeddings
```

### Clean Architecture 레이어

#### 1. Domain Layer (도메인 계층)
```python
# 핵심 비즈니스 로직, 외부 의존성 없음
entities/
├── patient.py              # 환자 엔티티
├── diagnosis.py            # 진단 엔티티
├── sql_query.py            # SQL 쿼리 엔티티
├── approval_request.py     # 승인 요청 엔티티
└── ai_task.py              # AI 작업 엔티티

value_objects/
├── patient_demographics.py
├── medical_code.py
├── query_confidence.py
└── approval_status.py

domain_services/
├── text2sql_domain_service.py
├── medical_validation_service.py
└── security_validation_service.py
```

#### 2. Application Layer (애플리케이션 계층)
```python
# 유스케이스와 애플리케이션 서비스
use_cases/
├── convert_text_to_sql.py
├── execute_approved_query.py
├── request_human_approval.py
├── analyze_medical_data.py
└── manage_ai_tasks.py

interfaces/
├── repositories/
│   ├── patient_repository.py
│   ├── query_repository.py
│   └── approval_repository.py
├── external_services/
│   ├── llm_service.py
│   ├── humanlayer_service.py
│   └── vector_store_service.py
└── notification_service.py
```

#### 3. Infrastructure Layer (인프라 계층)
```python
# 외부 시스템 연동 구현체
repositories/
├── sqlalchemy_patient_repository.py
├── mongodb_query_repository.py
└── redis_cache_repository.py

external_services/
├── openai_llm_service.py
├── langchain_text2sql_service.py
├── chroma_vector_service.py
└── humanlayer_api_client.py

database/
├── models/
├── migrations/
└── seeders/
```

#### 4. Interface Layer (인터페이스 계층)
```python
# REST API와 사용자 인터페이스
api/
├── v1/
│   ├── text2sql_controller.py
│   ├── approval_controller.py
│   ├── medical_data_controller.py
│   └── ai_agents_controller.py
├── middleware/
│   ├── authentication.py
│   ├── authorization.py
│   └── request_logging.py
└── dto/
    ├── text2sql_request.py
    ├── approval_response.py
    └── medical_query_dto.py
```

## 🧪 TDD 테스트 전략

### 테스트 피라미드
```
              /\
             /  \
            / E2E \ (소수, 브라우저 자동화)
           /______\
          /        \
         /Integration\ (API 통합 테스트)
        /__________\
       /            \
      /   Unit Tests  \ (85% 커버리지 목표)
     /________________\
```

### 테스트 구조
```
tests/
├── unit/                   # 단위 테스트 (가장 많음)
│   ├── domain/
│   │   ├── test_patient_entity.py
│   │   ├── test_sql_query_entity.py
│   │   └── test_text2sql_domain_service.py
│   ├── application/
│   │   ├── test_convert_text_to_sql_use_case.py
│   │   ├── test_approval_workflow_use_case.py
│   │   └── test_medical_data_analysis_use_case.py
│   └── infrastructure/
│       ├── test_openai_llm_service.py
│       └── test_humanlayer_client.py
├── integration/            # 통합 테스트
│   ├── test_text2sql_api.py
│   ├── test_approval_workflow.py
│   └── test_database_integration.py
├── e2e/                   # E2E 테스트
│   ├── test_user_journey.py
│   └── test_approval_flow.py
├── fixtures/              # 테스트 데이터
│   ├── medical_data.json
│   ├── sample_queries.json
│   └── mock_responses.json
└── conftest.py           # 테스트 설정
```

### 테스트 도구 스택
```python
pytest==7.4.4              # 테스트 프레임워크
pytest-asyncio==0.23.3     # 비동기 테스트 지원
pytest-cov==4.1.0          # 커버리지 측정
pytest-mock==3.11.1        # Mocking 지원
factory-boy==3.3.0         # 테스트 데이터 생성
httpx==0.26.0              # HTTP 클라이언트 테스트
pytest-postgresql==5.0.0   # 테스트용 DB
```

## 🤖 AI 서비스 아키텍처

### Text2SQL 엔진 설계
```python
class Text2SQLEngine:
    """Clean Architecture 기반 Text2SQL 엔진"""
    
    def __init__(self, 
                 llm_service: LLMServiceInterface,
                 vector_store: VectorStoreInterface,
                 validator: SQLValidatorInterface,
                 approval_service: ApprovalServiceInterface):
        self._llm_service = llm_service
        self._vector_store = vector_store
        self._validator = validator
        self._approval_service = approval_service
    
    async def convert_with_approval(self, 
                                  question: str, 
                                  user_context: UserContext) -> SQLQueryResult:
        """승인 기반 Text2SQL 변환"""
        # 1. 자연어 → SQL 변환
        sql_query = await self._generate_sql(question)
        
        # 2. 보안 검증
        validation_result = await self._validator.validate(sql_query)
        if not validation_result.is_safe:
            raise SecurityValidationError(validation_result.errors)
        
        # 3. 승인 요청 (HumanLayer)
        approval_request = await self._approval_service.request_approval(
            sql_query, user_context, validation_result
        )
        
        # 4. 승인 대기
        await approval_request.wait_for_approval()
        
        # 5. 승인된 쿼리 실행
        return await self._execute_approved_query(sql_query)
```

### GraphRAG 시스템 설계
```python
class MedicalGraphRAG:
    """의료 도메인 특화 GraphRAG 시스템"""
    
    def __init__(self,
                 vector_store: VectorStoreInterface,
                 graph_db: GraphDatabaseInterface,
                 embedding_service: EmbeddingServiceInterface):
        self._vector_store = vector_store
        self._graph_db = graph_db
        self._embedding_service = embedding_service
    
    async def enhance_query_with_context(self, 
                                       question: str) -> EnhancedQuery:
        """의료 온톨로지 기반 컨텍스트 강화"""
        # 1. 의료 용어 추출
        medical_entities = await self._extract_medical_entities(question)
        
        # 2. 그래프 탐색으로 관련 개념 확장
        related_concepts = await self._graph_db.find_related_concepts(
            medical_entities
        )
        
        # 3. 벡터 검색으로 유사 사례 검색
        similar_cases = await self._vector_store.similarity_search(
            question, related_concepts
        )
        
        return EnhancedQuery(
            original=question,
            entities=medical_entities,
            related_concepts=related_concepts,
            similar_cases=similar_cases
        )
```

## 🔄 HumanLayer 승인 워크플로우

### 승인 프로세스 설계
```python
class ApprovalWorkflow:
    """승인 워크플로우 관리"""
    
    async def request_sql_execution_approval(self, 
                                           sql_query: SQLQuery,
                                           user: User,
                                           risk_level: RiskLevel) -> ApprovalRequest:
        """SQL 실행 승인 요청"""
        
        approval_request = ApprovalRequest(
            id=uuid.uuid4(),
            type=ApprovalType.SQL_EXECUTION,
            requester=user,
            risk_level=risk_level,
            metadata={
                "sql": sql_query.text,
                "estimated_impact": sql_query.estimated_impact,
                "data_sensitivity": sql_query.data_sensitivity,
                "explanation": sql_query.natural_language_explanation
            }
        )
        
        # HumanLayer 데몬에 승인 요청 전송
        await self._humanlayer_client.create_approval_request(
            approval_request
        )
        
        return approval_request
    
    async def handle_approval_decision(self, 
                                     request_id: str, 
                                     decision: ApprovalDecision) -> None:
        """승인 결정 처리"""
        request = await self._get_approval_request(request_id)
        
        if decision.approved:
            # 승인된 경우 실행 대기열에 추가
            await self._execution_queue.add(request)
        else:
            # 거절된 경우 사용자에게 피드백 전송
            await self._notification_service.send_rejection_feedback(
                request.requester, decision.feedback
            )
```

### Real-time 승인 인터페이스
```typescript
// Frontend React 컴포넌트
const ApprovalInterface: React.FC = () => {
  const [pendingApprovals, setPendingApprovals] = useState<ApprovalRequest[]>([]);
  
  // WebSocket으로 실시간 승인 요청 수신
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:3001/ws/approvals`);
    
    ws.onmessage = (event) => {
      const approval = JSON.parse(event.data);
      setPendingApprovals(prev => [...prev, approval]);
    };
    
    return () => ws.close();
  }, []);
  
  const handleApprove = async (requestId: string, feedback?: string) => {
    await api.approveRequest(requestId, feedback);
    setPendingApprovals(prev => 
      prev.filter(req => req.id !== requestId)
    );
  };
  
  // UI 렌더링...
};
```

## 📊 데이터 연동 설계

### AI Hub 헬스케어 데이터 처리
```python
class AIHubDataProcessor:
    """AI Hub 헬스케어 데이터 처리"""
    
    def __init__(self, 
                 etl_service: ETLServiceInterface,
                 vector_store: VectorStoreInterface):
        self._etl_service = etl_service
        self._vector_store = vector_store
    
    async def process_medical_knowledge_data(self, 
                                           data_path: str) -> ProcessingResult:
        """의학 지식 데이터 처리 및 벡터화"""
        # 1. 원본 데이터 추출
        raw_data = await self._etl_service.extract_from_zip(data_path)
        
        # 2. 의료 텍스트 전처리
        processed_docs = await self._preprocess_medical_texts(raw_data)
        
        # 3. 임베딩 생성 및 벡터 저장소 저장
        embeddings = await self._generate_embeddings(processed_docs)
        await self._vector_store.store_embeddings(embeddings)
        
        # 4. 의료 온톨로지 그래프 구축
        knowledge_graph = await self._build_medical_ontology(processed_docs)
        
        return ProcessingResult(
            documents_processed=len(processed_docs),
            embeddings_created=len(embeddings),
            ontology_nodes=knowledge_graph.node_count
        )
```

### Mock 의료 데이터베이스 설계
```sql
-- 테스트용 의료 데이터베이스 스키마
-- Star Schema 기반 설계

-- 환자 차원 테이블
CREATE TABLE dim_patient (
    patient_key SERIAL PRIMARY KEY,
    patient_id VARCHAR(20) UNIQUE NOT NULL,
    age_group VARCHAR(10),  -- '20대', '30대', etc.
    gender VARCHAR(10),     -- '남', '여'
    region VARCHAR(20),     -- '서울', '경기', etc.
    blood_type VARCHAR(5),  -- 'A', 'B', 'O', 'AB'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 진단 차원 테이블
CREATE TABLE dim_diagnosis (
    diagnosis_key SERIAL PRIMARY KEY,
    kcd_code VARCHAR(10) NOT NULL,        -- K041, E119 etc.
    diagnosis_name_kor VARCHAR(200),      -- 한국어 진단명
    diagnosis_name_eng VARCHAR(200),      -- 영어 진단명
    category VARCHAR(100),                -- 질병 분류
    severity VARCHAR(20),                 -- 경증, 중등도, 중증
    created_at TIMESTAMP DEFAULT NOW()
);

-- 시간 차원 테이블
CREATE TABLE dim_time (
    time_key SERIAL PRIMARY KEY,
    date_value DATE UNIQUE NOT NULL,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    day INTEGER,
    day_of_week INTEGER,
    is_weekend BOOLEAN,
    season VARCHAR(10)
);

-- 진료 사실 테이블
CREATE TABLE fact_medical_visit (
    visit_key SERIAL PRIMARY KEY,
    patient_key INTEGER REFERENCES dim_patient(patient_key),
    diagnosis_key INTEGER REFERENCES dim_diagnosis(diagnosis_key),
    time_key INTEGER REFERENCES dim_time(time_key),
    visit_type VARCHAR(20),      -- 외래, 입원, 응급
    department VARCHAR(50),      -- 진료과
    length_of_stay INTEGER,      -- 재원일수
    total_cost DECIMAL(12,2),    -- 총 진료비
    medication_count INTEGER,    -- 처방 약물 수
    test_count INTEGER,          -- 검사 횟수
    created_at TIMESTAMP DEFAULT NOW()
);

-- 검사 결과 사실 테이블
CREATE TABLE fact_lab_result (
    result_key SERIAL PRIMARY KEY,
    patient_key INTEGER REFERENCES dim_patient(patient_key),
    time_key INTEGER REFERENCES dim_time(time_key),
    test_code VARCHAR(20),
    test_name VARCHAR(100),
    result_value DECIMAL(10,4),
    result_unit VARCHAR(20),
    reference_min DECIMAL(10,4),
    reference_max DECIMAL(10,4),
    abnormal_flag VARCHAR(10),   -- NORMAL, HIGH, LOW, CRITICAL
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔧 구현 단계별 계획

### Phase 1: TDD 인프라 구축 (Week 1)
1. **테스트 환경 설정**
   - pytest 설정 및 테스트 구조 생성
   - Mock 데이터 및 Fixture 준비
   - CI/CD 파이프라인 테스트 통합

2. **도메인 계층 TDD**
   - 환자, 진단, SQL쿼리 엔티티 테스트 작성
   - Value Object 테스트 작성
   - 도메인 서비스 테스트 작성

### Phase 2: 핵심 기능 TDD 개발 (Week 2-3)
1. **Text2SQL 엔진**
   - 자연어 처리 로직 테스트
   - SQL 생성 및 검증 테스트
   - 보안 검증 테스트

2. **승인 워크플로우**
   - HumanLayer 통합 테스트
   - 승인 프로세스 테스트
   - 실시간 알림 테스트

### Phase 3: 데이터 통합 및 UI (Week 4)
1. **AI Hub 데이터 연동**
   - ETL 파이프라인 테스트
   - 벡터 저장소 통합 테스트
   - 의료 온톨로지 구축 테스트

2. **프론트엔드 컴포넌트**
   - React 컴포넌트 테스트
   - 사용자 워크플로우 E2E 테스트

## 📈 성공 지표

### 기술적 지표
- **테스트 커버리지**: 85% 이상
- **빌드 성공률**: 98% 이상
- **API 응답 시간**: 평균 500ms 이하
- **승인 프로세스 시간**: 평균 2분 이하

### 품질 지표
- **Text2SQL 정확도**: 90% 이상
- **보안 검증 정확도**: 99% 이상
- **사용자 만족도**: 4.0/5.0 이상

### 개발 프로세스 지표
- **TDD 사이클 준수율**: 95% 이상
- **코드 리뷰 완료율**: 100%
- **자동화된 테스트 실행**: 매 커밋마다

## 🔐 보안 고려사항

### 의료 데이터 보안
- **데이터 비식별화**: 모든 개인정보 마스킹
- **접근 권한 관리**: Role-based 액세스 제어
- **감사 로깅**: 모든 데이터 접근 기록

### SQL 인젝션 방지
- **매개변수화 쿼리**: PreparedStatement 사용
- **입력 검증**: 모든 사용자 입력 검증
- **쿼리 분석**: AST 파싱으로 위험 쿼리 탐지

이 설계를 기반으로 실제 TDD 개발을 시작하겠습니다.