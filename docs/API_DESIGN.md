# K-BANK 메타데이터 AI 플랫폼 API 설계서

**버전:** 1.0  
**작성일:** 2025-11-25  
**기반:** RFP 요구사항, 아키텍처 설계서, 사이드바 메뉴 기획서  
**API 스타일:** RESTful + GraphQL (모델링 영역)

---

## 📋 API 설계 개요

### 설계 원칙
- **RESTful 아키텍처** 기반 일관성 있는 설계
- **OpenAPI 3.0** 표준 준수
- **마이크로서비스** 아키텍처 지원
- **K-BANK 보안** 정책 적용
- **버전 관리** 및 하위 호환성 보장

### API Gateway 구성
```
https://api.kbanknow.com/metadata/v1/
├── /auth         - 인증/인가
├── /metadata     - 메타데이터 관리
├── /standards    - 데이터 표준 관리
├── /modeling     - 데이터 모델링
├── /dataflow     - 데이터 흐름 관리
├── /ai           - AI 서비스
├── /integration  - 외부 연계
└── /system       - 시스템 관리
```

### 공통 요소

#### 인증 헤더
```http
Authorization: Bearer {jwt_token}
X-User-ID: {user_id}
X-User-Roles: {comma_separated_roles}
X-Request-ID: {uuid}
Content-Type: application/json
```

#### 공통 응답 형식
```json
{
  "success": true,
  "data": {},
  "message": "Success",
  "timestamp": "2025-11-25T10:30:00Z",
  "request_id": "uuid",
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

#### 에러 응답 형식
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": [
      {
        "field": "table_name",
        "message": "Table name is required"
      }
    ]
  },
  "timestamp": "2025-11-25T10:30:00Z",
  "request_id": "uuid"
}
```

---

## 🔐 1. 인증/인가 API

### 1.1 JWT 토큰 발급
```http
POST /api/v1/auth/login
```

**Request:**
```json
{
  "username": "user123",
  "password": "encrypted_password",
  "grant_type": "password"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user_info": {
      "user_id": "user123",
      "username": "user123",
      "full_name": "홍길동",
      "email": "hong@kbanknow.com",
      "department": "IT운영팀",
      "roles": ["DATA_ANALYST", "METADATA_USER"]
    }
  }
}
```

### 1.2 토큰 갱신
```http
POST /api/v1/auth/refresh
```

### 1.3 SSO 로그인 (SAML)
```http
GET /api/v1/auth/sso/saml
POST /api/v1/auth/sso/callback
```

### 1.4 권한 확인
```http
GET /api/v1/auth/permissions
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "user123",
    "permissions": [
      "metadata:read",
      "metadata:write",
      "standards:read",
      "modeling:read"
    ],
    "menu_access": {
      "dashboard": true,
      "metadata": true,
      "standards": true,
      "modeling": false,
      "dataflow": true,
      "ai": false
    }
  }
}
```

---

## 📊 2. 메타데이터 관리 API

### 2.1 데이터베이스 관리

#### 2.1.1 데이터베이스 목록 조회
```http
GET /api/v1/metadata/databases
```

**Query Parameters:**
- `page` (integer): 페이지 번호 (default: 1)
- `size` (integer): 페이지 크기 (default: 20)
- `db_type` (string): 데이터베이스 타입 필터
- `status` (string): 연결 상태 필터

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "db_id": "db001",
      "db_name": "고객관리DB",
      "db_type": "ORACLE",
      "host_name": "oracle-prod-01.kbank.com",
      "port_number": 1521,
      "database_name": "CUSTDB",
      "connection_status": "ACTIVE",
      "last_sync_datetime": "2025-11-25T09:30:00Z",
      "sync_status": "SUCCESS",
      "table_count": 145,
      "total_size_gb": 250.5
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 9,
    "total_pages": 1
  }
}
```

#### 2.1.2 데이터베이스 등록
```http
POST /api/v1/metadata/databases
```

**Request:**
```json
{
  "db_name": "신규데이터베이스",
  "db_type": "EDB",
  "host_name": "edb-dev-01.kbank.com",
  "port_number": 5432,
  "database_name": "newdb",
  "username": "kbank_user",
  "password": "encrypted_password",
  "connection_url": "jdbc:edb://edb-dev-01.kbank.com:5432/newdb"
}
```

#### 2.1.3 데이터베이스 연결 테스트
```http
POST /api/v1/metadata/databases/{db_id}/test-connection
```

#### 2.1.4 스키마 동기화
```http
POST /api/v1/metadata/databases/{db_id}/sync
```

**Request:**
```json
{
  "sync_type": "FULL", // FULL, INCREMENTAL
  "target_schemas": ["public", "hr", "finance"],
  "include_system_tables": false
}
```

### 2.2 테이블 관리

#### 2.2.1 테이블 목록 조회
```http
GET /api/v1/metadata/tables
```

**Query Parameters:**
- `db_id` (string): 데이터베이스 ID
- `schema_name` (string): 스키마명 필터
- `table_name` (string): 테이블명 검색
- `data_classification` (string): 데이터 분류 필터
- `contains_personal_info` (boolean): 개인정보 포함 여부
- `sort` (string): 정렬 기준 (name, size, modified_date)
- `order` (string): 정렬 방향 (asc, desc)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "table_id": "tbl001",
      "db_id": "db001",
      "schema_name": "public",
      "table_name": "customer",
      "table_comment": "고객 기본 정보",
      "business_description": "케이뱅크 고객의 기본 정보를 관리하는 마스터 테이블",
      "owner_team": "고객관리팀",
      "data_classification": "CONFIDENTIAL",
      "contains_personal_info": true,
      "contains_sensitive_info": true,
      "record_count": 1245678,
      "data_size_mb": 2048.5,
      "column_count": 25,
      "personal_info_columns": 5,
      "created_date": "2023-01-15",
      "last_modified_date": "2025-11-20"
    }
  ]
}
```

