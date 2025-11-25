# K-BANK 메타데이터 AI 플랫폼 데이터베이스 설계서

**버전:** 1.0  
**작성일:** 2025-11-25  
**DBMS:** EDB (EnterpriseDB) + Redis + Elasticsearch + Vector DB  
**기반:** RFP 요구사항, 아키텍처 설계서

---

## 📋 설계 개요

### 설계 목적
- 메타데이터, 데이터 표준, 모델링, 흐름 분석 등 전 영역의 데이터 구조 정의
- 9개 DBMS 환경 지원을 위한 유연한 스키마 설계
- 1,200명 동시 사용자 지원을 위한 성능 최적화 구조
- K-BANK 보안 및 컴플라이언스 요구사항 반영

### 설계 원칙
1. **확장성**: 향후 기능 추가를 고려한 유연한 구조
2. **성능**: 대용량 메타데이터 처리를 위한 최적화
3. **무결성**: 참조 무결성 및 비즈니스 규칙 보장
4. **추적성**: 모든 변경 이력 및 감사 로그 유지
5. **보안**: 개인정보 및 중요 데이터 암호화

---

## 🗄️ 전체 데이터베이스 구조

### 스키마 분리 전략
```sql
-- 도메인별 스키마 분리
CREATE SCHEMA metadata;      -- 메타데이터 관리
CREATE SCHEMA standards;     -- 데이터 표준 관리
CREATE SCHEMA modeling;      -- 데이터 모델링
CREATE SCHEMA dataflow;      -- 데이터 흐름 관리
CREATE SCHEMA ai_service;    -- AI 서비스
CREATE SCHEMA integration;   -- 외부 시스템 연계
CREATE SCHEMA system_mgmt;   -- 시스템 관리
CREATE SCHEMA audit;         -- 감사 및 로그
```

### 테이블 명명 규칙
```
패턴: {domain_prefix}_{entity_name}

예시:
- metadata.md_database_info      (메타데이터 - 데이터베이스 정보)
- standards.std_word_master      (표준 - 단어 마스터)
- modeling.mdl_entity_info       (모델링 - 엔터티 정보)
- dataflow.df_flow_analysis      (흐름 - 흐름 분석)
- ai_service.ai_query_history    (AI - 질의 이력)
```

---

## 📊 스키마별 상세 설계

### 1. METADATA 스키마 (메타데이터 관리)

#### 1.1 데이터베이스 연결 정보
```sql
-- 데이터베이스 연결 정보
CREATE TABLE metadata.md_database_info (
    db_id                   VARCHAR(50) PRIMARY KEY,
    db_name                 VARCHAR(100) NOT NULL,
    db_type                 VARCHAR(20) NOT NULL CHECK (db_type IN ('ORACLE', 'MYSQL', 'MARIADB', 'SINGLESTORE', 'POSTGRESQL', 'EDB', 'AURORA', 'REDSHIFT', 'S3')),
    host_name               VARCHAR(255) NOT NULL,
    port_number             INTEGER NOT NULL,
    database_name           VARCHAR(100) NOT NULL,
    connection_url          VARCHAR(500) NOT NULL,
    username                VARCHAR(100) NOT NULL,
    password_encrypted      TEXT NOT NULL,  -- AES-256 암호화
    schema_list             TEXT,           -- JSON 형태로 스키마 목록 저장
    connection_status       VARCHAR(20) DEFAULT 'ACTIVE' CHECK (connection_status IN ('ACTIVE', 'INACTIVE', 'ERROR')),
    last_sync_datetime      TIMESTAMP,
    sync_status             VARCHAR(20) DEFAULT 'PENDING' CHECK (sync_status IN ('PENDING', 'IN_PROGRESS', 'SUCCESS', 'FAILED')),
    sync_error_message      TEXT,
    created_by              VARCHAR(50) NOT NULL,
    created_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by             VARCHAR(50),
    modified_datetime       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted              BOOLEAN DEFAULT FALSE,
    deleted_by              VARCHAR(50),
    deleted_datetime        TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX idx_md_database_info_type ON metadata.md_database_info(db_type);
CREATE INDEX idx_md_database_info_status ON metadata.md_database_info(connection_status);
CREATE INDEX idx_md_database_info_sync ON metadata.md_database_info(last_sync_datetime);

COMMENT ON TABLE metadata.md_database_info IS '데이터베이스 연결 정보 관리';
```

#### 1.2 테이블 메타정보
```sql
-- 테이블 메타정보
CREATE TABLE metadata.md_table_info (
    table_id                VARCHAR(50) PRIMARY KEY,
    db_id                   VARCHAR(50) NOT NULL,
    schema_name             VARCHAR(100) NOT NULL,
    table_name              VARCHAR(100) NOT NULL,
    table_type              VARCHAR(20) CHECK (table_type IN ('TABLE', 'VIEW', 'MATERIALIZED_VIEW', 'PARTITION')),
    table_comment           TEXT,
    business_description    TEXT,
    owner_team              VARCHAR(100),
    data_classification     VARCHAR(20) CHECK (data_classification IN ('PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED')),
    contains_personal_info  BOOLEAN DEFAULT FALSE,
    contains_sensitive_info BOOLEAN DEFAULT FALSE,
    record_count            BIGINT,
    data_size_mb            NUMERIC(15,2),
    created_date            DATE,
    last_modified_date      DATE,
    partition_type          VARCHAR(20) CHECK (partition_type IN ('NONE', 'RANGE', 'LIST', 'HASH')),
    partition_key           VARCHAR(200),
    retention_period_days   INTEGER,
    archival_policy         VARCHAR(100),
    backup_required         BOOLEAN DEFAULT TRUE,
    sync_datetime           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by              VARCHAR(50) NOT NULL,
    created_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by             VARCHAR(50),
    modified_datetime       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted              BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_md_table_db FOREIGN KEY (db_id) REFERENCES metadata.md_database_info(db_id),
    CONSTRAINT uk_md_table_unique UNIQUE (db_id, schema_name, table_name)
);

-- 인덱스 생성
CREATE INDEX idx_md_table_info_db ON metadata.md_table_info(db_id);
CREATE INDEX idx_md_table_info_schema ON metadata.md_table_info(schema_name);
CREATE INDEX idx_md_table_info_name ON metadata.md_table_info(table_name);
CREATE INDEX idx_md_table_info_classification ON metadata.md_table_info(data_classification);
CREATE INDEX idx_md_table_info_personal ON metadata.md_table_info(contains_personal_info);

COMMENT ON TABLE metadata.md_table_info IS '테이블 메타정보';
```

