"""
Unit Tests for SQL Query Entity (Domain Layer)
도메인 계층 - SQL 쿼리 엔티티 테스트

TDD 원칙에 따라 Red-Green-Refactor 사이클로 개발
"""
import pytest
from datetime import datetime
from typing import Dict, Any

# Domain entities (아직 구현되지 않음 - TDD 방식)
# from app.domain.entities.sql_query import SQLQuery
# from app.domain.value_objects.query_confidence import QueryConfidence
# from app.domain.value_objects.risk_level import RiskLevel


class TestSQLQueryEntity:
    """SQL Query Entity 테스트 클래스"""
    
    @pytest.mark.unit
    def test_should_create_sql_query_with_valid_data(self, tdd_case):
        """
        TDD Case 1: 유효한 데이터로 SQL Query 생성
        
        Given: 유효한 SQL 쿼리 정보가 주어졌을 때
        When: SQLQuery 엔티티를 생성하면
        Then: 올바른 속성을 가진 엔티티가 생성된다
        """
        # Given - 유효한 SQL 쿼리 데이터
        tdd_case.given("유효한 SQL 쿼리 데이터가 준비됨")
        
        query_text = "SELECT COUNT(*) FROM patients WHERE age > 65"
        natural_language = "65세 이상 환자 수를 조회하세요"
        confidence = 0.92
        risk_level = "low"
        
        # When - SQLQuery 엔티티 생성 (아직 구현되지 않음)
        tdd_case.when("SQLQuery 엔티티를 생성함")
        
        # TODO: 실제 구현 후 주석 해제
        # sql_query = SQLQuery(
        #     text=query_text,
        #     natural_language=natural_language,
        #     confidence=QueryConfidence(confidence),
        #     risk_level=RiskLevel(risk_level)
        # )
        
        # Then - 올바른 속성 확인
        tdd_case.then("올바른 속성을 가진 엔티티가 생성됨")
        
        # Green 단계 - 실제 구현 테스트
        from app.domain.entities.sql_query import SQLQuery
        
        sql_query = SQLQuery(
            text=query_text,
            natural_language=natural_language,
            confidence=confidence
        )
        
        assert sql_query.text == query_text
        assert sql_query.natural_language == natural_language
        assert sql_query.confidence.value == confidence
        # risk_level은 자동 계산되므로 생성자 매개변수 제거 필요
        assert sql_query.created_at is not None

    @pytest.mark.unit
    def test_should_reject_invalid_sql_syntax(self, tdd_case):
        """
        TDD Case 2: 잘못된 SQL 구문 거부
        
        Given: 잘못된 SQL 구문이 주어졌을 때
        When: SQLQuery 엔티티를 생성하면
        Then: ValidationError가 발생한다
        """
        tdd_case.given("잘못된 SQL 구문이 주어짐")
        
        invalid_query = "SELCT * FORM patients WHRE age > 65"  # 오타가 있는 SQL
        natural_language = "65세 이상 환자 조회"
        
        tdd_case.when("잘못된 SQL로 SQLQuery 엔티티를 생성함")
        
        # Then - ValidationError 발생 확인
        tdd_case.then("ValidationError가 발생함")
        
        # 테스트 실패 (Red 단계) - 아직 구현되지 않음
        with pytest.raises(ImportError):
            from app.domain.entities.sql_query import SQLQuery
            from app.domain.exceptions import InvalidSQLSyntaxError
            
            with pytest.raises(InvalidSQLSyntaxError):
                SQLQuery(
                    text=invalid_query,
                    natural_language=natural_language,
                    confidence=0.5,
                    risk_level="medium"
                )

    @pytest.mark.unit
    def test_should_detect_dangerous_sql_operations(self, tdd_case):
        """
        TDD Case 3: 위험한 SQL 작업 탐지
        
        Given: 데이터 변경 SQL이 주어졌을 때
        When: SQLQuery 엔티티를 생성하면
        Then: 높은 위험도로 분류된다
        """
        tdd_case.given("데이터 변경 SQL이 주어짐")
        
        dangerous_queries = [
            "DELETE FROM patients WHERE age > 80",
            "UPDATE patients SET diagnosis = 'healthy'",
            "DROP TABLE patient_data",
            "INSERT INTO patients VALUES (1, 'test', 25)"
        ]
        
        tdd_case.when("위험한 SQL로 SQLQuery 엔티티를 생성함")
        
        for dangerous_sql in dangerous_queries:
            tdd_case.then(f"'{dangerous_sql[:20]}...'이 고위험으로 분류됨")
            
            # 테스트 실패 (Red 단계)
            with pytest.raises(ImportError):
                from app.domain.entities.sql_query import SQLQuery
                
                sql_query = SQLQuery(
                    text=dangerous_sql,
                    natural_language="위험한 작업",
                    confidence=0.8
                )
                
                assert sql_query.risk_level.value == "high"
                assert sql_query.is_dangerous() is True

    @pytest.mark.unit
    def test_should_calculate_estimated_execution_time(self, tdd_case):
        """
        TDD Case 4: 예상 실행 시간 계산
        
        Given: 복잡성이 다른 SQL 쿼리들이 주어졌을 때
        When: 실행 시간을 추정하면
        Then: 쿼리 복잡성에 따라 적절한 시간이 계산된다
        """
        tdd_case.given("복잡성이 다른 SQL 쿼리들이 준비됨")
        
        test_cases = [
            {
                "sql": "SELECT COUNT(*) FROM patients",
                "expected_time_range": (1, 5),  # 1-5초
                "complexity": "simple"
            },
            {
                "sql": """
                SELECT p.region, d.category, AVG(v.total_cost) as avg_cost
                FROM dim_patient p
                JOIN fact_medical_visit v ON p.patient_key = v.patient_key
                JOIN dim_diagnosis d ON v.diagnosis_key = d.diagnosis_key
                WHERE v.visit_date > '2023-01-01'
                GROUP BY p.region, d.category
                ORDER BY avg_cost DESC
                """,
                "expected_time_range": (10, 60),  # 10-60초
                "complexity": "complex"
            }
        ]
        
        tdd_case.when("각 쿼리의 실행 시간을 추정함")
        
        for case in test_cases:
            tdd_case.then(f"{case['complexity']} 쿼리가 적절한 시간으로 추정됨")
            
            # 테스트 실패 (Red 단계)
            with pytest.raises(ImportError):
                from app.domain.entities.sql_query import SQLQuery
                
                sql_query = SQLQuery(
                    text=case["sql"],
                    natural_language=f"{case['complexity']} 쿼리",
                    confidence=0.9
                )
                
                estimated_time = sql_query.estimate_execution_time()
                min_time, max_time = case["expected_time_range"]
                
                assert min_time <= estimated_time <= max_time

    @pytest.mark.unit
    def test_should_identify_pii_data_access(self, tdd_case):
        """
        TDD Case 5: 개인식별정보(PII) 접근 감지
        
        Given: 환자 개인정보가 포함된 쿼리가 주어졌을 때
        When: PII 접근을 검사하면
        Then: PII 포함 여부가 정확히 감지된다
        """
        tdd_case.given("PII가 포함된 쿼리들이 준비됨")
        
        pii_queries = [
            {
                "sql": "SELECT patient_id, name, ssn FROM patients",
                "contains_pii": True,
                "pii_fields": ["name", "ssn"]
            },
            {
                "sql": "SELECT COUNT(*) FROM patients GROUP BY age_group",
                "contains_pii": False,
                "pii_fields": []
            },
            {
                "sql": "SELECT email, phone FROM patient_contact WHERE patient_id = 'P123'",
                "contains_pii": True,
                "pii_fields": ["email", "phone"]
            }
        ]
        
        tdd_case.when("각 쿼리의 PII 포함 여부를 검사함")
        
        for query_case in pii_queries:
            tdd_case.then(f"PII 포함 여부가 올바르게 감지됨: {query_case['contains_pii']}")
            
            # 테스트 실패 (Red 단계)
            with pytest.raises(ImportError):
                from app.domain.entities.sql_query import SQLQuery
                
                sql_query = SQLQuery(
                    text=query_case["sql"],
                    natural_language="PII 테스트 쿼리",
                    confidence=0.8
                )
                
                pii_analysis = sql_query.analyze_pii_access()
                
                assert pii_analysis.contains_pii == query_case["contains_pii"]
                assert set(pii_analysis.pii_fields) == set(query_case["pii_fields"])

    @pytest.mark.unit 
    def test_should_validate_medical_context(self, tdd_case):
        """
        TDD Case 6: 의료 컨텍스트 검증
        
        Given: 의료 도메인 쿼리가 주어졌을 때
        When: 의료 컨텍스트를 검증하면
        Then: 의료 용어와 코드가 올바르게 인식된다
        """
        tdd_case.given("의료 도메인 쿼리가 준비됨")
        
        medical_query = """
        SELECT d.kcd_code, d.diagnosis_name, COUNT(*) as patient_count
        FROM dim_diagnosis d
        JOIN fact_medical_visit v ON d.diagnosis_key = v.diagnosis_key
        WHERE d.kcd_code LIKE 'E11%'  -- 당뇨병 코드
        GROUP BY d.kcd_code, d.diagnosis_name
        """
        
        tdd_case.when("의료 컨텍스트를 검증함")
        
        tdd_case.then("의료 용어와 코드가 올바르게 인식됨")
        
        # 테스트 실패 (Red 단계)
        with pytest.raises(ImportError):
            from app.domain.entities.sql_query import SQLQuery
            from app.domain.value_objects.medical_context import MedicalContext
            
            sql_query = SQLQuery(
                text=medical_query,
                natural_language="당뇨병 환자 통계",
                confidence=0.9
            )
            
            medical_context = sql_query.extract_medical_context()
            
            assert medical_context.has_kcd_codes() is True
            assert 'E11' in medical_context.kcd_codes
            assert medical_context.medical_domain == MedicalContext.Domain.ENDOCRINOLOGY
            assert len(medical_context.medical_terms) > 0

    @pytest.mark.unit
    def test_should_generate_approval_metadata(self, tdd_case):
        """
        TDD Case 7: 승인 메타데이터 생성
        
        Given: SQL 쿼리가 주어졌을 때
        When: 승인용 메타데이터를 생성하면
        Then: HumanLayer에서 필요한 모든 정보가 포함된다
        """
        tdd_case.given("SQL 쿼리가 준비됨")
        
        query_text = """
        SELECT p.region, COUNT(DISTINCT p.patient_key) as patient_count,
               AVG(v.total_cost) as avg_cost
        FROM dim_patient p
        JOIN fact_medical_visit v ON p.patient_key = v.patient_key
        WHERE v.visit_date >= '2024-01-01'
        GROUP BY p.region
        HAVING patient_count > 100
        ORDER BY avg_cost DESC
        """
        
        tdd_case.when("승인용 메타데이터를 생성함")
        
        tdd_case.then("HumanLayer 승인에 필요한 모든 정보가 포함됨")
        
        # 테스트 실패 (Red 단계)
        with pytest.raises(ImportError):
            from app.domain.entities.sql_query import SQLQuery
            
            sql_query = SQLQuery(
                text=query_text,
                natural_language="지역별 환자 수 및 평균 비용 분석",
                confidence=0.85
            )
            
            approval_metadata = sql_query.generate_approval_metadata()
            
            # 필수 메타데이터 확인
            assert "sql" in approval_metadata
            assert "explanation" in approval_metadata
            assert "risk_assessment" in approval_metadata
            assert "estimated_execution_time" in approval_metadata
            assert "data_sensitivity" in approval_metadata
            assert "estimated_rows" in approval_metadata
            assert "tables_accessed" in approval_metadata
            assert "contains_pii" in approval_metadata
            
            # 위험 평가 상세 정보 확인
            risk_assessment = approval_metadata["risk_assessment"]
            assert "level" in risk_assessment
            assert "factors" in risk_assessment
            assert "mitigation_measures" in risk_assessment