#### 2.2.2 테이블 상세 조회
```http
GET /api/v1/metadata/tables/{table_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "table_id": "tbl001",
    "basic_info": {
      "db_id": "db001",
      "schema_name": "public",
      "table_name": "customer",
      "table_type": "TABLE",
      "table_comment": "고객 기본 정보",
      "business_description": "케이뱅크 고객의 기본 정보를 관리하는 마스터 테이블"
    },
    "metadata": {
      "owner_team": "고객관리팀",
      "data_classification": "CONFIDENTIAL",
      "contains_personal_info": true,
      "record_count": 1245678,
      "data_size_mb": 2048.5,
      "partition_type": "RANGE",
      "partition_key": "created_date"
    },
    "compliance": {
      "retention_period_days": 1825,
      "archival_policy": "CUSTOMER_RETENTION_POLICY",
      "backup_required": true,
      "encryption_required": true
    },
    "columns": [
      {
        "column_id": "col001",
        "column_name": "customer_id",
        "data_type": "VARCHAR",
        "max_length": 20,
        "is_nullable": false,
        "is_primary_key": true,
        "column_comment": "고객 식별자",
        "is_personal_info": false
      },
      {
        "column_id": "col002",
        "column_name": "customer_name",
        "data_type": "VARCHAR",
        "max_length": 100,
        "is_nullable": false,
        "is_encrypted": true,
        "column_comment": "고객명",
        "is_personal_info": true,
        "personal_info_type": "NAME"
      }
    ],
    "indexes": [
      {
        "index_id": "idx001",
        "index_name": "pk_customer",
        "index_type": "PRIMARY",
        "column_list": ["customer_id"],
        "is_unique": true
      }
    ],
    "relationships": {
      "referenced_by": [
        {
          "table_name": "account",
          "relationship_type": "1:M",
          "foreign_key": "customer_id"
        }
      ],
      "references": []
    }
  }
}
```

#### 2.2.3 테이블 정보 수정
```http
PUT /api/v1/metadata/tables/{table_id}
```

#### 2.2.4 테이블 삭제
```http
DELETE /api/v1/metadata/tables/{table_id}
```

### 2.3 컬럼 관리

#### 2.3.1 컬럼 목록 조회
```http
GET /api/v1/metadata/tables/{table_id}/columns
```

#### 2.3.2 컬럼 상세 조회
```http
GET /api/v1/metadata/columns/{column_id}
```

#### 2.3.3 컬럼 정보 수정
```http
PUT /api/v1/metadata/columns/{column_id}
```

### 2.4 검색 및 통계

#### 2.4.1 통합 검색
```http
GET /api/v1/metadata/search
```

**Query Parameters:**
- `q` (string, required): 검색어
- `type` (string): 검색 타입 (table, column, all)
- `db_id` (string): 데이터베이스 필터
- `schema` (string): 스키마 필터

**Response:**
```json
{
  "success": true,
  "data": {
    "query": "고객",
    "total_results": 25,
    "tables": [
      {
        "table_id": "tbl001",
        "table_name": "customer",
        "schema_name": "public",
        "relevance_score": 0.95,
        "matched_fields": ["table_name", "table_comment"]
      }
    ],
    "columns": [
      {
        "column_id": "col001",
        "column_name": "customer_id",
        "table_name": "customer",
        "relevance_score": 0.87,
        "matched_fields": ["column_name"]
      }
    ]
  }
}
```

#### 2.4.2 메타데이터 통계
```http
GET /api/v1/metadata/statistics
```

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_databases": 9,
      "total_tables": 1456,
      "total_columns": 23890,
      "total_size_gb": 5423.2
    },
    "by_database": [
      {
        "db_name": "고객관리DB",
        "table_count": 145,
        "column_count": 2890,
        "size_gb": 250.5
      }
    ],
    "data_classification": {
      "PUBLIC": 234,
      "INTERNAL": 567,
      "CONFIDENTIAL": 456,
      "RESTRICTED": 199
    },
    "personal_info_tables": 287,
    "compliance_stats": {
      "backup_enabled": 1398,
      "encryption_required": 287,
      "archival_policy_set": 1234
    }
  }
}
```

---

## 📝 3. 데이터 표준 관리 API

### 3.1 단어 관리

#### 3.1.1 단어 목록 조회
```http
GET /api/v1/standards/words
```

**Query Parameters:**
- `page`, `size`: 페이지네이션
- `word_name` (string): 단어명 검색
- `approval_status` (string): 승인 상태 필터
- `business_domain` (string): 업무 영역 필터

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "word_id": "word001",
      "word_name": "고객",
      "word_english_name": "Customer",
      "word_abbreviation": "CUST",
      "word_definition": "케이뱅크 서비스를 이용하는 개인 또는 법인",
      "business_domain": "고객관리",
      "approval_status": "APPROVED",
      "synonym_list": ["클라이언트", "이용자"],
      "usage_count": 45,
      "created_by": "admin",
      "created_datetime": "2025-01-15T10:30:00Z",
      "approved_by": "data_admin",
      "approved_datetime": "2025-01-16T14:20:00Z"
    }
  ]
}
```

#### 3.1.2 단어 등록
```http
POST /api/v1/standards/words
```

**Request:**
```json
{
  "word_name": "계좌",
  "word_english_name": "Account",
  "word_abbreviation": "ACCT",
  "word_definition": "고객이 금융거래를 위해 개설한 계정",
  "usage_example": "고객 계좌에서 이체 거래를 수행한다.",
  "business_domain": "계좌관리",
  "synonym_list": ["어카운트", "계정"],
  "antonym_list": [],
  "forbidden_words": ["통장"]
}
```

#### 3.1.3 단어 승인
```http
POST /api/v1/standards/words/{word_id}/approve
```

**Request:**
```json
{
  "approval_action": "APPROVE", // APPROVE, REJECT
  "approval_comment": "업무 정의가 명확하여 승인합니다."
}
```

#### 3.1.4 중복 단어 검사
```http
POST /api/v1/standards/words/check-duplicates
```

**Request:**
```json
{
  "word_name": "고객"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "is_duplicate": true,
    "existing_words": [
      {
        "word_id": "word001",
        "word_name": "고객",
        "similarity_score": 1.0
      }
    ],
    "similar_words": [
      {
        "word_id": "word002",
        "word_name": "고객사",
        "similarity_score": 0.85
      }
    ]
  }
}
```

### 3.2 용어 관리

#### 3.2.1 용어 목록 조회
```http
GET /api/v1/standards/terms
```

#### 3.2.2 용어 등록
```http
POST /api/v1/standards/terms
```

#### 3.2.3 용어 구성 분석
```http
GET /api/v1/standards/terms/{term_id}/word-composition
```