#### 1.3 컬럼 메타정보
```sql
-- 컬럼 메타정보
CREATE TABLE metadata.md_column_info (
    column_id               VARCHAR(50) PRIMARY KEY,
    table_id                VARCHAR(50) NOT NULL,
    column_name             VARCHAR(100) NOT NULL,
    data_type               VARCHAR(50) NOT NULL,
    max_length              INTEGER,
    numeric_precision       INTEGER,
    numeric_scale           INTEGER,
    is_nullable             BOOLEAN DEFAULT TRUE,
    is_primary_key          BOOLEAN DEFAULT FALSE,
    is_foreign_key          BOOLEAN DEFAULT FALSE,
    is_unique               BOOLEAN DEFAULT FALSE,
    default_value           TEXT,
    column_comment          TEXT,
    business_description    TEXT,
    data_format             VARCHAR(100),
    valid_values            TEXT,  -- JSON 형태의 허용값 목록
    is_encrypted            BOOLEAN DEFAULT FALSE,
    encryption_algorithm    VARCHAR(50),
    masking_rule            VARCHAR(100),
    column_order            INTEGER NOT NULL,
    is_personal_info        BOOLEAN DEFAULT FALSE,
    personal_info_type      VARCHAR(50) CHECK (personal_info_type IN ('NAME', 'PHONE', 'EMAIL', 'ADDRESS', 'SSN', 'CARD_NO')),
    sync_datetime           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by              VARCHAR(50) NOT NULL,
    created_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by             VARCHAR(50),
    modified_datetime       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted              BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_md_column_table FOREIGN KEY (table_id) REFERENCES metadata.md_table_info(table_id),
    CONSTRAINT uk_md_column_unique UNIQUE (table_id, column_name)
);

-- 인덱스 생성
CREATE INDEX idx_md_column_info_table ON metadata.md_column_info(table_id);
CREATE INDEX idx_md_column_info_name ON metadata.md_column_info(column_name);
CREATE INDEX idx_md_column_info_type ON metadata.md_column_info(data_type);
CREATE INDEX idx_md_column_info_personal ON metadata.md_column_info(is_personal_info);

COMMENT ON TABLE metadata.md_column_info IS '컬럼 메타정보';
```

#### 1.4 인덱스 정보
```sql
-- 인덱스 정보
CREATE TABLE metadata.md_index_info (
    index_id                VARCHAR(50) PRIMARY KEY,
    table_id                VARCHAR(50) NOT NULL,
    index_name              VARCHAR(100) NOT NULL,
    index_type              VARCHAR(20) CHECK (index_type IN ('UNIQUE', 'PRIMARY', 'NORMAL', 'BITMAP', 'FUNCTIONAL')),
    column_list             TEXT NOT NULL,  -- JSON 형태의 컬럼 목록
    is_unique               BOOLEAN DEFAULT FALSE,
    storage_size_mb         NUMERIC(15,2),
    created_date            DATE,
    sync_datetime           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_md_index_table FOREIGN KEY (table_id) REFERENCES metadata.md_table_info(table_id)
);

COMMENT ON TABLE metadata.md_index_info IS '인덱스 정보';
```

---

### 2. STANDARDS 스키마 (데이터 표준 관리)

#### 2.1 단어 마스터
```sql
-- 표준 단어 마스터
CREATE TABLE standards.std_word_master (
    word_id                 VARCHAR(50) PRIMARY KEY,
    word_name               VARCHAR(100) NOT NULL,
    word_english_name       VARCHAR(100),
    word_abbreviation       VARCHAR(20),
    word_definition         TEXT NOT NULL,
    usage_example           TEXT,
    business_domain         VARCHAR(100),
    synonym_list            TEXT,  -- JSON 형태
    antonym_list            TEXT,  -- JSON 형태
    forbidden_words         TEXT,  -- JSON 형태
    approval_status         VARCHAR(20) DEFAULT 'DRAFT' CHECK (approval_status IN ('DRAFT', 'PENDING', 'APPROVED', 'REJECTED')),
    approval_comment        TEXT,
    approved_by             VARCHAR(50),
    approved_datetime       TIMESTAMP,
    created_by              VARCHAR(50) NOT NULL,
    created_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by             VARCHAR(50),
    modified_datetime       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted              BOOLEAN DEFAULT FALSE,
    CONSTRAINT uk_std_word_name UNIQUE (word_name)
);

-- 인덱스 생성
CREATE INDEX idx_std_word_name ON standards.std_word_master(word_name);
CREATE INDEX idx_std_word_status ON standards.std_word_master(approval_status);
CREATE INDEX idx_std_word_domain ON standards.std_word_master(business_domain);

COMMENT ON TABLE standards.std_word_master IS '표준 단어 마스터';
```

#### 2.2 용어 마스터
```sql
-- 표준 용어 마스터
CREATE TABLE standards.std_term_master (
    term_id                 VARCHAR(50) PRIMARY KEY,
    term_name               VARCHAR(200) NOT NULL,
    term_english_name       VARCHAR(200),
    term_abbreviation       VARCHAR(50),
    term_definition         TEXT NOT NULL,
    business_rule           TEXT,
    related_laws            TEXT,  -- 관련 법령
    usage_guideline         TEXT,
    word_composition        TEXT,  -- JSON 형태의 구성 단어 정보
    business_domain         VARCHAR(100),
    approval_status         VARCHAR(20) DEFAULT 'DRAFT' CHECK (approval_status IN ('DRAFT', 'PENDING', 'APPROVED', 'REJECTED')),
    approval_comment        TEXT,
    approved_by             VARCHAR(50),
    approved_datetime       TIMESTAMP,
    created_by              VARCHAR(50) NOT NULL,
    created_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by             VARCHAR(50),
    modified_datetime       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted              BOOLEAN DEFAULT FALSE,
    CONSTRAINT uk_std_term_name UNIQUE (term_name)
);

COMMENT ON TABLE standards.std_term_master IS '표준 용어 마스터';
```