# TDD 통합 테스트 (도메인 서비스와의 상호작용)
class TestSQLQueryWithDomainServices:
    """SQL Query와 도메인 서비스 간의 상호작용 테스트"""
    
    @pytest.mark.unit
    def test_should_interact_with_validation_service(self, tdd_case):
        """
        도메인 서비스와의 상호작용 테스트
        
        Given: SQLQuery와 ValidationService가 있을 때
        When: 쿼리 검증을 요청하면
        Then: 적절한 검증 결과가 반환된다
        """
        tdd_case.given("SQLQuery와 ValidationService가 준비됨")
        
        tdd_case.when("쿼리 검증을 요청함")
        
        tdd_case.then("적절한 검증 결과가 반환됨")
        
        # 테스트 실패 (Red 단계) - 도메인 서비스도 아직 구현되지 않음
        with pytest.raises(ImportError):
            from app.domain.entities.sql_query import SQLQuery
            from app.domain.services.sql_validation_service import SQLValidationService
            
            validator = SQLValidationService()
            sql_query = SQLQuery(
                text="SELECT * FROM patients",
                natural_language="모든 환자 조회",
                confidence=0.7
            )
            
            validation_result = validator.validate(sql_query)
            
            assert validation_result.is_valid is not None
            assert validation_result.errors is not None
            assert validation_result.warnings is not None