**Response:**
```json
{
  "success": true,
  "data": {
    "term_id": "term001",
    "term_name": "고객계좌번호",
    "word_composition": [
      {
        "word_id": "word001",
        "word_name": "고객",
        "position": 1
      },
      {
        "word_id": "word002",
        "word_name": "계좌",
        "position": 2
      },
      {
        "word_id": "word003",
        "word_name": "번호",
        "position": 3
      }
    ],
    "composition_valid": true,
    "compliance_score": 0.95
  }
}
```

### 3.3 도메인 관리

#### 3.3.1 도메인 목록 조회
```http
GET /api/v1/standards/domains
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "domain_id": "dom001",
      "domain_name": "고객ID",
      "domain_description": "고객을 식별하는 유일한 식별자",
      "logical_data_type": "문자열",
      "physical_data_type_oracle": "VARCHAR2(20)",
      "physical_data_type_edb": "VARCHAR(20)",
      "max_length": 20,
      "min_length": 10,
      "validation_rule": "^[A-Z0-9]{10,20}$",
      "format_pattern": "CUST{YYYYMMDD}{SequenceNo}",
      "example_values": ["CUST202511250001", "CUST202511250002"],
      "null_allowed": false,
      "encryption_required": false,
      "usage_count": 156
    }
  ]
}
```

#### 3.3.2 도메인 매핑 확인
```http
GET /api/v1/standards/domains/{domain_id}/mappings
```

**Response:**
```json
{
  "success": true,
  "data": {
    "domain_id": "dom001",
    "domain_name": "고객ID",
    "mapped_columns": [
      {
        "table_name": "customer",
        "column_name": "customer_id",
        "compliance_status": "COMPLIANT"
      },
      {
        "table_name": "account",
        "column_name": "customer_id",
        "compliance_status": "COMPLIANT"
      }
    ],
    "non_compliant_columns": [
      {
        "table_name": "old_customer",
        "column_name": "cust_no",
        "compliance_issues": ["NAMING_RULE", "DATA_TYPE"]
      }
    ]
  }
}
```

### 3.4 코드 관리

#### 3.4.1 코드 그룹 목록 조회
```http
GET /api/v1/standards/codes
```

#### 3.4.2 코드 상세 목록 조회
```http
GET /api/v1/standards/codes/{code_id}/details
```

**Response:**
```json
{
  "success": true,
  "data": {
    "code_id": "code001",
    "code_name": "고객유형코드",
    "code_description": "고객의 유형을 구분하는 코드",
    "details": [
      {
        "code_value": "01",
        "code_name": "개인고객",
        "code_description": "개인 자연인 고객",
        "sort_order": 1,
        "is_active": true,
        "effective_start_date": "2023-01-01",
        "effective_end_date": null
      },
      {
        "code_value": "02",
        "code_name": "법인고객",
        "code_description": "법인 사업자 고객",
        "sort_order": 2,
        "is_active": true
      }
    ]
  }
}
```

### 3.5 표준 준수율

#### 3.5.1 준수율 통계 조회
```http
GET /api/v1/standards/compliance
```

**Query Parameters:**
- `db_id` (string): 데이터베이스 필터
- `schema_name` (string): 스키마 필터
- `date_range` (string): 날짜 범위 (7d, 30d, 90d)

**Response:**
```json
{
  "success": true,
  "data": {
    "overall_compliance": {
      "total_columns": 23890,
      "compliant_columns": 21501,
      "compliance_rate": 90.01,
      "target_rate": 90.00,
      "trend": "IMPROVING"
    },
    "by_category": {
      "word_compliance_rate": 92.5,
      "domain_compliance_rate": 88.3,
      "naming_compliance_rate": 89.7
    },
    "by_database": [
      {
        "db_name": "고객관리DB",
        "compliance_rate": 95.2,
        "total_columns": 2890,
        "compliant_columns": 2751
      }
    ],
    "non_compliant_items": [
      {
        "table_name": "old_customer",
        "column_name": "cust_no",
        "issues": ["NAMING_RULE", "DOMAIN_MISMATCH"],
        "severity": "HIGH"
      }
    ]
  }
}
```

#### 3.5.2 표준화 실행
```http
POST /api/v1/standards/compliance/remediate
```

**Request:**
```json
{
  "remediation_type": "AUTO", // AUTO, MANUAL, REVIEW
  "target_tables": ["old_customer", "legacy_account"],
  "dry_run": true,
  "auto_approve": false
}
```

---

## 🏗️ 4. 데이터 모델링 API

### 4.1 GraphQL API

데이터 모델링은 복잡한 관계형 데이터를 다루므로 GraphQL을 사용합니다.

#### 4.1.1 GraphQL Endpoint
```http
POST /api/v1/modeling/graphql
```

#### 4.1.2 Schema Definition
```graphql
type Project {
  id: ID!
  name: String!
  description: String
  businessDomain: String
  projectType: ProjectType!
  status: ProjectStatus!
  entities: [Entity!]!
  relationships: [Relationship!]!
  versions: [Version!]!
  createdBy: String!
  createdAt: DateTime!
}

type Entity {
  id: ID!
  projectId: ID!
  name: String!
  logicalName: String!
  description: String
  entityType: EntityType!
  subjectArea: String
  attributes: [Attribute!]!
  relationships: [Relationship!]!
  position: Position
  style: Style
}

type Attribute {
  id: ID!
  entityId: ID!
  name: String!
  logicalName: String!
  description: String
  domainId: ID
  domain: Domain
  dataType: String!
  maxLength: Int
  isPrimaryKey: Boolean!
  isForeignKey: Boolean!
  isNotNull: Boolean!
  order: Int!
}

type Relationship {
  id: ID!
  projectId: ID!
  name: String!
  parentEntityId: ID!
  childEntityId: ID!
  parentEntity: Entity!
  childEntity: Entity!
  relationshipType: RelationshipType!
  cardinality: Cardinality!
  optionality: Optionality!
}

enum ProjectType {
  LOGICAL
  PHYSICAL
  CONCEPTUAL
}

enum EntityType {
  MASTER
  TRANSACTION
  CODE
  HISTORY
  LOG
}

enum RelationshipType {
  IDENTIFYING
  NON_IDENTIFYING
  SUPER_SUB
}
```

#### 4.1.3 주요 Query 예시