#### 2.3 도메인 마스터
```sql
-- 표준 도메인 마스터
CREATE TABLE standards.std_domain_master (
    domain_id               VARCHAR(50) PRIMARY KEY,
    domain_name             VARCHAR(100) NOT NULL,
    domain_description      TEXT,
    logical_data_type       VARCHAR(50) NOT NULL,
    physical_data_type_oracle VARCHAR(50),
    physical_data_type_mysql VARCHAR(50),
    physical_data_type_postgresql VARCHAR(50),
    physical_data_type_edb  VARCHAR(50),
    max_length              INTEGER,
    min_length              INTEGER,
    decimal_places          INTEGER,
    default_value           TEXT,
    validation_rule         TEXT,  -- 정규식 또는 체크 조건
    format_pattern          VARCHAR(200),
    example_values          TEXT,  -- JSON 형태
    null_allowed            BOOLEAN DEFAULT TRUE,
    encryption_required     BOOLEAN DEFAULT FALSE,
    masking_required        BOOLEAN DEFAULT FALSE,
    approval_status         VARCHAR(20) DEFAULT 'DRAFT' CHECK (approval_status IN ('DRAFT', 'PENDING', 'APPROVED', 'REJECTED')),
    created_by              VARCHAR(50) NOT NULL,
    created_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by             VARCHAR(50),
    modified_datetime       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted              BOOLEAN DEFAULT FALSE,
    CONSTRAINT uk_std_domain_name UNIQUE (domain_name)
);

COMMENT ON TABLE standards.std_domain_master IS '표준 도메인 마스터';
```

#### 2.4 코드 마스터
```sql
-- 표준 코드 마스터 (상위 코드)
CREATE TABLE standards.std_code_master (
    code_id                 VARCHAR(50) PRIMARY KEY,
    code_group_id           VARCHAR(50),
    code_name               VARCHAR(100) NOT NULL,
    code_description        TEXT,
    code_type               VARCHAR(20) CHECK (code_type IN ('COMMON', 'BUSINESS', 'SYSTEM')),
    usage_scope             VARCHAR(100),  -- 사용 범위
    owner_organization      VARCHAR(100),  -- 관리 조직
    approval_status         VARCHAR(20) DEFAULT 'DRAFT' CHECK (approval_status IN ('DRAFT', 'PENDING', 'APPROVED', 'REJECTED')),
    created_by              VARCHAR(50) NOT NULL,
    created_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by             VARCHAR(50),
    modified_datetime       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted              BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_std_code_group FOREIGN KEY (code_group_id) REFERENCES standards.std_code_master(code_id)
);

-- 표준 코드 상세 (하위 코드값)
CREATE TABLE standards.std_code_detail (
    detail_id               VARCHAR(50) PRIMARY KEY,
    code_id                 VARCHAR(50) NOT NULL,
    code_value              VARCHAR(100) NOT NULL,
    code_name               VARCHAR(200) NOT NULL,
    code_description        TEXT,
    sort_order              INTEGER DEFAULT 0,
    parent_code_value       VARCHAR(100),  -- 계층형 코드용
    additional_attributes   TEXT,  -- JSON 형태의 추가 속성
    effective_start_date    DATE,
    effective_end_date      DATE,
    is_active               BOOLEAN DEFAULT TRUE,
    created_by              VARCHAR(50) NOT NULL,
    created_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by             VARCHAR(50),
    modified_datetime       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted              BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_std_code_detail_master FOREIGN KEY (code_id) REFERENCES standards.std_code_master(code_id),
    CONSTRAINT uk_std_code_detail UNIQUE (code_id, code_value)
);

COMMENT ON TABLE standards.std_code_master IS '표준 코드 마스터';
COMMENT ON TABLE standards.std_code_detail IS '표준 코드 상세';
```

#### 2.5 표준 준수율
```sql
-- 표준 준수율 통계
CREATE TABLE standards.std_compliance_stats (
    stats_id                VARCHAR(50) PRIMARY KEY,
    db_id                   VARCHAR(50) NOT NULL,
    schema_name             VARCHAR(100),
    table_id                VARCHAR(50),
    stats_date              DATE NOT NULL,
    total_columns           INTEGER DEFAULT 0,
    compliant_columns       INTEGER DEFAULT 0,
    non_compliant_columns   INTEGER DEFAULT 0,
    compliance_rate         NUMERIC(5,2) DEFAULT 0.00,
    word_compliance_rate    NUMERIC(5,2) DEFAULT 0.00,
    domain_compliance_rate  NUMERIC(5,2) DEFAULT 0.00,
    naming_compliance_rate  NUMERIC(5,2) DEFAULT 0.00,
    calculated_datetime     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_std_compliance_db FOREIGN KEY (db_id) REFERENCES metadata.md_database_info(db_id)
);

-- 파티션 테이블로 생성 (월별)
-- CREATE TABLE standards.std_compliance_stats_2025_01 PARTITION OF standards.std_compliance_stats
--     FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

COMMENT ON TABLE standards.std_compliance_stats IS '표준 준수율 통계';
```

---

### 3. MODELING 스키마 (데이터 모델링)

#### 3.1 모델 프로젝트
```sql
-- 모델링 프로젝트
CREATE TABLE modeling.mdl_project (
    project_id              VARCHAR(50) PRIMARY KEY,
    project_name            VARCHAR(200) NOT NULL,
    project_description     TEXT,
    business_domain         VARCHAR(100),
    project_type            VARCHAR(20) CHECK (project_type IN ('LOGICAL', 'PHYSICAL', 'CONCEPTUAL')),
    project_status          VARCHAR(20) DEFAULT 'ACTIVE' CHECK (project_status IN ('ACTIVE', 'INACTIVE', 'ARCHIVED')),
    owner_team              VARCHAR(100),
    modeling_tool_type      VARCHAR(50),  -- ERWin, DA#, PowerDesigner 등
    created_by              VARCHAR(50) NOT NULL,
    created_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by             VARCHAR(50),
    modified_datetime       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted              BOOLEAN DEFAULT FALSE
);

COMMENT ON TABLE modeling.mdl_project IS '모델링 프로젝트';
```

#### 3.2 엔터티 정보
```sql
-- 엔터티 정보
CREATE TABLE modeling.mdl_entity_info (
    entity_id               VARCHAR(50) PRIMARY KEY,
    project_id              VARCHAR(50) NOT NULL,
    entity_name             VARCHAR(100) NOT NULL,
    entity_logical_name     VARCHAR(200) NOT NULL,
    entity_description      TEXT,
    entity_type             VARCHAR(20) CHECK (entity_type IN ('MASTER', 'TRANSACTION', 'CODE', 'HISTORY', 'LOG')),
    subject_area            VARCHAR(100),
    business_rules          TEXT,
    data_volume_estimate    BIGINT,
    access_frequency        VARCHAR(20) CHECK (access_frequency IN ('HIGH', 'MEDIUM', 'LOW')),
    retention_period        INTEGER,  -- 보관 기간 (일)
    position_x              INTEGER,  -- ERD 상의 X 좌표
    position_y              INTEGER,  -- ERD 상의 Y 좌표
    width                   INTEGER,  -- ERD 상의 너비
    height                  INTEGER,  -- ERD 상의 높이
    color_code              VARCHAR(10),  -- 엔터티 색상
    created_by              VARCHAR(50) NOT NULL,
    created_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by             VARCHAR(50),
    modified_datetime       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted              BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_mdl_entity_project FOREIGN KEY (project_id) REFERENCES modeling.mdl_project(project_id),
    CONSTRAINT uk_mdl_entity UNIQUE (project_id, entity_name)
);

COMMENT ON TABLE modeling.mdl_entity_info IS '엔터티 정보';
```

