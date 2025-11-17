"""
SQL Query Entity
SQL 쿼리 도메인 엔티티
"""
import re
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from enum import Enum

from ..value_objects.query_confidence import QueryConfidence
from ..value_objects.risk_level import RiskLevel
from ..exceptions.domain_exceptions import InvalidSQLSyntaxError, PIIDataExposureError


class SQLQueryType(Enum):
    """SQL 쿼리 타입"""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CREATE = "create"
    DROP = "drop"
    ALTER = "alter"
    UNKNOWN = "unknown"


@dataclass
class PIIAnalysisResult:
    """개인식별정보 분석 결과"""
    contains_pii: bool
    pii_fields: List[str]
    risk_score: int
    recommendations: List[str]


@dataclass
class MedicalContext:
    """의료 컨텍스트 정보"""
    kcd_codes: List[str] = field(default_factory=list)
    medical_terms: List[str] = field(default_factory=list)
    medical_domain: Optional[str] = None
    
    def has_kcd_codes(self) -> bool:
        return len(self.kcd_codes) > 0
    
    class Domain:
        ENDOCRINOLOGY = "endocrinology"
        CARDIOLOGY = "cardiology"
        ONCOLOGY = "oncology"
        GENERAL = "general"


@dataclass
class ValidationResult:
    """SQL 검증 결과"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    is_safe: bool = True


@dataclass
class ApprovalMetadata:
    """승인 메타데이터"""
    sql: str
    explanation: str
    risk_assessment: Dict[str, Any]
    estimated_execution_time: int
    data_sensitivity: str
    estimated_rows: int
    tables_accessed: List[str]
    contains_pii: bool


class SQLQuery:
    """SQL 쿼리 도메인 엔티티"""
    
    # PII 필드 패턴
    PII_PATTERNS = {
        'name': [r'name', r'patient_name', r'full_name'],
        'ssn': [r'ssn', r'social_security', r'resident_number'],
        'email': [r'email', r'e_mail'],
        'phone': [r'phone', r'mobile', r'telephone', r'contact'],
        'address': [r'address', r'addr', r'location'],
        'birth_date': [r'birth', r'dob', r'date_of_birth']
    }
    
    # 위험한 SQL 키워드
    DANGEROUS_KEYWORDS = [
        'DELETE', 'DROP', 'TRUNCATE', 'UPDATE', 'INSERT', 
        'ALTER', 'CREATE', 'GRANT', 'REVOKE'
    ]
    
    # 의료 용어 패턴
    MEDICAL_TERMS = [
        'diagnosis', 'patient', 'treatment', 'medication', 
        'symptoms', 'disease', 'therapy', 'prescription'
    ]
    
    def __init__(self, 
                 text: str,
                 natural_language: str,
                 confidence: float):
        """SQL Query 생성자"""
        # 필수 검증
        self._validate_sql_syntax(text)
        
        # 기본 속성
        self.id = str(uuid.uuid4())
        self.text = text.strip()
        self.natural_language = natural_language
        self.confidence = QueryConfidence(confidence)
        self.created_at = datetime.utcnow()
        
        # 위험도 계산
        risk_factors = self._analyze_risk_factors()
        self.risk_level = RiskLevel.from_factors(risk_factors)
        
        # 쿼리 타입 분석
        self.query_type = self._analyze_query_type()
        
        # 테이블 추출
        self.tables_accessed = self._extract_tables()
        
        # 메타데이터
        self.estimated_rows = self._estimate_result_rows()
        self.estimated_execution_time = self.estimate_execution_time()
    
    def _validate_sql_syntax(self, sql: str) -> None:
        """기본 SQL 구문 검증"""
        sql_upper = sql.upper().strip()
        
        # 빈 쿼리 체크
        if not sql_upper:
            raise InvalidSQLSyntaxError(sql, "Empty SQL query")
        
        # 기본 SQL 키워드 체크
        valid_start_keywords = ['SELECT', 'WITH', 'EXPLAIN']
        if not any(sql_upper.startswith(keyword) for keyword in valid_start_keywords):
            # 위험한 키워드로 시작하는 경우 오류
            if any(sql_upper.startswith(keyword) for keyword in self.DANGEROUS_KEYWORDS):
                raise InvalidSQLSyntaxError(sql, "Dangerous SQL operation not allowed")
        
        # 기본 구문 오류 체크 (간단한 패턴)
        if 'SELCT' in sql_upper or 'FORM' in sql_upper or 'WHRE' in sql_upper:
            raise InvalidSQLSyntaxError(sql, "SQL syntax error detected")
    
    def _analyze_risk_factors(self) -> List[str]:
        """위험 요소 분석"""
        factors = []
        sql_upper = self.text.upper()
        
        # 위험한 키워드 체크
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword in sql_upper:
                factors.append(f"dangerous_keyword_{keyword.lower()}")
        
        # PII 필드 체크
        for pii_type, patterns in self.PII_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, self.text, re.IGNORECASE):
                    factors.append(f"pii_access_{pii_type}")
        
        # 복잡한 조인 체크
        join_count = len(re.findall(r'\bJOIN\b', sql_upper))
        if join_count > 3:
            factors.append("complex_join_query")
        
        # 서브쿼리 체크
        if '(' in self.text and 'SELECT' in sql_upper:
            factors.append("subquery_usage")
        
        return factors
    
    def _analyze_query_type(self) -> SQLQueryType:
        """쿼리 타입 분석"""
        sql_upper = self.text.upper().strip()
        
        if sql_upper.startswith('SELECT'):
            return SQLQueryType.SELECT
        elif sql_upper.startswith('INSERT'):
            return SQLQueryType.INSERT
        elif sql_upper.startswith('UPDATE'):
            return SQLQueryType.UPDATE
        elif sql_upper.startswith('DELETE'):
            return SQLQueryType.DELETE
        elif sql_upper.startswith('CREATE'):
            return SQLQueryType.CREATE
        elif sql_upper.startswith('DROP'):
            return SQLQueryType.DROP
        elif sql_upper.startswith('ALTER'):
            return SQLQueryType.ALTER
        else:
            return SQLQueryType.UNKNOWN
    
    def _extract_tables(self) -> List[str]:
        """테이블 명 추출 (간단한 패턴 매칭)"""
        tables = []
        
        # FROM 절에서 테이블 추출
        from_pattern = r'\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        from_matches = re.findall(from_pattern, self.text, re.IGNORECASE)
        tables.extend(from_matches)
        
        # JOIN 절에서 테이블 추출
        join_pattern = r'\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        join_matches = re.findall(join_pattern, self.text, re.IGNORECASE)
        tables.extend(join_matches)
        
        return list(set(tables))  # 중복 제거
    
    def _estimate_result_rows(self) -> int:
        """결과 행 수 추정 (단순한 휴리스틱)"""
        sql_upper = self.text.upper()
        
        # COUNT 쿼리는 1행
        if 'COUNT(' in sql_upper:
            return 1
        
        # GROUP BY가 있으면 그룹 수만큼
        if 'GROUP BY' in sql_upper:
            return 50  # 평균적인 그룹 수
        
        # WHERE 조건이 있으면 필터링된 수
        if 'WHERE' in sql_upper:
            return 100
        
        # 조인이 있으면 더 많은 결과
        join_count = len(re.findall(r'\bJOIN\b', sql_upper))
        if join_count > 0:
            return 500 * join_count
        
        # 기본값
        return 1000
    
    def estimate_execution_time(self) -> int:
        """실행 시간 추정 (초 단위)"""
        base_time = 1  # 기본 1초
        
        # 조인 수에 따른 복잡도
        join_count = len(re.findall(r'\bJOIN\b', self.text.upper()))
        base_time += join_count * 2
        
        # GROUP BY, ORDER BY 추가 시간
        if 'GROUP BY' in self.text.upper():
            base_time += 3
        if 'ORDER BY' in self.text.upper():
            base_time += 2
        
        # 서브쿼리 추가 시간
        subquery_count = self.text.count('(')
        base_time += subquery_count * 1
        
        # 추정 행 수에 따른 조정
        if self.estimated_rows > 10000:
            base_time += 10
        elif self.estimated_rows > 1000:
            base_time += 5
        
        return min(base_time, 300)  # 최대 5분
    
    def is_dangerous(self) -> bool:
        """위험한 쿼리인지 확인"""
        return self.risk_level.score >= 3
    
    def analyze_pii_access(self) -> PIIAnalysisResult:
        """개인식별정보 접근 분석"""
        pii_fields = []
        
        for pii_type, patterns in self.PII_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, self.text, re.IGNORECASE):
                    pii_fields.append(pii_type)
        
        contains_pii = len(pii_fields) > 0
        risk_score = len(pii_fields) * 2  # PII 필드당 위험도 2점
        
        recommendations = []
        if contains_pii:
            recommendations.extend([
                "데이터 마스킹 적용 필요",
                "접근 권한 재확인 필요",
                "결과 데이터 보안 저장 필요"
            ])
        
        return PIIAnalysisResult(
            contains_pii=contains_pii,
            pii_fields=list(set(pii_fields)),
            risk_score=risk_score,
            recommendations=recommendations
        )
    
    def extract_medical_context(self) -> MedicalContext:
        """의료 컨텍스트 추출"""
        # KCD 코드 패턴 (예: E11, I10 등)
        kcd_pattern = r'\b[A-Z]\d{1,2}%?\b'
        kcd_codes = re.findall(kcd_pattern, self.text)
        
        # 의료 용어 추출
        medical_terms = []
        for term in self.MEDICAL_TERMS:
            if re.search(term, self.text, re.IGNORECASE):
                medical_terms.append(term)
        
        # 도메인 추정
        medical_domain = MedicalContext.Domain.GENERAL
        if any(code.startswith('E') for code in kcd_codes):
            medical_domain = MedicalContext.Domain.ENDOCRINOLOGY
        elif any(code.startswith('I') for code in kcd_codes):
            medical_domain = MedicalContext.Domain.CARDIOLOGY
        elif any(code.startswith('C') for code in kcd_codes):
            medical_domain = MedicalContext.Domain.ONCOLOGY
        
        return MedicalContext(
            kcd_codes=kcd_codes,
            medical_terms=medical_terms,
            medical_domain=medical_domain
        )
    
    def generate_approval_metadata(self) -> Dict[str, Any]:
        """HumanLayer 승인용 메타데이터 생성"""
        pii_analysis = self.analyze_pii_access()
        medical_context = self.extract_medical_context()
        
        risk_assessment = {
            "level": self.risk_level.value,
            "score": self.risk_level.score,
            "factors": self.risk_level.factors,
            "mitigation_measures": [
                "쿼리 실행 시간 제한",
                "결과 행 수 제한",
                "접근 로그 기록"
            ]
        }
        
        # 데이터 민감도 계산
        data_sensitivity = "low"
        if pii_analysis.contains_pii:
            data_sensitivity = "high"
        elif medical_context.has_kcd_codes():
            data_sensitivity = "medium"
        
        return {
            "sql": self.text,
            "explanation": self.natural_language,
            "risk_assessment": risk_assessment,
            "estimated_execution_time": self.estimated_execution_time,
            "data_sensitivity": data_sensitivity,
            "estimated_rows": self.estimated_rows,
            "tables_accessed": self.tables_accessed,
            "contains_pii": pii_analysis.contains_pii,
            "pii_fields": pii_analysis.pii_fields,
            "medical_context": {
                "kcd_codes": medical_context.kcd_codes,
                "medical_terms": medical_context.medical_terms,
                "domain": medical_context.medical_domain
            },
            "query_metadata": {
                "id": self.id,
                "type": self.query_type.value,
                "confidence": self.confidence.value,
                "created_at": self.created_at.isoformat()
            }
        }
    
    def __str__(self) -> str:
        return f"SQLQuery(id={self.id[:8]}..., type={self.query_type.value}, risk={self.risk_level.value})"
    
    def __repr__(self) -> str:
        return (f"SQLQuery(text='{self.text[:50]}...', "
                f"confidence={self.confidence.value}, "
                f"risk_level='{self.risk_level.value}')")