**프로젝트 목록 조회:**
```graphql
query GetProjects($filter: ProjectFilter) {
  projects(filter: $filter) {
    id
    name
    description
    projectType
    status
    createdAt
    entityCount
    lastModified
  }
}
```

**프로젝트 상세 조회:**
```graphql
query GetProject($id: ID!) {
  project(id: $id) {
    id
    name
    description
    entities {
      id
      name
      logicalName
      entityType
      position {
        x
        y
      }
      attributes {
        id
        name
        logicalName
        dataType
        isPrimaryKey
        isForeignKey
        order
      }
    }
    relationships {
      id
      name
      parentEntity {
        id
        name
      }
      childEntity {
        id
        name
      }
      relationshipType
      cardinality
    }
  }
}
```

**엔터티 생성:**
```graphql
mutation CreateEntity($input: CreateEntityInput!) {
  createEntity(input: $input) {
    id
    name
    logicalName
    description
    entityType
  }
}
```

### 4.2 RESTful API (보조)

#### 4.2.1 모델 내보내기
```http
GET /api/v1/modeling/projects/{project_id}/export
```

**Query Parameters:**
- `format` (string): 내보내기 형식 (json, xml, erwin, ddl)
- `include_data` (boolean): 샘플 데이터 포함 여부

#### 4.2.2 모델 가져오기
```http
POST /api/v1/modeling/projects/import
```

**Request (Multipart):**
```
Content-Type: multipart/form-data

file: [모델 파일]
format: erwin
project_name: 신규프로젝트
overwrite: false
```

#### 4.2.3 DDL 생성
```http
POST /api/v1/modeling/projects/{project_id}/generate-ddl
```

**Request:**
```json
{
  "target_database": "EDB",
  "include_comments": true,
  "include_indexes": true,
  "include_constraints": true,
  "naming_convention": "KBANK_STANDARD"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "ddl_script": "CREATE TABLE customer (\n  customer_id VARCHAR(20) PRIMARY KEY...",
    "script_size": 15420,
    "table_count": 45,
    "warnings": [
      {
        "entity_name": "old_customer",
        "warning": "Entity name does not follow naming convention"
      }
    ]
  }
}
```

### 4.3 버전 관리

#### 4.3.1 버전 목록 조회
```http
GET /api/v1/modeling/projects/{project_id}/versions
```

#### 4.3.2 새 버전 생성
```http
POST /api/v1/modeling/projects/{project_id}/versions
```

**Request:**
```json
{
  "version_number": "1.2.0",
  "version_description": "고객 테이블 구조 개선",
  "change_summary": "고객 테이블에 마케팅 동의 여부 컬럼 추가",
  "baseline_version": false
}
```

#### 4.3.3 버전 비교
```http
GET /api/v1/modeling/projects/{project_id}/versions/compare
```

**Query Parameters:**
- `from_version` (string): 비교 기준 버전
- `to_version` (string): 비교 대상 버전

**Response:**
```json
{
  "success": true,
  "data": {
    "comparison": {
      "from_version": "1.1.0",
      "to_version": "1.2.0",
      "changes": {
        "entities_added": [
          {
            "entity_name": "marketing_consent",
            "entity_type": "TRANSACTION"
          }
        ],
        "entities_modified": [
          {
            "entity_name": "customer",
            "changes": {
              "attributes_added": ["marketing_consent_yn", "consent_date"]
            }
          }
        ],
        "entities_removed": [],
        "relationships_added": [
          {
            "relationship_name": "customer_consent",
            "parent_entity": "customer",
            "child_entity": "marketing_consent"
          }
        ]
      }
    }
  }
}
```

---

## 🌊 5. 데이터 흐름 관리 API

### 5.1 프로그램 분석

#### 5.1.1 프로그램 등록 및 분석 요청
```http
POST /api/v1/dataflow/programs
```

**Request:**
```json
{
  "program_name": "고객정보수정배치",
  "program_type": "BATCH",
  "programming_language": "JAVA",
  "file_path": "/app/batch/customer/CustomerUpdateBatch.java",
  "program_description": "고객 정보를 외부 시스템에서 받아 업데이트하는 배치",
  "business_purpose": "외부 채널에서 변경된 고객 정보를 실시간으로 반영",
  "execution_schedule": "0 */10 * * * *",
  "owner_team": "고객관리팀"
}
```

#### 5.1.2 분석 상태 조회
```http
GET /api/v1/dataflow/programs/{program_id}/analysis-status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "program_id": "prog001",
    "analysis_status": "SUCCESS",
    "last_analysis_datetime": "2025-11-25T10:30:00Z",
    "analysis_result": {
      "flows_detected": 12,
      "tables_accessed": 8,
      "sql_statements": 15,
      "complexity_score": "MEDIUM"
    },
    "error_message": null
  }
}
```

### 5.2 데이터 흐름 조회

#### 5.2.1 테이블 기준 흐름 조회
```http
GET /api/v1/dataflow/tables/{table_id}/flows
```

**Query Parameters:**
- `direction` (string): 흐름 방향 (inbound, outbound, both)
- `depth` (integer): 탐색 깊이 (default: 3)
- `include_indirect` (boolean): 간접 흐름 포함

**Response:**
```json
{
  "success": true,
  "data": {
    "table_id": "tbl001",
    "table_name": "customer",
    "inbound_flows": [
      {
        "flow_id": "flow001",
        "source_table": "external_customer_feed",
        "flow_type": "INSERT",
        "program_name": "고객정보동기화배치",
        "execution_frequency": "실시간",
        "data_volume": 1000,
        "last_execution": "2025-11-25T10:25:00Z"
      }
    ],
    "outbound_flows": [
      {
        "flow_id": "flow002",
        "target_table": "customer_mart",
        "flow_type": "SELECT",
        "program_name": "고객마트생성ETL",
        "execution_frequency": "일 1회",
        "data_volume": 1245678,
        "transformation": "집계 및 비식별화 처리"
      }
    ]
  }
}
```

#### 5.2.2 프로그램 기준 흐름 조회
```http
GET /api/v1/dataflow/programs/{program_id}/flows
```

### 5.3 영향도 분석