#### 3.3 속성 정보
```sql
-- 속성 정보
CREATE TABLE modeling.mdl_attribute_info (
    attribute_id            VARCHAR(50) PRIMARY KEY,
    entity_id               VARCHAR(50) NOT NULL,
    attribute_name          VARCHAR(100) NOT NULL,
    attribute_logical_name  VARCHAR(200) NOT NULL,
    attribute_description   TEXT,
    domain_id               VARCHAR(50),
    data_type               VARCHAR(50) NOT NULL,
    max_length              INTEGER,
    decimal_places          INTEGER,
    is_primary_key          BOOLEAN DEFAULT FALSE,
    is_foreign_key          BOOLEAN DEFAULT FALSE,
    is_not_null             BOOLEAN DEFAULT FALSE,
    is_unique               BOOLEAN DEFAULT FALSE,
    default_value           TEXT,
    validation_rule         TEXT,
    attribute_order         INTEGER NOT NULL,
    business_rules          TEXT,
    sample_data             TEXT,
    created_by              VARCHAR(50) NOT NULL,
    created_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by             VARCHAR(50),
    modified_datetime       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted              BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_mdl_attribute_entity FOREIGN KEY (entity_id) REFERENCES modeling.mdl_entity_info(entity_id),
    CONSTRAINT fk_mdl_attribute_domain FOREIGN KEY (domain_id) REFERENCES standards.std_domain_master(domain_id),
    CONSTRAINT uk_mdl_attribute UNIQUE (entity_id, attribute_name)
);

COMMENT ON TABLE modeling.mdl_attribute_info IS '속성 정보';
```

#### 3.4 관계 정보
```sql
-- 관계 정보
CREATE TABLE modeling.mdl_relationship_info (
    relationship_id         VARCHAR(50) PRIMARY KEY,
    project_id              VARCHAR(50) NOT NULL,
    relationship_name       VARCHAR(100) NOT NULL,
    parent_entity_id        VARCHAR(50) NOT NULL,
    child_entity_id         VARCHAR(50) NOT NULL,
    relationship_type       VARCHAR(20) CHECK (relationship_type IN ('IDENTIFYING', 'NON_IDENTIFYING', 'SUPER_SUB')),
    cardinality             VARCHAR(20) CHECK (cardinality IN ('1:1', '1:M', 'M:N')),
    optionality             VARCHAR(20) CHECK (optionality IN ('MANDATORY', 'OPTIONAL')),
    relationship_description TEXT,
    foreign_key_attributes  TEXT,  -- JSON 형태의 FK 속성 매핑
    created_by              VARCHAR(50) NOT NULL,
    created_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by             VARCHAR(50),
    modified_datetime       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted              BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_mdl_rel_project FOREIGN KEY (project_id) REFERENCES modeling.mdl_project(project_id),
    CONSTRAINT fk_mdl_rel_parent FOREIGN KEY (parent_entity_id) REFERENCES modeling.mdl_entity_info(entity_id),
    CONSTRAINT fk_mdl_rel_child FOREIGN KEY (child_entity_id) REFERENCES modeling.mdl_entity_info(entity_id)
);

COMMENT ON TABLE modeling.mdl_relationship_info IS '관계 정보';
```

#### 3.5 모델 버전 관리
```sql
-- 모델 버전 관리
CREATE TABLE modeling.mdl_version_history (
    version_id              VARCHAR(50) PRIMARY KEY,
    project_id              VARCHAR(50) NOT NULL,
    version_number          VARCHAR(20) NOT NULL,
    version_description     TEXT,
    change_summary          TEXT,
    version_status          VARCHAR(20) CHECK (version_status IN ('DRAFT', 'REVIEW', 'APPROVED', 'DEPLOYED')),
    baseline_version        BOOLEAN DEFAULT FALSE,
    model_data_snapshot     TEXT,  -- JSON 형태의 전체 모델 스냅샷
    created_by              VARCHAR(50) NOT NULL,
    created_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by             VARCHAR(50),
    approved_datetime       TIMESTAMP,
    deployed_by             VARCHAR(50),
    deployed_datetime       TIMESTAMP,
    CONSTRAINT fk_mdl_version_project FOREIGN KEY (project_id) REFERENCES modeling.mdl_project(project_id),
    CONSTRAINT uk_mdl_version UNIQUE (project_id, version_number)
);

COMMENT ON TABLE modeling.mdl_version_history IS '모델 버전 관리';
```

---

### 4. DATAFLOW 스키마 (데이터 흐름 관리)

#### 4.1 프로그램 정보
```sql
-- 프로그램 정보
CREATE TABLE dataflow.df_program_info (
    program_id              VARCHAR(50) PRIMARY KEY,
    program_name            VARCHAR(200) NOT NULL,
    program_type            VARCHAR(20) CHECK (program_type IN ('BATCH', 'API', 'ETL', 'PROCEDURE', 'FUNCTION', 'TRIGGER')),
    programming_language    VARCHAR(20) CHECK (programming_language IN ('JAVA', 'PYTHON', 'NODEJS', 'SQL', 'SHELL', 'OTHER')),
    file_path               TEXT,
    program_description     TEXT,
    business_purpose        TEXT,
    execution_schedule      VARCHAR(100),  -- cron expression
    owner_team              VARCHAR(100),
    last_analysis_datetime  TIMESTAMP,
    analysis_status         VARCHAR(20) DEFAULT 'PENDING' CHECK (analysis_status IN ('PENDING', 'IN_PROGRESS', 'SUCCESS', 'FAILED')),
    analysis_error_message  TEXT,
    created_by              VARCHAR(50) NOT NULL,
    created_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by             VARCHAR(50),
    modified_datetime       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted              BOOLEAN DEFAULT FALSE
);

-- 인덱스 생성
CREATE INDEX idx_df_program_type ON dataflow.df_program_info(program_type);
CREATE INDEX idx_df_program_language ON dataflow.df_program_info(programming_language);

COMMENT ON TABLE dataflow.df_program_info IS '프로그램 정보';
```