#### 5.3.1 테이블 영향도 분석
```http
GET /api/v1/dataflow/impact-analysis/table/{table_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "source_table": {
      "table_id": "tbl001",
      "table_name": "customer",
      "schema_name": "public"
    },
    "impact_summary": {
      "direct_impact_tables": 5,
      "indirect_impact_tables": 23,
      "affected_programs": 15,
      "total_impact_score": 0.85,
      "risk_level": "HIGH"
    },
    "direct_impacts": [
      {
        "impact_table": "account",
        "impact_type": "REFERENTIAL_INTEGRITY",
        "impact_score": 0.95,
        "relationship": "FOREIGN_KEY",
        "affected_columns": ["customer_id"]
      }
    ],
    "indirect_impacts": [
      {
        "impact_table": "transaction_history",
        "impact_distance": 2,
        "impact_score": 0.75,
        "impact_path": ["customer", "account", "transaction_history"]
      }
    ],
    "affected_programs": [
      {
        "program_name": "고객통합조회API",
        "program_type": "API",
        "impact_type": "DATA_ACCESS",
        "risk_level": "MEDIUM"
      }
    ]
  }
}
```

#### 5.3.2 컬럼 영향도 분석
```http
GET /api/v1/dataflow/impact-analysis/column/{column_id}
```

#### 5.3.3 변경 시뮬레이션
```http
POST /api/v1/dataflow/impact-analysis/simulate
```

**Request:**
```json
{
  "change_type": "COLUMN_MODIFY",
  "target_entity": {
    "type": "COLUMN",
    "table_id": "tbl001",
    "column_id": "col002"
  },
  "change_details": {
    "current_data_type": "VARCHAR(100)",
    "new_data_type": "VARCHAR(200)",
    "nullable_change": false
  }
}
```

### 5.4 CRUD 매트릭스

#### 5.4.1 테이블별 CRUD 조회
```http
GET /api/v1/dataflow/crud-matrix/table/{table_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "table_info": {
      "table_id": "tbl001",
      "table_name": "customer",
      "total_programs": 15
    },
    "crud_matrix": [
      {
        "program_name": "고객등록API",
        "program_type": "API",
        "create": true,
        "read": false,
        "update": false,
        "delete": false,
        "access_frequency": "HIGH",
        "last_access": "2025-11-25T10:20:00Z"
      },
      {
        "program_name": "고객조회API",
        "program_type": "API",
        "create": false,
        "read": true,
        "update": false,
        "delete": false,
        "access_frequency": "HIGH"
      },
      {
        "program_name": "고객정보수정배치",
        "program_type": "BATCH",
        "create": false,
        "read": true,
        "update": true,
        "delete": false,
        "access_frequency": "MEDIUM"
      }
    ],
    "summary": {
      "create_programs": 3,
      "read_programs": 12,
      "update_programs": 5,
      "delete_programs": 1
    }
  }
}
```

### 5.5 흐름 시각화 데이터

#### 5.5.1 시각화용 그래프 데이터
```http
GET /api/v1/dataflow/visualization/graph
```

**Query Parameters:**
- `center_table` (string): 중심 테이블 ID
- `depth` (integer): 탐색 깊이
- `layout` (string): 레이아웃 타입 (force, hierarchy, circular)

**Response:**
```json
{
  "success": true,
  "data": {
    "nodes": [
      {
        "id": "tbl001",
        "label": "customer",
        "type": "table",
        "size": 1245678,
        "classification": "CONFIDENTIAL",
        "color": "#ff6b6b",
        "position": {"x": 100, "y": 150}
      },
      {
        "id": "prog001",
        "label": "고객등록API",
        "type": "program",
        "language": "JAVA",
        "color": "#4ecdc4"
      }
    ],
    "edges": [
      {
        "id": "edge001",
        "source": "prog001",
        "target": "tbl001",
        "type": "INSERT",
        "weight": 1000,
        "color": "#51cf66",
        "label": "INSERT 1000건/일"
      }
    ],
    "layout_info": {
      "type": "force",
      "center": {"x": 400, "y": 300},
      "bounds": {"width": 800, "height": 600}
    }
  }
}
```

---

## 🤖 6. AI 서비스 API

### 6.1 자연어 질의

#### 6.1.1 질의 처리
```http
POST /api/v1/ai/query
```

**Request:**
```json
{
  "query_text": "고객 테이블에서 최근 1개월 신규 가입자 수를 알려줘",
  "query_type": "TEXT2SQL",
  "context": {
    "user_databases": ["db001", "db002"],
    "preferred_schema": "public",
    "session_id": "session123"
  },
  "llm_model": "gpt-4",
  "include_explanation": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "query_id": "query001",
    "query_text": "고객 테이블에서 최근 1개월 신규 가입자 수를 알려줘",
    "interpretation": {
      "intent": "COUNT_QUERY",
      "target_table": "customer",
      "time_filter": "최근 1개월",
      "metric": "신규 가입자 수"
    },
    "generated_sql": {
      "sql": "SELECT COUNT(*) as new_customers FROM public.customer WHERE created_date >= CURRENT_DATE - INTERVAL '1 month'",
      "explanation": "고객 테이블에서 생성일자가 최근 1개월 내인 레코드의 개수를 조회합니다.",
      "confidence_score": 0.95
    },
    "context_used": {
      "relevant_tables": ["customer"],
      "relevant_columns": ["created_date"],
      "business_rules": ["신규 가입자는 created_date 기준으로 판단"]
    },
    "suggestions": [
      "월별 신규 가입자 추이를 보려면 GROUP BY를 추가해보세요",
      "가입 채널별로 구분하려면 channel 컬럼을 함께 조회해보세요"
    ]
  }
}
```

#### 6.1.2 SQL 실행
```http
POST /api/v1/ai/query/{query_id}/execute
```

**Request:**
```json
{
  "database_id": "db001",
  "dry_run": true,
  "limit": 100
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "execution_result": {
      "status": "SUCCESS",
      "execution_time_ms": 245,
      "row_count": 1,
      "columns": [
        {
          "name": "new_customers",
          "type": "BIGINT"
        }
      ],
      "rows": [
        [1247]
      ],
      "execution_plan": {
        "estimated_cost": 1.23,
        "index_used": ["idx_customer_created_date"]
      }
    },
    "query_feedback": {
      "performance_score": "GOOD",
      "optimization_suggestions": []
    }
  }
}
```

### 6.2 추천 시스템

#### 6.2.1 모델링 추천
```http
POST /api/v1/ai/recommendations/modeling
```

**Request:**
```json
{
  "context_type": "ENTITY_DESIGN",
  "business_domain": "고객관리",
  "current_entities": ["customer", "account"],
  "business_requirements": "고객의 마케팅 동의 이력을 관리하고 싶습니다"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "type": "NEW_ENTITY",
        "confidence_score": 0.92,
        "recommendation": {
          "entity_name": "marketing_consent",
          "entity_logical_name": "마케팅동의이력",
          "entity_type": "TRANSACTION",
          "suggested_attributes": [
            {
              "name": "consent_id",
              "logical_name": "동의ID",
              "data_type": "VARCHAR(20)",
              "is_primary_key": true
            },
            {
              "name": "customer_id",
              "logical_name": "고객ID",
              "data_type": "VARCHAR(20)",
              "is_foreign_key": true
            },
            {
              "name": "consent_type",
              "logical_name": "동의유형",
              "data_type": "VARCHAR(10)"
            }
          ],
          "relationships": [
            {
              "parent_entity": "customer",
              "relationship_type": "NON_IDENTIFYING",
              "cardinality": "1:M"
            }
          ]
        },
        "reasoning": "고객별로 여러 종류의 마케팅 동의 이력을 시계열로 관리하기 위해서는 별도의 트랜잭션 엔터티가 필요합니다."
      }
    ]
  }
}
```

#### 6.2.2 표준 용어 추천
```http
POST /api/v1/ai/recommendations/terms
```

**Request:**
```json
{
  "input_text": "고객마케팅동의여부",
  "context": {
    "business_domain": "마케팅",
    "existing_terms": ["고객", "마케팅", "동의"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "input_analysis": {
      "detected_words": ["고객", "마케팅", "동의", "여부"],
      "compound_term": true,
      "standard_compliance": 0.75
    },
    "recommendations": [
      {
        "recommended_term": "고객마케팅동의여부",
        "confidence_score": 0.95,
        "reasoning": "기존 표준 단어들의 조합으로 구성 가능",
        "word_composition": [
          {"word": "고객", "standard_word_id": "word001"},
          {"word": "마케팅", "standard_word_id": "word015"},
          {"word": "동의", "standard_word_id": "word023"},
          {"word": "여부", "standard_word_id": "word008"}
        ]
      },
      {
        "recommended_term": "마케팅수신동의여부",
        "confidence_score": 0.87,
        "reasoning": "더 명확한 의미 전달을 위한 대안",
        "suggested_improvements": ["수신이라는 단어 추가로 의미 명확화"]
      }
    ]
  }
}
```

### 6.3 지식베이스 관리

#### 6.3.1 문서 임베딩
```http
POST /api/v1/ai/knowledge/embeddings
```

**Request:**
```json
{
  "content_type": "TABLE_SCHEMA",
  "content_id": "tbl001",
  "content_text": "customer 테이블은 케이뱅크 고객의 기본 정보를 관리하는 마스터 테이블입니다...",
  "metadata": {
    "schema_name": "public",
    "table_name": "customer",
    "business_domain": "고객관리"
  }
}
```

#### 6.3.2 유사 콘텐츠 검색
```http
POST /api/v1/ai/knowledge/search
```

**Request:**
```json
{
  "query_text": "고객 개인정보 관련 테이블",
  "content_types": ["TABLE_SCHEMA", "BUSINESS_RULE"],
  "similarity_threshold": 0.7,
  "max_results": 10
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "search_results": [
      {
        "content_id": "tbl001",
        "content_type": "TABLE_SCHEMA",
        "similarity_score": 0.95,
        "content_summary": "customer 테이블 - 고객 기본 정보 및 개인정보 관리",
        "metadata": {
          "table_name": "customer",
          "personal_info_columns": 5
        }
      },
      {
        "content_id": "rule001",
        "content_type": "BUSINESS_RULE",
        "similarity_score": 0.87,
        "content_summary": "개인정보 암호화 및 마스킹 정책",
        "metadata": {
          "policy_type": "PRIVACY"
        }
      }
    ]
  }
}
```

### 6.4 AI 모델 관리

#### 6.4.1 지원 모델 목록
```http
GET /api/v1/ai/models
```

**Response:**
```json
{
  "success": true,
  "data": {
    "available_models": [
      {
        "model_id": "gpt-4",
        "model_name": "GPT-4",
        "provider": "OpenAI",
        "capabilities": ["TEXT2SQL", "RECOMMENDATIONS", "ANALYSIS"],
        "max_tokens": 128000,
        "cost_per_1k_tokens": 0.03,
        "response_time_avg_ms": 2500,
        "availability": "AVAILABLE"
      },
      {
        "model_id": "claude-3",
        "model_name": "Claude 3 Sonnet",
        "provider": "Anthropic",
        "capabilities": ["TEXT2SQL", "RECOMMENDATIONS"],
        "max_tokens": 200000,
        "cost_per_1k_tokens": 0.015,
        "response_time_avg_ms": 1800,
        "availability": "AVAILABLE"
      }
    ]
  }
}
```

#### 6.4.2 모델 성능 통계
```http
GET /api/v1/ai/models/{model_id}/statistics
```

**Query Parameters:**
- `date_range` (string): 통계 기간 (7d, 30d, 90d)

**Response:**
```json
{
  "success": true,
  "data": {
    "model_id": "gpt-4",
    "period": "30d",
    "statistics": {
      "total_queries": 1247,
      "success_rate": 0.94,
      "avg_response_time_ms": 2350,
      "avg_confidence_score": 0.87,
      "user_satisfaction": {
        "avg_rating": 4.2,
        "total_feedback": 234
      },
      "query_types": {
        "TEXT2SQL": {
          "count": 856,
          "success_rate": 0.92,
          "avg_confidence": 0.89
        },
        "RECOMMENDATIONS": {
          "count": 391,
          "success_rate": 0.97,
          "avg_confidence": 0.84
        }
      },
      "cost_summary": {
        "total_tokens_used": 2450000,
        "total_cost_usd": 73.5
      }
    }
  }
}
```

---

## 🔗 7. 시스템 연계 API

### 7.1 IM/SSO 연계

#### 7.1.1 사용자 정보 동기화
```http
POST /api/v1/integration/im/sync-users
```

**Request:**
```json
{
  "sync_type": "INCREMENTAL", // FULL, INCREMENTAL
  "last_sync_datetime": "2025-11-24T10:00:00Z",
  "department_filter": ["IT운영팀", "데이터관리팀"]
}
```