#### 4.2 데이터 흐름 분석 결과
```sql
-- 데이터 흐름 분석 결과
CREATE TABLE dataflow.df_flow_analysis (
    flow_id                 VARCHAR(50) PRIMARY KEY,
    program_id              VARCHAR(50) NOT NULL,
    source_table_id         VARCHAR(50),
    target_table_id         VARCHAR(50),
    flow_type               VARCHAR(20) CHECK (flow_type IN ('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'MERGE')),
    flow_description        TEXT,
    sql_statement           TEXT,
    column_mappings         TEXT,  -- JSON 형태의 컬럼 매핑 정보
    transformation_logic    TEXT,
    execution_frequency     VARCHAR(50),
    data_volume_estimate    BIGINT,
    performance_impact      VARCHAR(20) CHECK (performance_impact IN ('HIGH', 'MEDIUM', 'LOW')),
    analysis_datetime       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_df_flow_program FOREIGN KEY (program_id) REFERENCES dataflow.df_program_info(program_id),
    CONSTRAINT fk_df_flow_source FOREIGN KEY (source_table_id) REFERENCES metadata.md_table_info(table_id),
    CONSTRAINT fk_df_flow_target FOREIGN KEY (target_table_id) REFERENCES metadata.md_table_info(table_id)
);

-- 인덱스 생성
CREATE INDEX idx_df_flow_program ON dataflow.df_flow_analysis(program_id);
CREATE INDEX idx_df_flow_source ON dataflow.df_flow_analysis(source_table_id);
CREATE INDEX idx_df_flow_target ON dataflow.df_flow_analysis(target_table_id);
CREATE INDEX idx_df_flow_type ON dataflow.df_flow_analysis(flow_type);

COMMENT ON TABLE dataflow.df_flow_analysis IS '데이터 흐름 분석 결과';
```

#### 4.3 영향도 분석
```sql
-- 영향도 분석 결과
CREATE TABLE dataflow.df_impact_analysis (
    impact_id               VARCHAR(50) PRIMARY KEY,
    source_entity_type      VARCHAR(20) CHECK (source_entity_type IN ('TABLE', 'COLUMN', 'PROGRAM')),
    source_entity_id        VARCHAR(50) NOT NULL,
    impact_entity_type      VARCHAR(20) CHECK (impact_entity_type IN ('TABLE', 'COLUMN', 'PROGRAM')),
    impact_entity_id        VARCHAR(50) NOT NULL,
    impact_level            VARCHAR(20) CHECK (impact_level IN ('DIRECT', 'INDIRECT')),
    impact_distance         INTEGER DEFAULT 1,  -- 영향도 거리 (단계)
    impact_score            NUMERIC(3,2) DEFAULT 0.00,  -- 영향도 점수 (0.00 ~ 1.00)
    risk_level              VARCHAR(20) CHECK (risk_level IN ('HIGH', 'MEDIUM', 'LOW')),
    analysis_datetime       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_df_impact UNIQUE (source_entity_type, source_entity_id, impact_entity_type, impact_entity_id)
);

-- 인덱스 생성
CREATE INDEX idx_df_impact_source ON dataflow.df_impact_analysis(source_entity_type, source_entity_id);
CREATE INDEX idx_df_impact_target ON dataflow.df_impact_analysis(impact_entity_type, impact_entity_id);
CREATE INDEX idx_df_impact_level ON dataflow.df_impact_analysis(impact_level);

COMMENT ON TABLE dataflow.df_impact_analysis IS '영향도 분석 결과';
```

#### 4.4 CRUD 매트릭스
```sql
-- CRUD 매트릭스
CREATE TABLE dataflow.df_crud_matrix (
    crud_id                 VARCHAR(50) PRIMARY KEY,
    program_id              VARCHAR(50) NOT NULL,
    table_id                VARCHAR(50) NOT NULL,
    column_id               VARCHAR(50),
    create_flag             BOOLEAN DEFAULT FALSE,  -- C
    read_flag               BOOLEAN DEFAULT FALSE,  -- R
    update_flag             BOOLEAN DEFAULT FALSE,  -- U
    delete_flag             BOOLEAN DEFAULT FALSE,  -- D
    access_frequency        VARCHAR(20) CHECK (access_frequency IN ('HIGH', 'MEDIUM', 'LOW')),
    last_access_datetime    TIMESTAMP,
    analysis_datetime       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_df_crud_program FOREIGN KEY (program_id) REFERENCES dataflow.df_program_info(program_id),
    CONSTRAINT fk_df_crud_table FOREIGN KEY (table_id) REFERENCES metadata.md_table_info(table_id),
    CONSTRAINT fk_df_crud_column FOREIGN KEY (column_id) REFERENCES metadata.md_column_info(column_id),
    CONSTRAINT uk_df_crud UNIQUE (program_id, table_id, column_id)
);

-- 인덱스 생성
CREATE INDEX idx_df_crud_program ON dataflow.df_crud_matrix(program_id);
CREATE INDEX idx_df_crud_table ON dataflow.df_crud_matrix(table_id);

COMMENT ON TABLE dataflow.df_crud_matrix IS 'CRUD 매트릭스';
```

---

### 5. AI_SERVICE 스키마 (AI 서비스)

#### 5.1 AI 질의 이력
```sql
-- AI 질의 이력
CREATE TABLE ai_service.ai_query_history (
    query_id                VARCHAR(50) PRIMARY KEY,
    user_id                 VARCHAR(50) NOT NULL,
    session_id              VARCHAR(100),
    query_text              TEXT NOT NULL,
    query_type              VARCHAR(20) CHECK (query_type IN ('TEXT2SQL', 'METADATA_SEARCH', 'RECOMMENDATION', 'GENERAL')),
    context_data            TEXT,  -- JSON 형태의 컨텍스트 정보
    llm_model               VARCHAR(50),
    response_text           TEXT,
    generated_sql           TEXT,
    confidence_score        NUMERIC(3,2),
    execution_result        TEXT,  -- SQL 실행 결과 (성공/실패)
    response_time_ms        INTEGER,
    feedback_score          INTEGER CHECK (feedback_score BETWEEN 1 AND 5),
    feedback_comment        TEXT,
    query_datetime          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted              BOOLEAN DEFAULT FALSE
);

-- 인덱스 생성
CREATE INDEX idx_ai_query_user ON ai_service.ai_query_history(user_id);
CREATE INDEX idx_ai_query_type ON ai_service.ai_query_history(query_type);
CREATE INDEX idx_ai_query_datetime ON ai_service.ai_query_history(query_datetime);
CREATE INDEX idx_ai_query_model ON ai_service.ai_query_history(llm_model);

-- 파티션 테이블로 생성 (월별)
-- CREATE TABLE ai_service.ai_query_history_2025_01 PARTITION OF ai_service.ai_query_history
--     FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

COMMENT ON TABLE ai_service.ai_query_history IS 'AI 질의 이력';
```