#### 7.1.2 조직도 동기화
```http
POST /api/v1/integration/im/sync-organization
```

### 7.2 ITSM 연계

#### 7.2.1 변경 요청 생성
```http
POST /api/v1/integration/itsm/change-requests
```

**Request:**
```json
{
  "change_type": "DATA_MODEL_CHANGE",
  "title": "고객 테이블 컬럼 추가",
  "description": "마케팅 동의 여부 컬럼 추가",
  "business_justification": "GDPR 준수를 위한 개인정보 동의 관리 강화",
  "impact_assessment": {
    "affected_systems": ["CRM", "Marketing Platform"],
    "estimated_effort": "2MD",
    "risk_level": "LOW"
  },
  "metadata_changes": {
    "table_id": "tbl001",
    "change_details": {
      "columns_added": [
        {
          "column_name": "marketing_consent_yn",
          "data_type": "CHAR(1)",
          "description": "마케팅 동의 여부"
        }
      ]
    }
  },
  "approver_group": "DATA_GOVERNANCE_TEAM"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "change_request_id": "CHG-2025-001234",
    "status": "SUBMITTED",
    "submitted_datetime": "2025-11-25T10:30:00Z",
    "expected_approval_date": "2025-11-27T17:00:00Z",
    "tracking_url": "https://itsm.kbanknow.com/change-requests/CHG-2025-001234"
  }
}
```

#### 7.2.2 변경 요청 상태 조회
```http
GET /api/v1/integration/itsm/change-requests/{change_request_id}
```

### 7.3 보안 시스템 연계

#### 7.3.1 DB 접근 제어 정책 동기화
```http
POST /api/v1/integration/security/db-access-policies
```

**Request:**
```json
{
  "table_id": "tbl001",
  "security_policies": {
    "classification": "CONFIDENTIAL",
    "access_level": "RESTRICTED",
    "encryption_required": true,
    "masking_rules": [
      {
        "column_name": "customer_name",
        "masking_type": "PARTIAL",
        "masking_pattern": "**#{LAST_2_CHARS}"
      }
    ],
    "access_groups": ["CUSTOMER_MGMT_TEAM", "DATA_ADMIN"],
    "audit_level": "FULL"
  }
}
```

#### 7.3.2 개인정보 인벤토리 동기화
```http
POST /api/v1/integration/security/personal-info-inventory
```

### 7.4 테스트 데이터 관리 시스템 연계

#### 7.4.1 마스킹 대상 정보 제공
```http
GET /api/v1/integration/test-data/masking-targets
```

**Response:**
```json
{
  "success": true,
  "data": {
    "masking_targets": [
      {
        "table_id": "tbl001",
        "table_name": "customer",
        "columns": [
          {
            "column_name": "customer_name",
            "personal_info_type": "NAME",
            "masking_rule": "FULL_MASK",
            "sample_original": "홍길동",
            "sample_masked": "***"
          },
          {
            "column_name": "phone_number",
            "personal_info_type": "PHONE",
            "masking_rule": "PARTIAL_MASK",
            "sample_original": "010-1234-5678",
            "sample_masked": "010-****-5678"
          }
        ]
      }
    ]
  }
}
```

---

## ⚙️ 8. 시스템 관리 API

### 8.1 사용자 관리

#### 8.1.1 사용자 목록 조회
```http
GET /api/v1/system/users
```

#### 8.1.2 사용자 권한 관리
```http
PUT /api/v1/system/users/{user_id}/roles
```

**Request:**
```json
{
  "roles": ["DATA_ANALYST", "METADATA_USER"],
  "effective_start_date": "2025-11-25",
  "effective_end_date": null,
  "assigned_by": "admin"
}
```

### 8.2 모니터링

#### 8.2.1 시스템 상태 조회
```http
GET /api/v1/system/health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "overall_status": "HEALTHY",
    "timestamp": "2025-11-25T10:30:00Z",
    "services": {
      "metadata_service": {
        "status": "UP",
        "response_time_ms": 45,
        "last_check": "2025-11-25T10:29:30Z"
      },
      "ai_service": {
        "status": "UP",
        "response_time_ms": 1250,
        "last_check": "2025-11-25T10:29:30Z"
      },
      "database": {
        "status": "UP",
        "connection_pool": {
          "active": 8,
          "idle": 12,
          "max": 20
        }
      }
    },
    "resources": {
      "cpu_usage_percent": 45.2,
      "memory_usage_percent": 67.8,
      "disk_usage_percent": 34.1
    }
  }
}
```

#### 8.2.2 사용량 통계
```http
GET /api/v1/system/usage-statistics
```

**Query Parameters:**
- `period` (string): 통계 기간 (daily, weekly, monthly)
- `start_date` (date): 시작 날짜
- `end_date` (date): 종료 날짜

**Response:**
```json
{
  "success": true,
  "data": {
    "period": "daily",
    "date_range": {
      "start": "2025-11-18",
      "end": "2025-11-25"
    },
    "daily_stats": [
      {
        "date": "2025-11-25",
        "unique_users": 127,
        "total_requests": 2345,
        "api_calls_by_service": {
          "metadata": 1456,
          "standards": 234,
          "ai": 178,
          "dataflow": 345,
          "modeling": 132
        },
        "avg_response_time_ms": 245,
        "error_rate_percent": 0.8
      }
    ]
  }
}
```

### 8.3 로그 관리

#### 8.3.1 감사 로그 조회
```http
GET /api/v1/system/audit-logs
```

**Query Parameters:**
- `user_id` (string): 사용자 필터
- `action_type` (string): 액션 타입 필터
- `resource_type` (string): 리소스 타입 필터
- `start_datetime` (datetime): 시작 시간
- `end_datetime` (datetime): 종료 시간
- `page`, `size`: 페이지네이션

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "log_id": "log001",
      "user_id": "user123",
      "username": "홍길동",
      "action_type": "UPDATE",
      "resource_type": "TABLE",
      "resource_id": "tbl001",
      "resource_name": "customer",
      "description": "테이블 메타정보 수정",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "request_details": {
        "changed_fields": ["table_comment", "data_classification"],
        "old_values": {"table_comment": "고객정보"},
        "new_values": {"table_comment": "고객 기본정보"}
      },
      "timestamp": "2025-11-25T10:25:00Z"
    }
  ]
}
```

#### 8.3.2 시스템 로그 조회
```http
GET /api/v1/system/system-logs
```

---

## 📊 9. 대시보드 및 리포트 API

### 9.1 대시보드 데이터

#### 9.1.1 통합 현황판 데이터
```http
GET /api/v1/dashboard/overview
```

**Response:**
```json
{
  "success": true,
  "data": {
    "metadata_stats": {
      "total_databases": 9,
      "total_tables": 1456,
      "total_columns": 23890,
      "sync_status": {
        "synced": 8,
        "pending": 1,
        "error": 0
      }
    },
    "standards_stats": {
      "compliance_rate": 90.1,
      "approved_words": 1234,
      "pending_approvals": 23,
      "total_domains": 456
    },
    "dataflow_stats": {
      "analyzed_programs": 234,
      "total_flows": 1567,
      "analysis_coverage": 87.5
    },
    "ai_stats": {
      "daily_queries": 178,
      "success_rate": 94.2,
      "avg_response_time": 2.3,
      "active_users": 45
    },
    "recent_activities": [
      {
        "type": "MODEL_APPROVAL",
        "description": "고객관리 모델 v1.2 승인 완료",
        "timestamp": "2025-11-25T10:15:00Z",
        "user": "data_admin"
      }
    ]
  }
}
```

#### 9.1.2 알림 센터 데이터
```http
GET /api/v1/dashboard/notifications
```

### 9.2 리포트 생성

#### 9.2.1 표준 준수율 리포트
```http
GET /api/v1/reports/standards-compliance
```

**Query Parameters:**
- `format` (string): 출력 형식 (json, pdf, excel)
- `db_id` (string): 데이터베이스 필터
- `date_range` (string): 기간 (30d, 90d, 1y)

#### 9.2.2 데이터 흐름 리포트
```http
GET /api/v1/reports/dataflow-analysis
```

#### 9.2.3 사용량 리포트
```http
GET /api/v1/reports/usage-statistics
```

---

## 🔄 10. Webhook 및 이벤트 API

### 10.1 Webhook 관리

#### 10.1.1 Webhook 등록
```http
POST /api/v1/webhooks
```

**Request:**
```json
{
  "webhook_name": "ITSM 연동 웹훅",
  "target_url": "https://itsm.kbanknow.com/api/metadata-changes",
  "events": ["MODEL_APPROVED", "SCHEMA_CHANGED", "COMPLIANCE_VIOLATION"],
  "authentication": {
    "type": "BEARER_TOKEN",
    "token": "webhook_secret_token"
  },
  "retry_policy": {
    "max_retries": 3,
    "retry_delay_seconds": 60
  }
}
```

### 10.2 실시간 이벤트 스트림

#### 10.2.1 WebSocket 연결
```
wss://api.kbanknow.com/metadata/v1/events/stream?token={jwt_token}
```

**이벤트 형식:**
```json
{
  "event_id": "evt001",
  "event_type": "TABLE_METADATA_UPDATED",
  "timestamp": "2025-11-25T10:30:00Z",
  "source_service": "metadata_service",
  "data": {
    "table_id": "tbl001",
    "table_name": "customer",
    "changes": ["table_comment", "data_classification"],
    "changed_by": "user123"
  }
}
```

---

## 📋 부록

### A. 에러 코드 정의

```json
{
  "error_codes": {
    "VALIDATION_ERROR": {
      "code": "VAL001",
      "message": "입력 값 검증 실패",
      "http_status": 400
    },
    "UNAUTHORIZED": {
      "code": "AUTH001", 
      "message": "인증 실패",
      "http_status": 401
    },
    "FORBIDDEN": {
      "code": "AUTH002",
      "message": "접근 권한 없음", 
      "http_status": 403
    },
    "RESOURCE_NOT_FOUND": {
      "code": "RES001",
      "message": "요청한 리소스를 찾을 수 없음",
      "http_status": 404
    },
    "DATABASE_CONNECTION_ERROR": {
      "code": "DB001",
      "message": "데이터베이스 연결 실패",
      "http_status": 503
    },
    "AI_SERVICE_ERROR": {
      "code": "AI001",
      "message": "AI 서비스 오류",
      "http_status": 503
    }
  }
}
```

### B. Rate Limiting

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

**제한 정책:**
- 일반 API: 1000 requests/hour/user
- AI API: 100 requests/hour/user
- 검색 API: 500 requests/hour/user

### C. API 버전 관리

```http
# 헤더 방식 (권장)
Accept: application/vnd.kbank.metadata.v1+json

# URL 방식
GET /api/v1/metadata/tables
GET /api/v2/metadata/tables

# 쿼리 파라미터 방식
GET /api/metadata/tables?version=1
```

---

## 🎯 구현 우선순위

### Phase 1 (Month 1-2): 핵심 API
1. **인증/인가 API** - JWT, 권한 관리
2. **메타데이터 관리 API** - DB, 테이블, 컬럼 CRUD
3. **기본 검색 API** - 통합 검색, 통계
4. **시스템 관리 API** - 사용자, 모니터링

### Phase 2 (Month 2-3): 표준 관리 API  
1. **데이터 표준 API** - 단어, 용어, 도메인, 코드
2. **모델링 API** - GraphQL, 기본 CRUD
3. **승인 워크플로우 API**

### Phase 3 (Month 3-4): 분석 API
1. **데이터 흐름 API** - 프로그램 분석, 흐름 추적
2. **영향도 분석 API** - 영향도, CRUD 매트릭스
3. **시각화 API** - 그래프 데이터

### Phase 4 (Month 4-5): AI API
1. **자연어 질의 API** - Text2SQL
2. **추천 API** - 모델링, 표준 추천
3. **지식베이스 API** - 임베딩, 검색

### Phase 5 (Month 5-6): 연계 API
1. **외부 시스템 연계 API**
2. **Webhook 및 이벤트 API**
3. **리포트 API**

---

**문서 승인**

| 역할 | 이름 | 승인일 | 서명 |
|------|------|--------|------|
| API 설계자 | [ ] | 2025-11-25 | [ ] |
| 백엔드 리더 | [ ] | | [ ] |
| 프론트엔드 리더 | [ ] | | [ ] |
| 프로젝트 매니저 | [ ] | | [ ] |

**다음 검토 예정일**: 2025-12-02  
**API 문서 URL**: https://api-docs.kbanknow.com/metadata/v1