#### 5.2 임베딩 관리
```sql
-- 임베딩 관리 (벡터 DB 메타데이터)
CREATE TABLE ai_service.ai_embedding_metadata (
    embedding_id            VARCHAR(50) PRIMARY KEY,
    content_type            VARCHAR(50) CHECK (content_type IN ('TABLE_SCHEMA', 'COLUMN_DESC', 'BUSINESS_RULE', 'SQL_PATTERN')),
    content_id              VARCHAR(50) NOT NULL,  -- 원본 데이터 ID
    content_text            TEXT NOT NULL,
    embedding_model         VARCHAR(50) NOT NULL,
    vector_dimension        INTEGER NOT NULL,
    collection_name         VARCHAR(100) NOT NULL,
    vector_id               VARCHAR(100) NOT NULL,  -- 벡터DB 내 ID
    similarity_threshold    NUMERIC(3,2) DEFAULT 0.70,
    created_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_datetime      TIMESTAMP,
    usage_count             INTEGER DEFAULT 0
);

-- 인덱스 생성
CREATE INDEX idx_ai_embedding_type ON ai_service.ai_embedding_metadata(content_type);
CREATE INDEX idx_ai_embedding_content ON ai_service.ai_embedding_metadata(content_id);
CREATE INDEX idx_ai_embedding_collection ON ai_service.ai_embedding_metadata(collection_name);

COMMENT ON TABLE ai_service.ai_embedding_metadata IS '임베딩 메타데이터';
```

#### 5.3 추천 이력
```sql
-- AI 추천 이력
CREATE TABLE ai_service.ai_recommendation_history (
    recommendation_id       VARCHAR(50) PRIMARY KEY,
    user_id                 VARCHAR(50) NOT NULL,
    recommendation_type     VARCHAR(50) CHECK (recommendation_type IN ('WORD_SUGGESTION', 'DOMAIN_SUGGESTION', 'MODEL_PATTERN', 'SQL_OPTIMIZATION')),
    context_data            TEXT,  -- JSON 형태의 컨텍스트
    recommendation_list     TEXT,  -- JSON 형태의 추천 목록
    selected_recommendation TEXT,  -- 사용자가 선택한 추천
    confidence_scores       TEXT,  -- JSON 형태의 신뢰도 점수 목록
    acceptance_rate         NUMERIC(3,2),
    created_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE ai_service.ai_recommendation_history IS 'AI 추천 이력';
```

---

### 6. SYSTEM_MGMT 스키마 (시스템 관리)

#### 6.1 사용자 정보
```sql
-- 사용자 정보
CREATE TABLE system_mgmt.sys_user_info (
    user_id                 VARCHAR(50) PRIMARY KEY,
    username                VARCHAR(100) NOT NULL,
    email                   VARCHAR(255) NOT NULL,
    full_name               VARCHAR(100) NOT NULL,
    department              VARCHAR(100),
    position                VARCHAR(50),
    phone_number            VARCHAR(20),
    employee_id             VARCHAR(50),
    user_status             VARCHAR(20) DEFAULT 'ACTIVE' CHECK (user_status IN ('ACTIVE', 'INACTIVE', 'LOCKED', 'EXPIRED')),
    last_login_datetime     TIMESTAMP,
    login_attempt_count     INTEGER DEFAULT 0,
    password_changed_datetime TIMESTAMP,
    account_expired_date    DATE,
    created_by              VARCHAR(50) NOT NULL,
    created_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by             VARCHAR(50),
    modified_datetime       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted              BOOLEAN DEFAULT FALSE,
    CONSTRAINT uk_sys_user_username UNIQUE (username),
    CONSTRAINT uk_sys_user_email UNIQUE (email)
);

-- 인덱스 생성
CREATE INDEX idx_sys_user_username ON system_mgmt.sys_user_info(username);
CREATE INDEX idx_sys_user_status ON system_mgmt.sys_user_info(user_status);
CREATE INDEX idx_sys_user_department ON system_mgmt.sys_user_info(department);

COMMENT ON TABLE system_mgmt.sys_user_info IS '사용자 정보';
```

#### 6.2 역할 및 권한
```sql
-- 역할 정보
CREATE TABLE system_mgmt.sys_role_info (
    role_id                 VARCHAR(50) PRIMARY KEY,
    role_name               VARCHAR(100) NOT NULL,
    role_description        TEXT,
    role_type               VARCHAR(20) CHECK (role_type IN ('SYSTEM', 'BUSINESS', 'CUSTOM')),
    permissions             TEXT,  -- JSON 형태의 권한 목록
    created_by              VARCHAR(50) NOT NULL,
    created_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by             VARCHAR(50),
    modified_datetime       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted              BOOLEAN DEFAULT FALSE,
    CONSTRAINT uk_sys_role_name UNIQUE (role_name)
);

-- 사용자 역할 매핑
CREATE TABLE system_mgmt.sys_user_role_mapping (
    mapping_id              VARCHAR(50) PRIMARY KEY,
    user_id                 VARCHAR(50) NOT NULL,
    role_id                 VARCHAR(50) NOT NULL,
    assigned_by             VARCHAR(50) NOT NULL,
    assigned_datetime       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expired_datetime        TIMESTAMP,
    is_active               BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_sys_user_role_user FOREIGN KEY (user_id) REFERENCES system_mgmt.sys_user_info(user_id),
    CONSTRAINT fk_sys_user_role_role FOREIGN KEY (role_id) REFERENCES system_mgmt.sys_role_info(role_id),
    CONSTRAINT uk_sys_user_role UNIQUE (user_id, role_id)
);

COMMENT ON TABLE system_mgmt.sys_role_info IS '역할 정보';
COMMENT ON TABLE system_mgmt.sys_user_role_mapping IS '사용자 역할 매핑';
```

#### 6.3 메뉴 및 기능 권한
```sql
-- 메뉴 정보
CREATE TABLE system_mgmt.sys_menu_info (
    menu_id                 VARCHAR(50) PRIMARY KEY,
    parent_menu_id          VARCHAR(50),
    menu_name               VARCHAR(100) NOT NULL,
    menu_path               VARCHAR(200),
    menu_icon               VARCHAR(50),
    menu_order              INTEGER DEFAULT 0,
    menu_level              INTEGER DEFAULT 1,
    is_visible              BOOLEAN DEFAULT TRUE,
    permission_required     VARCHAR(100),  -- 필요 권한
    created_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted              BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_sys_menu_parent FOREIGN KEY (parent_menu_id) REFERENCES system_mgmt.sys_menu_info(menu_id)
);

COMMENT ON TABLE system_mgmt.sys_menu_info IS '메뉴 정보';
```

---

### 7. AUDIT 스키마 (감사 및 로그)

#### 7.1 접근 로그
```sql
-- 접근 로그
CREATE TABLE audit.aud_access_log (
    log_id                  VARCHAR(50) PRIMARY KEY,
    user_id                 VARCHAR(50) NOT NULL,
    session_id              VARCHAR(100),
    access_type             VARCHAR(20) CHECK (access_type IN ('LOGIN', 'LOGOUT', 'PAGE_VIEW', 'API_CALL', 'FILE_DOWNLOAD')),
    resource_type           VARCHAR(50),  -- TABLE, COLUMN, MODEL, etc.
    resource_id             VARCHAR(50),
    resource_name           VARCHAR(200),
    action_type             VARCHAR(20) CHECK (action_type IN ('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'EXECUTE')),
    ip_address              INET,
    user_agent              TEXT,
    referer_url             TEXT,
    request_method          VARCHAR(10),
    request_url             TEXT,
    request_parameters      TEXT,  -- JSON 형태
    response_status         INTEGER,
    response_time_ms        INTEGER,
    access_datetime         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_aud_access_user FOREIGN KEY (user_id) REFERENCES system_mgmt.sys_user_info(user_id)
);

-- 인덱스 생성
CREATE INDEX idx_aud_access_user ON audit.aud_access_log(user_id);
CREATE INDEX idx_aud_access_type ON audit.aud_access_log(access_type);
CREATE INDEX idx_aud_access_datetime ON audit.aud_access_log(access_datetime);
CREATE INDEX idx_aud_access_resource ON audit.aud_access_log(resource_type, resource_id);

-- 파티션 테이블로 생성 (월별)
-- CREATE TABLE audit.aud_access_log_2025_01 PARTITION OF audit.aud_access_log
--     FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

COMMENT ON TABLE audit.aud_access_log IS '접근 로그';
```

#### 7.2 변경 이력 로그
```sql
-- 변경 이력 로그
CREATE TABLE audit.aud_change_log (
    change_id               VARCHAR(50) PRIMARY KEY,
    user_id                 VARCHAR(50) NOT NULL,
    table_schema            VARCHAR(100) NOT NULL,
    table_name              VARCHAR(100) NOT NULL,
    operation_type          VARCHAR(20) CHECK (operation_type IN ('INSERT', 'UPDATE', 'DELETE')),
    primary_key_values      TEXT,  -- JSON 형태
    old_values              TEXT,  -- JSON 형태 (UPDATE/DELETE)
    new_values              TEXT,  -- JSON 형태 (INSERT/UPDATE)
    change_reason           TEXT,
    change_datetime         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_aud_change_user FOREIGN KEY (user_id) REFERENCES system_mgmt.sys_user_info(user_id)
);

-- 인덱스 생성
CREATE INDEX idx_aud_change_user ON audit.aud_change_log(user_id);
CREATE INDEX idx_aud_change_table ON audit.aud_change_log(table_schema, table_name);
CREATE INDEX idx_aud_change_operation ON audit.aud_change_log(operation_type);
CREATE INDEX idx_aud_change_datetime ON audit.aud_change_log(change_datetime);

COMMENT ON TABLE audit.aud_change_log IS '변경 이력 로그';
```

---

## 🚀 성능 최적화 전략

### 인덱스 전략
```sql
-- 복합 인덱스 생성 예시
CREATE INDEX idx_md_table_info_composite 
ON metadata.md_table_info(db_id, schema_name, table_name, data_classification);

CREATE INDEX idx_df_flow_analysis_composite 
ON dataflow.df_flow_analysis(program_id, flow_type, source_table_id);

CREATE INDEX idx_ai_query_history_composite 
ON ai_service.ai_query_history(user_id, query_type, query_datetime);
```

### 파티셔닝 전략
```sql
-- 로그성 테이블 월별 파티셔닝
CREATE TABLE audit.aud_access_log (
    -- 컬럼 정의...
) PARTITION BY RANGE (access_datetime);

-- 자동 파티션 관리 함수
CREATE OR REPLACE FUNCTION create_monthly_partitions()
RETURNS void AS $$
DECLARE
    start_date DATE;
    end_date DATE;
    partition_name TEXT;
BEGIN
    start_date := date_trunc('month', CURRENT_DATE);
    end_date := start_date + INTERVAL '1 month';
    partition_name := 'aud_access_log_' || to_char(start_date, 'YYYY_MM');
    
    EXECUTE format('CREATE TABLE IF NOT EXISTS audit.%I PARTITION OF audit.aud_access_log 
                    FOR VALUES FROM (%L) TO (%L)', 
                   partition_name, start_date, end_date);
END;
$$ LANGUAGE plpgsql;
```

### 캐싱 전략
```sql
-- 자주 조회되는 메타데이터를 위한 머티리얼라이즈드 뷰
CREATE MATERIALIZED VIEW metadata.mv_table_summary AS
SELECT 
    t.db_id,
    t.schema_name,
    t.table_name,
    t.table_comment,
    t.record_count,
    t.data_size_mb,
    COUNT(c.column_id) as column_count,
    COUNT(CASE WHEN c.is_personal_info THEN 1 END) as personal_info_columns,
    MAX(t.last_modified_date) as last_modified_date
FROM metadata.md_table_info t
LEFT JOIN metadata.md_column_info c ON t.table_id = c.table_id
WHERE t.is_deleted = FALSE
GROUP BY t.db_id, t.schema_name, t.table_name, t.table_comment, t.record_count, t.data_size_mb;

-- 인덱스 생성
CREATE INDEX idx_mv_table_summary_db ON metadata.mv_table_summary(db_id);

-- 자동 갱신 (스케줄러)
-- SELECT cron.schedule('refresh-metadata-summary', '0 2 * * *', 
--                      'REFRESH MATERIALIZED VIEW metadata.mv_table_summary;');
```

---

## 🔐 보안 및 암호화

### 컬럼 레벨 암호화
```sql
-- 암호화 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 암호화 함수
CREATE OR REPLACE FUNCTION encrypt_sensitive_data(data TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN encode(encrypt(data::bytea, 'kbank-secret-key', 'aes'), 'base64');
END;
$$ LANGUAGE plpgsql;

-- 복호화 함수
CREATE OR REPLACE FUNCTION decrypt_sensitive_data(encrypted_data TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN convert_from(decrypt(decode(encrypted_data, 'base64'), 'kbank-secret-key', 'aes'), 'utf8');
END;
$$ LANGUAGE plpgsql;

-- 트리거를 통한 자동 암호화
CREATE OR REPLACE FUNCTION encrypt_password_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.password_encrypted IS NOT NULL THEN
        NEW.password_encrypted := encrypt_sensitive_data(NEW.password_encrypted);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_encrypt_database_password
    BEFORE INSERT OR UPDATE ON metadata.md_database_info
    FOR EACH ROW
    EXECUTE FUNCTION encrypt_password_trigger();
```

### Row Level Security (RLS)
```sql
-- 테이블별 RLS 활성화
ALTER TABLE metadata.md_table_info ENABLE ROW LEVEL SECURITY;

-- 정책 생성 (사용자는 자신이 속한 팀의 데이터만 조회 가능)
CREATE POLICY user_team_access_policy ON metadata.md_table_info
    FOR ALL TO authenticated_users
    USING (
        owner_team = current_setting('app.current_user_team', true) 
        OR 
        current_setting('app.current_user_role', true) = 'ADMIN'
    );
```

---

## 📊 모니터링 및 통계

### 성능 모니터링 뷰
```sql
-- 테이블별 성능 통계
CREATE VIEW system_mgmt.v_table_performance AS
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;

-- 인덱스 사용률 통계
CREATE VIEW system_mgmt.v_index_usage AS
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched,
    ROUND(
        CASE WHEN idx_scan + seq_scan > 0 
        THEN (idx_scan::float / (idx_scan + seq_scan)) * 100 
        ELSE 0 END, 2
    ) as index_usage_percentage
FROM pg_stat_user_indexes i
JOIN pg_stat_user_tables t ON i.relid = t.relid
ORDER BY index_usage_percentage DESC;
```

### 비즈니스 KPI 추적
```sql
-- 일별 사용량 통계 
CREATE VIEW system_mgmt.v_daily_usage_stats AS
SELECT 
    DATE(access_datetime) as usage_date,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(*) as total_requests,
    COUNT(CASE WHEN access_type = 'API_CALL' THEN 1 END) as api_calls,
    AVG(response_time_ms) as avg_response_time,
    COUNT(CASE WHEN response_status >= 400 THEN 1 END) as error_count
FROM audit.aud_access_log
WHERE access_datetime >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(access_datetime)
ORDER BY usage_date DESC;
```

---

## 🎯 마이그레이션 계획

### 1. As-is 데이터 마이그레이션
```sql
-- 기존 ERWin 메타데이터 마이그레이션 스크립트
CREATE OR REPLACE FUNCTION migrate_erwin_metadata()
RETURNS void AS $$
DECLARE
    erwin_record RECORD;
BEGIN
    -- ERWin Mart에서 데이터 추출 및 변환
    FOR erwin_record IN 
        SELECT * FROM legacy.erwin_tables 
    LOOP
        INSERT INTO metadata.md_table_info (
            table_id, db_id, schema_name, table_name, 
            table_comment, created_by, created_datetime
        ) VALUES (
            gen_random_uuid()::text,
            erwin_record.database_id,
            erwin_record.schema_name,
            erwin_record.table_name,
            erwin_record.description,
            'MIGRATION_SCRIPT',
            CURRENT_TIMESTAMP
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

### 2. 데이터 검증 스크립트
```sql
-- 마이그레이션 데이터 검증
CREATE OR REPLACE FUNCTION validate_migration_data()
RETURNS TABLE(validation_result TEXT, error_count BIGINT) AS $$
BEGIN
    -- 테이블 수 검증
    RETURN QUERY
    SELECT 'Table Count Validation' as validation_result, 
           ABS((SELECT COUNT(*) FROM metadata.md_table_info) - 
               (SELECT COUNT(*) FROM legacy.erwin_tables))::BIGINT as error_count;
    
    -- 참조 무결성 검증
    RETURN QUERY
    SELECT 'Foreign Key Validation' as validation_result,
           (SELECT COUNT(*) FROM metadata.md_column_info c
            LEFT JOIN metadata.md_table_info t ON c.table_id = t.table_id
            WHERE t.table_id IS NULL)::BIGINT as error_count;
END;
$$ LANGUAGE plpgsql;
```

---

## 📋 데이터베이스 운영 가이드

### 백업 전략
```sql
-- 스키마별 백업 스크립트
-- 메타데이터 스키마 (핵심 데이터)
pg_dump -h localhost -U kbank_user -n metadata kbank_metadata_db > metadata_backup_$(date +%Y%m%d).sql

-- 로그 스키마 (압축 백업)
pg_dump -h localhost -U kbank_user -n audit --compress=9 kbank_metadata_db > audit_backup_$(date +%Y%m%d).sql.gz

-- Point-in-time Recovery를 위한 WAL 아카이빙
archive_command = 'cp %p /backup/wal/%f'
```

### 정기 유지보수
```sql
-- 월간 유지보수 스크립트
CREATE OR REPLACE FUNCTION monthly_maintenance()
RETURNS void AS $$
BEGIN
    -- 통계 정보 업데이트
    ANALYZE;
    
    -- 오래된 로그 데이터 아카이빙 (6개월 이전)
    DELETE FROM audit.aud_access_log 
    WHERE access_datetime < CURRENT_DATE - INTERVAL '6 months';
    
    -- 임시 테이블 정리
    DROP TABLE IF EXISTS temp_migration_data;
    
    -- 인덱스 재구축 (필요시)
    REINDEX DATABASE kbank_metadata_db;
    
    -- 파티션 정리
    SELECT drop_old_partitions('audit.aud_access_log', INTERVAL '1 year');
END;
$$ LANGUAGE plpgsql;
```

---

## 🎯 Next Actions

### 즉시 실행 (Week 1)
1. **스키마 생성 스크립트 실행**
2. **기본 테이블 생성**
3. **인덱스 및 제약조건 생성**
4. **기본 데이터 삽입**

### 단기 실행 (Week 2-3)
1. **마이그레이션 스크립트 개발**
2. **성능 테스트 및 튜닝**
3. **백업/복구 프로세스 구축**
4. **모니터링 설정**

### 중기 실행 (Month 2)
1. **파티셔닝 구현**
2. **RLS 정책 적용**
3. **암호화 구현**
4. **운영 프로세스 문서화**

---

**문서 승인**

| 역할 | 이름 | 승인일 | 서명 |
|------|------|--------|------|
| DB 아키텍트 | [ ] | 2025-11-25 | [ ] |
| DBA | [ ] | | [ ] |
| 보안 담당자 | [ ] | | [ ] |
| 프로젝트 매니저 | [ ] | | [ ] |

**다음 검토 예정일**: 2025-12-02