from typing import Optional, Dict, Any, List
from app.core.config import settings
import duckdb
import time
import uuid
from datetime import datetime

class Text2SQLService:
    """Service for converting natural language to SQL queries"""
    
    def __init__(self):
        self.query_history = []  # In-memory storage for demo
        
        # Initialize LLM if available
        self.llm = None
        try:
            if settings.ANTHROPIC_API_KEY:
                # Use Claude (Anthropic)
                from langchain_anthropic import ChatAnthropic
                self.llm = ChatAnthropic(
                    api_key=settings.ANTHROPIC_API_KEY,
                    model="claude-3-haiku-20240307",  # Fast and efficient
                    temperature=0
                )
                print("✅ Using Claude (Anthropic) LLM")
            elif settings.OPENAI_API_KEY:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    model="gpt-4-turbo-preview",
                    temperature=0
                )
                print("✅ Using OpenAI LLM")
            else:
                # Try Ollama as fallback (local LLM)
                from langchain_community.llms import Ollama
                self.llm = Ollama(
                    model="llama3.2:3b",
                    base_url="http://localhost:11434"
                )
                print("✅ Using local Ollama LLM")
        except Exception as e:
            print(f"⚠️ LLM initialization failed: {e}")
            print("⚠️ Using rule-based fallback")
    
    async def natural_language_to_sql(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        include_explanation: bool = True
    ) -> Dict[str, Any]:
        """Convert natural language question to SQL query"""
        
        # Get schema context
        schema_context = self._get_schema_context()
        
        if self.llm:
            # Use LLM to generate SQL
            prompt = f"""You are a SQL expert for a medical data warehouse using DuckDB.
            Convert the following Korean question to a SQL query.
            
            Database Schema:
            {schema_context}
            
            Question: {question}
            
            DuckDB Syntax Rules:
            1. Use proper JOIN conditions
            2. Include appropriate WHERE clauses
            3. Use GROUP BY for aggregations
            4. For current date: use CURRENT_DATE or '2025-11-17'::DATE
            5. For date arithmetic: use INTERVAL, e.g., CURRENT_DATE - INTERVAL 1 YEAR
            6. For date ranges: use BETWEEN '2024-11-17'::DATE AND '2025-11-17'::DATE
            7. Do NOT use MySQL functions like CURDATE(), DATE_SUB()
            8. Return only the SQL query, no explanations
            
            SQL Query:"""
            
            response = self.llm.invoke(prompt)
            sql = response.content.strip() if hasattr(response, 'content') else str(response).strip()
            
            # Clean SQL (remove markdown formatting if present)
            if sql.startswith('```sql'):
                sql = sql.replace('```sql', '').replace('```', '').strip()
            elif sql.startswith('```'):
                sql = sql.replace('```', '').strip()
            
            # Generate explanation
            explanation = ""
            if include_explanation:
                explain_prompt = f"""다음 SQL 쿼리를 간단한 한국어로 설명해주세요:
                {sql}
                
                어떤 데이터를 조회하는지 간결하게 설명해주세요."""
                
                explain_response = self.llm.invoke(explain_prompt)
                explanation = explain_response.content.strip() if hasattr(explain_response, 'content') else str(explain_response).strip()
            
            confidence = 0.85  # Would be calculated based on validation
        else:
            # Fallback to rule-based generation
            sql, explanation, confidence = self._generate_sql_rule_based(question)
        
        # Store in history
        query_record = {
            "id": str(uuid.uuid4()),
            "question": question,
            "sql": sql,
            "explanation": explanation,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.query_history.append(query_record)
        
        return {
            "sql": sql,
            "explanation": explanation,
            "confidence": confidence,
            "execution_result": None
        }
    
    def _get_schema_context(self) -> str:
        """Get database schema as context for LLM"""
        return """
        Tables:
        1. dim_patient (환자 차원)
           - patient_key: 환자 고유 키
           - patient_name: 환자 이름
           - age_group: 연령대 (20대, 30대, etc.)
           - gender: 성별 (남, 여)
           - region: 지역
        
        2. dim_department (진료과 차원)
           - dept_key: 진료과 키
           - dept_name: 진료과명
           - dept_category: 진료과 분류
        
        3. dim_diagnosis (진단 차원)
           - diagnosis_key: 진단 고유 키
           - kcd_code: KCD 질병 코드
           - diagnosis_name: 진단명
           - category: 질병 분류
        
        4. fact_visit (진료 사실)
           - visit_key: 방문 고유 키
           - patient_key: 환자 키 (FK to dim_patient)
           - diagnosis_key: 진단 키 (FK to dim_diagnosis)
           - dept_key: 진료과 키 (FK to dim_department)
           - visit_date: 방문 날짜
           - visit_count: 방문 횟수
           - duration_days: 입원 일수
           - total_cost: 진료비
           - visit_type: 진료 유형 (입원, 외래, 응급실)
        
        5. fact_lab_test (검사 결과)
           - test_key: 검사 키
           - patient_key: 환자 키
           - visit_key: 방문 키
           - test_name: 검사명
           - test_date: 검사 날짜
           - test_value: 검사 수치
           - unit: 단위
           - reference_range: 참조 범위
        
        6. fact_vital_signs (생체 징후)
           - vital_key: 생체징후 키
           - patient_key: 환자 키
           - visit_key: 방문 키
           - measurement_time: 측정 시간
           - vital_type: 생체징후 종류 (수축기혈압, 이완기혈압, 맥박, 체온)
           - vital_value: 측정값
           - unit: 단위
        
        7. fact_medical_record (의료기록)
           - record_key: 기록 키
           - patient_key: 환자 키
           - visit_key: 방문 키
           - dept_key: 진료과 키
           - record_type: 기록 유형 (입원경과기록, 외래경과기록, 퇴원요약)
           - record_date: 기록 날짜
           - record_content: 기록 내용
        
        8. fact_prescription (처방)
           - prescription_key: 처방 키
           - patient_key: 환자 키
           - visit_key: 방문 키
           - medication_name: 약물명
           - medication_category: 약물 분류
           - dosage: 용량
           - unit: 단위
           - frequency_per_day: 일일 복용 횟수
           - duration_days: 처방 일수
           - start_date: 처방 시작일
           - end_date: 처방 종료일
        
        Sample Data:
        - 환자: 홍길동 (당뇨병, 내분비내과), 김철수 (심장질환, 심장내과), 김영희 (고혈압, 심장내과)
        - 검사: 중성지방, 총콜레스테롤, Troponin I, CK-MB, BNP, HbA1c
        - Vital Signs: 수축기혈압, 이완기혈압, 맥박, 체온
        - 약물: 메트포르민(당뇨병), 암로디핀(고혈압), 아스피린(항혈전), 로사르탄(고혈압)
        - 시점: 2025년 11월이 현재 달 (오늘: 2025-11-17)
        
        Common KCD codes:
        - E11: 당뇨병
        - I10: 고혈압
        - E78: 고지혈증
        - C%: 암
        - J%: 호흡기 질환
        """
    
    def _generate_sql_rule_based(self, question: str) -> tuple[str, str, float]:
        """Simple rule-based SQL generation for fallback"""
        question_lower = question.lower()
        
        # Pattern matching for common queries
        if "당뇨" in question:
            if "몇 명" in question or "환자 수" in question:
                sql = """
                SELECT COUNT(DISTINCT fv.patient_key) as patient_count
                FROM fact_visit fv
                JOIN dim_diagnosis dd ON fv.diagnosis_key = dd.diagnosis_key
                WHERE dd.kcd_code LIKE 'E11%'
                """
                explanation = "당뇨병(E11) 진단을 받은 환자 수를 조회합니다."
                confidence = 0.7
            else:
                sql = "SELECT * FROM dim_diagnosis WHERE kcd_code LIKE 'E11%'"
                explanation = "당뇨병 관련 진단 정보를 조회합니다."
                confidence = 0.5
        elif "고혈압" in question:
            sql = """
            SELECT COUNT(DISTINCT fv.patient_key) as patient_count
            FROM fact_visit fv
            JOIN dim_diagnosis dd ON fv.diagnosis_key = dd.diagnosis_key
            WHERE dd.kcd_code LIKE 'I10%'
            """
            explanation = "고혈압(I10) 진단을 받은 환자 수를 조회합니다."
            confidence = 0.7
        else:
            # Default query
            sql = "SELECT COUNT(*) as total_visits FROM fact_visit"
            explanation = "전체 방문 횟수를 조회합니다."
            confidence = 0.3
        
        return sql, explanation, confidence
    
    async def execute_sql(
        self,
        sql: str,
        limit: Optional[int] = 100
    ) -> Dict[str, Any]:
        """Execute SQL query and return results"""
        start_time = time.time()
        
        try:
            # Initialize DuckDB connection
            conn = duckdb.connect(':memory:')
            
            # Create sample tables (replace with actual database connection)
            self._create_sample_tables(conn)
            
            # Add LIMIT if not present
            if limit and "limit" not in sql.lower():
                # Remove trailing semicolon if present
                sql_clean = sql.rstrip(';').strip()
                sql = f"{sql_clean} LIMIT {limit}"
            
            # Execute query
            result = conn.execute(sql).fetchall()
            columns = [desc[0] for desc in conn.description] if conn.description else []
            
            # Convert to dict format
            results = [
                dict(zip(columns, row))
                for row in result
            ]
            
            conn.close()
            
            execution_time = (time.time() - start_time) * 1000
            
            return {
                "results": results,
                "row_count": len(results),
                "columns": columns,
                "execution_time_ms": execution_time,
                "natural_language_explanation": self._generate_result_explanation(results, columns)
            }
        except Exception as e:
            raise Exception(f"SQL execution failed: {str(e)}")
    
    def _create_sample_tables(self, conn):
        """Create sample tables for demonstration"""
        # Create patient table with names
        conn.execute("""
            CREATE TABLE dim_patient AS
            SELECT * FROM (VALUES
                (1, '홍길동', '30대', '남', '서울'),
                (2, '김영희', '40대', '여', '경기'),
                (3, '박철수', '50대', '남', '부산'),
                (4, '이미영', '60대', '여', '서울'),
                (5, '최민수', '20대', '남', '대구'),
                (6, '정수진', '30대', '여', '인천'),
                (7, '강동원', '40대', '남', '울산'),
                (8, '김철수', '50대', '남', '서울'),
                (9, '이영희', '50대', '여', '대전'),
                (10, '박민호', '50대', '남', '광주'),
                (11, '최수정', '50대', '여', '대구'),
                (12, '장영수', '50대', '남', '부산'),
                (13, '윤미자', '60대', '여', '서울'),
                (14, '조현수', '40대', '남', '인천'),
                (15, '한지영', '30대', '여', '부산'),
                (16, '송민준', '50대', '남', '대구'),
                (17, '김혜진', '50대', '여', '광주'),
                (18, '박성호', '50대', '남', '울산'),
                (19, '이수연', '30대', '여', '서울'),
                (20, '정태현', '40대', '남', '대전')
            ) AS t(patient_key, patient_name, age_group, gender, region)
        """)
        
        # Create department table
        conn.execute("""
            CREATE TABLE dim_department AS
            SELECT * FROM (VALUES
                (1, '내분비내과', '내과계'),
                (2, '심장내과', '내과계'),
                (3, '호흡기내과', '내과계'),
                (4, '종양내과', '내과계'),
                (5, '소화기내과', '내과계'),
                (6, '응급의학과', '응급실'),
                (7, '순환기내과', '내과계'),
                (8, '신장내과', '내과계')
            ) AS t(dept_key, dept_name, dept_category)
        """)
        
        conn.execute("""
            CREATE TABLE dim_diagnosis AS
            SELECT * FROM (VALUES
                (1, 'E11', '2형 당뇨병', '내분비질환'),
                (2, 'I10', '본태성 고혈압', '순환기질환'),
                (3, 'J45', '천식', '호흡기질환'),
                (4, 'C50', '유방암', '종양'),
                (5, 'K29', '위염', '소화기질환'),
                (6, 'E78', '고지혈증', '내분비질환')
            ) AS t(diagnosis_key, kcd_code, diagnosis_name, category)
        """)
        
        # Create visit table with department and visit type
        conn.execute("""
            CREATE TABLE fact_visit AS
            SELECT * FROM (VALUES
                (1, 1, 1, 1, '2023-01-15'::DATE, 1, 5, 1500000, '입원'),
                (2, 2, 2, 2, '2023-02-20'::DATE, 1, 3, 800000, '입원'),
                (3, 3, 1, 1, '2023-03-10'::DATE, 2, 7, 2000000, '입원'),
                (4, 4, 3, 3, '2023-04-05'::DATE, 1, 2, 500000, '입원'),
                (5, 5, 4, 4, '2023-05-12'::DATE, 1, 10, 5000000, '입원'),
                (6, 1, 6, 1, '2023-06-01'::DATE, 1, 0, 300000, '외래'),
                (7, 1, 1, 1, '2023-07-15'::DATE, 1, 3, 800000, '입원'),
                (8, 8, 2, 2, '2025-01-10'::DATE, 1, 4, 1200000, '입원'),
                (9, 8, 2, 2, '2025-02-15'::DATE, 1, 0, 150000, '외래'),
                (10, 8, 2, 2, '2025-03-20'::DATE, 1, 0, 180000, '외래'),
                (11, 8, 2, 2, '2025-05-10'::DATE, 1, 0, 160000, '외래'),
                (12, 9, 2, 6, '2025-11-01'::DATE, 1, 2, 800000, '응급실'),
                (13, 10, 2, 6, '2025-11-02'::DATE, 1, 1, 600000, '응급실'),
                (14, 11, 2, 6, '2025-11-03'::DATE, 1, 0, 300000, '응급실'),
                (15, 12, 2, 2, '2025-11-05'::DATE, 1, 0, 200000, '외래'),
                (16, 2, 1, 1, '2025-11-10'::DATE, 1, 6, 1800000, '입원'),
                (17, 3, 1, 1, '2025-11-12'::DATE, 1, 8, 2200000, '입원'),
                (18, 6, 1, 1, '2025-11-15'::DATE, 1, 0, 250000, '외래'),
                (19, 7, 1, 1, '2025-11-16'::DATE, 1, 0, 280000, '외래'),
                (20, 13, 1, 1, '2025-11-05'::DATE, 1, 0, 220000, '외래'),
                (21, 14, 2, 2, '2025-11-06'::DATE, 1, 0, 180000, '외래'),
                (22, 15, 3, 3, '2025-11-07'::DATE, 1, 0, 150000, '외래'),
                (23, 16, 2, 2, '2025-11-08'::DATE, 1, 0, 200000, '외래'),
                (24, 17, 2, 2, '2025-11-09'::DATE, 1, 0, 190000, '외래'),
                (25, 18, 2, 2, '2025-11-11'::DATE, 1, 0, 210000, '외래'),
                (26, 19, 1, 1, '2025-11-13'::DATE, 1, 0, 240000, '외래'),
                (27, 20, 2, 2, '2025-11-14'::DATE, 1, 0, 170000, '외래'),
                (28, 1, 1, 1, '2025-11-17'::DATE, 1, 0, 260000, '외래'),
                (29, 8, 2, 2, '2025-11-17'::DATE, 1, 0, 180000, '외래'),
                (30, 16, 2, 6, '2025-10-15'::DATE, 1, 3, 900000, '응급실'),
                (31, 18, 2, 6, '2025-10-20'::DATE, 1, 1, 650000, '응급실'),
                (23, 16, 2, 2, '2025-11-08'::DATE, 1, 0, 200000, '외래'),
                (25, 18, 2, 2, '2025-11-11'::DATE, 1, 0, 210000, '외래'),
                (32, 13, 1, 1, '2025-10-05'::DATE, 1, 4, 1200000, '입원'),
                (33, 15, 1, 1, '2025-09-15'::DATE, 1, 7, 1800000, '입원'),
                (34, 19, 1, 1, '2025-08-20'::DATE, 1, 5, 1500000, '입원'),
                (35, 20, 1, 1, '2025-07-10'::DATE, 1, 6, 1600000, '입원'),
                (36, 1, 1, 1, '2025-11-15'::DATE, 1, 3, 900000, '입원')
            ) AS t(visit_key, patient_key, diagnosis_key, dept_key, visit_date, visit_count, duration_days, total_cost, visit_type)
        """)
        
        # Create lab test results table
        conn.execute("""
            CREATE TABLE fact_lab_test AS
            SELECT * FROM (VALUES
                (1, 1, 1, '중성지방', '2023-01-16'::DATE, 250.5, 'mg/dL', '< 150'),
                (2, 1, 1, '총콜레스테롤', '2023-01-16'::DATE, 220.3, 'mg/dL', '< 200'),
                (3, 1, 1, 'HDL콜레스테롤', '2023-01-16'::DATE, 45.2, 'mg/dL', '> 40'),
                (4, 1, 1, 'LDL콜레스테롤', '2023-01-16'::DATE, 130.1, 'mg/dL', '< 100'),
                (5, 1, 7, '중성지방', '2023-07-16'::DATE, 180.2, 'mg/dL', '< 150'),
                (6, 1, 7, '총콜레스테롤', '2023-07-16'::DATE, 195.8, 'mg/dL', '< 200'),
                (7, 2, 2, '중성지방', '2023-02-21'::DATE, 120.5, 'mg/dL', '< 150'),
                (8, 2, 2, '총콜레스테롤', '2023-02-21'::DATE, 180.3, 'mg/dL', '< 200'),
                (9, 8, 8, 'Troponin I', '2025-01-11'::DATE, 0.8, 'ng/mL', '< 0.04'),
                (10, 8, 8, 'CK-MB', '2025-01-11'::DATE, 15.2, 'ng/mL', '< 6.3'),
                (11, 8, 8, 'BNP', '2025-01-11'::DATE, 850, 'pg/mL', '< 100'),
                (12, 8, 9, 'Troponin I', '2025-02-16'::DATE, 0.02, 'ng/mL', '< 0.04'),
                (13, 8, 10, 'HbA1c', '2025-03-21'::DATE, 7.8, '%', '< 7.0'),
                (14, 8, 11, 'HbA1c', '2025-05-11'::DATE, 7.2, '%', '< 7.0'),
                (15, 9, 12, '혈청크레아티닌', '2025-11-01'::DATE, 1.8, 'mg/dL', '0.7-1.2'),
                (16, 10, 13, 'BUN', '2025-11-02'::DATE, 45, 'mg/dL', '8-20'),
                (17, 8, 23, 'CBC', '2025-11-08'::DATE, 12.5, 'g/dL', '12-16'),
                (18, 8, 23, '혈소판수', '2025-11-08'::DATE, 280000, '/μL', '150000-400000'),
                (19, 8, 23, 'PT', '2025-11-08'::DATE, 11.8, 'sec', '9.5-13.5'),
                (20, 8, 23, 'aPTT', '2025-11-08'::DATE, 32.5, 'sec', '25-35'),
                (21, 8, 29, 'Troponin I', '2025-11-17'::DATE, 0.01, 'ng/mL', '< 0.04'),
                (22, 8, 29, 'BNP', '2025-11-17'::DATE, 125, 'pg/mL', '< 100'),
                (23, 16, 23, '혈청크레아티닌', '2025-11-08'::DATE, 1.2, 'mg/dL', '0.7-1.2'),
                (24, 18, 25, 'BUN', '2025-11-11'::DATE, 18, 'mg/dL', '8-20'),
                (25, 1, 28, '중성지방', '2025-11-17'::DATE, 165.2, 'mg/dL', '< 150'),
                (26, 1, 28, '총콜레스테롤', '2025-11-17'::DATE, 185.5, 'mg/dL', '< 200'),
                (27, 1, 28, 'HDL콜레스테롤', '2025-11-17'::DATE, 48.3, 'mg/dL', '> 40'),
                (28, 1, 28, 'LDL콜레스테롤', '2025-11-17'::DATE, 115.8, 'mg/dL', '< 100'),
                (29, 1, 36, '중성지방', '2025-11-15'::DATE, 195.8, 'mg/dL', '< 150'),
                (30, 1, 36, '총콜레스테롤', '2025-11-15'::DATE, 210.3, 'mg/dL', '< 200'),
                (31, 1, 36, 'HDL콜레스테롤', '2025-11-15'::DATE, 42.1, 'mg/dL', '> 40'),
                (32, 1, 36, 'LDL콜레스테롤', '2025-11-15'::DATE, 125.4, 'mg/dL', '< 100')
            ) AS t(test_key, patient_key, visit_key, test_name, test_date, test_value, unit, reference_range)
        """)
        
        # Create vital signs table
        conn.execute("""
            CREATE TABLE fact_vital_signs AS
            SELECT * FROM (VALUES
                (1, 1, 1, '2023-01-15 09:00:00'::TIMESTAMP, '수축기혈압', 145.0, 'mmHg'),
                (2, 1, 1, '2023-01-15 09:00:00'::TIMESTAMP, '이완기혈압', 92.0, 'mmHg'),
                (3, 1, 1, '2023-01-15 09:00:00'::TIMESTAMP, '맥박', 78.0, 'bpm'),
                (4, 1, 1, '2023-01-15 09:00:00'::TIMESTAMP, '체온', 36.5, '°C'),
                (5, 1, 7, '2023-07-15 10:30:00'::TIMESTAMP, '수축기혈압', 138.0, 'mmHg'),
                (6, 1, 7, '2023-07-15 10:30:00'::TIMESTAMP, '이완기혈압', 88.0, 'mmHg'),
                (7, 1, 7, '2023-07-15 10:30:00'::TIMESTAMP, '맥박', 72.0, 'bpm'),
                (8, 2, 2, '2023-02-20 14:15:00'::TIMESTAMP, '수축기혈압', 125.0, 'mmHg'),
                (9, 2, 2, '2023-02-20 14:15:00'::TIMESTAMP, '이완기혈압', 80.0, 'mmHg'),
                (10, 2, 2, '2023-02-20 14:15:00'::TIMESTAMP, '맥박', 68.0, 'bpm'),
                (11, 8, 8, '2025-01-10 09:00:00'::TIMESTAMP, '수축기혈압', 160.0, 'mmHg'),
                (12, 8, 8, '2025-01-10 09:00:00'::TIMESTAMP, '이완기혈압', 95.0, 'mmHg'),
                (13, 8, 8, '2025-01-10 09:00:00'::TIMESTAMP, '맥박', 85.0, 'bpm'),
                (14, 9, 12, '2025-11-01 18:30:00'::TIMESTAMP, '수축기혈압', 180.0, 'mmHg'),
                (15, 9, 12, '2025-11-01 18:30:00'::TIMESTAMP, '이완기혈압', 110.0, 'mmHg'),
                (16, 10, 13, '2025-11-02 20:15:00'::TIMESTAMP, '수축기혈압', 175.0, 'mmHg'),
                (17, 10, 13, '2025-11-02 20:15:00'::TIMESTAMP, '이완기혈압', 105.0, 'mmHg'),
                (18, 1, 28, '2025-11-17 14:30:00'::TIMESTAMP, '수축기혈압', 132.0, 'mmHg'),
                (19, 1, 28, '2025-11-17 14:30:00'::TIMESTAMP, '이완기혈압', 78.0, 'mmHg'),
                (20, 1, 28, '2025-11-17 14:30:00'::TIMESTAMP, '맥박', 68.0, 'bpm'),
                (21, 1, 28, '2025-11-17 14:30:00'::TIMESTAMP, '체온', 36.3, '°C'),
                (22, 1, 36, '2025-11-15 08:00:00'::TIMESTAMP, '수축기혈압', 145.0, 'mmHg'),
                (23, 1, 36, '2025-11-15 08:00:00'::TIMESTAMP, '이완기혈압', 88.0, 'mmHg'),
                (24, 1, 36, '2025-11-15 08:00:00'::TIMESTAMP, '맥박', 82.0, 'bpm'),
                (25, 1, 36, '2025-11-15 08:00:00'::TIMESTAMP, '체온', 37.2, '°C')
            ) AS t(vital_key, patient_key, visit_key, measurement_time, vital_type, vital_value, unit)
        """)
        
        # Create medical records table
        conn.execute("""
            CREATE TABLE fact_medical_record AS
            SELECT * FROM (VALUES
                (1, 1, 1, 1, '입원경과기록', '2023-01-15'::DATE, '당뇨병 악화로 입원. 혈당 조절을 위한 인슐린 치료 시작. 고지혈증 동반되어 스타틴 병용 치료 계획.'),
                (2, 1, 1, 1, '입원경과기록', '2023-01-17'::DATE, '인슐린 용량 조절 후 혈당 개선 양상. 중성지방 수치 여전히 높아 식이요법 교육 실시.'),
                (3, 1, 1, 1, '퇴원요약', '2023-01-20'::DATE, '혈당 조절 양호하여 퇴원. 외래 추적관찰 예정. 당뇨병성 합병증 예방을 위한 지속적 관리 필요.'),
                (4, 1, 7, 1, '외래경과기록', '2023-07-15'::DATE, '당뇨병 외래 추적관찰. HbA1c 7.2%로 목표치 근접. 체중감량 5kg 달성하여 혈압도 개선됨.'),
                (5, 2, 2, 2, '외래경과기록', '2023-02-20'::DATE, '고혈압 초진. ACE inhibitor 처방 시작. 생활습관 개선 교육 실시.'),
                (6, 8, 8, 2, '입원경과기록', '2025-01-10'::DATE, '급성 심근경색으로 응급실 경유하여 입원. PCI 시행 후 상태 호전됨. 심장효소 수치 점차 감소 추세.'),
                (7, 8, 9, 2, '외래경과기록', '2025-02-15'::DATE, '심근경색 후 첫 외래 추적관찰. 심기능 회복 양호. 이중항혈소판치료 지속 중.'),
                (8, 8, 10, 2, '외래경과기록', '2025-03-20'::DATE, '심장 초음파상 좌심실 기능 정상화. 운동부하검사 정상 소견.'),
                (9, 8, 11, 2, '외래경과기록', '2025-05-10'::DATE, '정기 추적관찰. 흉통 없음. HbA1c 개선되어 목표치 달성.'),
                (10, 8, 29, 2, '외래경과기록', '2025-11-17'::DATE, '심장 상태 안정적. 운동능력 향상됨. 혈압 및 당뇨 조절 양호.'),
                (11, 1, 28, 1, '외래경과기록', '2025-11-17'::DATE, '당뇨병 정기 추적관찰. 혈당 조절 양호. 중성지방 수치 개선됨. 혈압도 안정적으로 유지되고 있음.'),
                (12, 1, 36, 1, '입원경과기록', '2025-11-15'::DATE, '당뇨병 급성 악화로 응급 입원. 혈당 수치 급격히 상승하여 인슐린 집중치료 시작.'),
                (13, 1, 36, 1, '입원경과기록', '2025-11-16'::DATE, '인슐린 치료 후 혈당 안정화. 중성지방 및 콜레스테롤 수치 모니터링 중. 혈압 정상 범위 유지.'),
                (14, 1, 36, 1, '퇴원요약', '2025-11-18'::DATE, '혈당 조절 목표치 달성하여 퇴원. 지속적인 외래 추적관찰 필요.')
            ) AS t(record_key, patient_key, visit_key, dept_key, record_type, record_date, record_content)
        """)
        
        # Create prescription table
        conn.execute("""
            CREATE TABLE fact_prescription AS
            SELECT * FROM (VALUES
                (1, 1, 1, '메트포르민', '당뇨병 치료제', 1000, 'mg', 2, 90, '2023-01-15'::DATE, '2023-04-15'::DATE),
                (2, 1, 1, '아토르바스타틴', '고지혈증 치료제', 20, 'mg', 1, 90, '2023-01-15'::DATE, '2023-04-15'::DATE),
                (3, 1, 7, '메트포르민', '당뇨병 치료제', 1000, 'mg', 2, 90, '2023-07-15'::DATE, '2023-10-15'::DATE),
                (4, 2, 2, '암로디핀', '고혈압 치료제', 5, 'mg', 1, 30, '2023-02-20'::DATE, '2023-03-22'::DATE),
                (5, 8, 8, '아스피린', '항혈전제', 100, 'mg', 1, 30, '2025-01-10'::DATE, '2025-02-09'::DATE),
                (6, 8, 8, '메토프롤롤', '베타차단제', 50, 'mg', 2, 30, '2025-01-10'::DATE, '2025-02-09'::DATE),
                (7, 8, 9, '아스피린', '항혈전제', 100, 'mg', 1, 90, '2025-02-15'::DATE, '2025-05-15'::DATE),
                (8, 9, 12, '로사르탄', '고혈압 치료제', 50, 'mg', 1, 7, '2025-11-01'::DATE, '2025-11-08'::DATE),
                (9, 9, 12, '푸로세미드', '이뇨제', 40, 'mg', 1, 7, '2025-11-01'::DATE, '2025-11-08'::DATE),
                (10, 10, 13, '니페디핀', '칼슘차단제', 30, 'mg', 2, 7, '2025-11-02'::DATE, '2025-11-09'::DATE),
                (11, 11, 14, '암로디핀', '고혈압 치료제', 10, 'mg', 1, 3, '2025-11-03'::DATE, '2025-11-06'::DATE),
                (12, 16, 23, '암로디핀', '고혈압 치료제', 5, 'mg', 1, 30, '2025-11-08'::DATE, '2025-12-08'::DATE),
                (13, 16, 30, '로사르탄', '고혈압 치료제', 50, 'mg', 1, 7, '2025-10-15'::DATE, '2025-10-22'::DATE),
                (14, 18, 25, '암로디핀', '고혈압 치료제', 10, 'mg', 1, 30, '2025-11-11'::DATE, '2025-12-11'::DATE),
                (15, 18, 31, '니페디핀', '칼슘차단제', 30, 'mg', 2, 7, '2025-10-20'::DATE, '2025-10-27'::DATE),
                (16, 8, 29, '아스피린', '항혈전제', 100, 'mg', 1, 90, '2025-11-17'::DATE, '2026-02-15'::DATE),
                (17, 2, 16, '메트포르민', '당뇨병 치료제', 1000, 'mg', 2, 90, '2025-11-10'::DATE, '2026-02-08'::DATE)
            ) AS t(prescription_key, patient_key, visit_key, medication_name, medication_category, dosage, unit, frequency_per_day, duration_days, start_date, end_date)
        """)
    
    def _generate_result_explanation(self, results: List[Dict], columns: List[str]) -> str:
        """Generate natural language explanation of query results"""
        if not results:
            return "쿼리 결과가 없습니다."
        
        if len(results) == 1 and len(columns) == 1:
            # Single value result
            return f"결과: {results[0][columns[0]]}"
        
        return f"총 {len(results)}개의 결과가 조회되었습니다."
    
    async def get_query_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent query history"""
        return self.query_history[-limit:][::-1]  # Return most recent first
    
    async def enhance_medical_prompt(
        self,
        question: str,
        enhancement_type: str = "medical"
    ) -> Dict[str, Any]:
        """의료 질의를 구조화된 프롬프트로 강화"""
        
        if not self.llm:
            # Fallback to rule-based enhancement
            return self._enhance_prompt_rule_based(question)
        
        # 의료 도메인 특화 프롬프트 강화
        enhancement_prompt = f"""
        당신은 의료 정보 시스템 전문가입니다.
        사용자가 입력한 간단한 의료 질의를 더 구체적이고 정확한 의료 용어를 사용하여 질문 형태로 강화해주세요.
        
        강화 규칙:
        1. 반드시 질문 형태로 변환 (끝에 "알려주세요", "보여주세요", "조회해주세요" 등)
        2. 환자명 → "환자이름이 [이름]인"
        3. 진료과 → "진료과가 [과명]인"
        4. 질병명을 의학 용어로 구체화
        5. 검사명을 정확한 의학 용어로 변환
        6. 기간/시점을 명확히 명시
        7. 데이터 유형을 구체화 (예: 진료기록 → 입원경과기록)
        8. vital sign 등 의학 용어 사용
        
        변환 예시:
        - "홍길동 환자" → "환자이름이 홍길동인"
        - "내분비내과와 연계된" → "진료과가 내분비내과와 연계된"
        - "당뇨 경과기록" → "당뇨병 관련 입원경과기록"
        - "TG 및 콜레스테롤 검사" → "검사명이 중성지방 및 콜레스테롤인 검사"
        - "혈압, 맥박 정보" → "vital sign 혈압, 맥박 정보"
        - "경과기록" → "입원경과기록"
        - "보여줘" → "조회해주세요"
        - "알려줘" → "알려주세요"
        
        원본 질의: {question}
        
        강화된 질의를 한국어 질문 형태로 작성해주세요. 원본의 의미는 유지하되, 의료진이 사용할 정확한 용어로 구체화하고 반드시 정중한 질문 형태로 만들어주세요.
        강화된 질의만 답변하고 다른 설명은 하지 마세요.
        """
        
        try:
            response = self.llm.invoke(enhancement_prompt)
            enhanced_question = response.content.strip() if hasattr(response, 'content') else str(response).strip()
            
            # 강화 사항 분석
            enhancements_applied = self._analyze_enhancements(question, enhanced_question)
            
            # 신뢰도 계산 (단어 수 증가, 의학 용어 포함 등을 기준)
            confidence = self._calculate_enhancement_confidence(question, enhanced_question)
            
            return {
                "original_question": question,
                "enhanced_question": enhanced_question,
                "enhancements_applied": enhancements_applied,
                "confidence": confidence
            }
        except Exception as e:
            print(f"⚠️ LLM prompt enhancement failed: {e}")
            return self._enhance_prompt_rule_based(question)
    
    def _enhance_prompt_rule_based(self, question: str) -> Dict[str, Any]:
        """규칙 기반 프롬프트 강화"""
        enhanced = question
        enhancements = []
        
        # 기본적인 의료 용어 매핑
        medical_mappings = {
            "TG": "중성지방",
            "콜레스테롤": "콜레스테롤",
            "혈압": "vital sign 혈압",
            "맥박": "vital sign 맥박",
            "당뇨": "당뇨병",
            "경과기록": "입원경과기록"
        }
        
        for original, enhanced_term in medical_mappings.items():
            if original in enhanced and enhanced_term not in enhanced:
                enhanced = enhanced.replace(original, enhanced_term)
                enhancements.append(f"의학용어 강화: {original} → {enhanced_term}")
        
        # 환자명 패턴 강화
        import re
        patient_pattern = r"([가-힣]+)\s*환자"
        match = re.search(patient_pattern, enhanced)
        if match:
            patient_name = match.group(1)
            enhanced = re.sub(patient_pattern, f"환자이름이 {patient_name}인", enhanced)
            enhancements.append(f"환자명 구조화: {patient_name} 환자 → 환자이름이 {patient_name}인")
        
        # 질문 형태로 변환
        casual_endings = ["보여줘", "알려줘", "줘", "해줘"]
        formal_endings = ["보여주세요", "알려주세요", "주세요", "해주세요"]
        
        for i, casual in enumerate(casual_endings):
            if enhanced.endswith(casual):
                enhanced = enhanced[:-len(casual)] + formal_endings[i]
                enhancements.append(f"정중한 질문 형태로 변환: {casual} → {formal_endings[i]}")
                break
        else:
            # 질문 형태가 아닌 경우 질문으로 변환
            if not any(enhanced.endswith(ending) for ending in ["주세요", "까요?", "인가요?"]):
                enhanced = enhanced.rstrip(".") + "을 조회해주세요"
                enhancements.append("질문 형태로 변환")
        
        confidence = 0.6 if enhancements else 0.3
        
        return {
            "original_question": question,
            "enhanced_question": enhanced,
            "enhancements_applied": enhancements,
            "confidence": confidence
        }
    
    def _analyze_enhancements(self, original: str, enhanced: str) -> List[str]:
        """강화 사항 분석"""
        enhancements = []
        
        # 길이 증가 확인
        if len(enhanced) > len(original):
            enhancements.append("질의 구체화")
        
        # 의학 용어 포함 확인
        medical_terms = ["환자이름이", "진료과가", "vital sign", "입원경과기록", "중성지방", "검사명이"]
        for term in medical_terms:
            if term in enhanced and term not in original:
                enhancements.append(f"의학용어 추가: {term}")
        
        return enhancements
    
    def _calculate_enhancement_confidence(self, original: str, enhanced: str) -> float:
        """강화 신뢰도 계산"""
        # 기본 신뢰도
        confidence = 0.5
        
        # 길이 기반 신뢰도
        length_ratio = len(enhanced) / len(original) if len(original) > 0 else 1
        if length_ratio > 1.2:  # 20% 이상 증가
            confidence += 0.2
        
        # 의학 용어 포함도
        medical_terms = ["환자이름이", "진료과가", "vital sign", "입원경과기록", "중성지방", "검사명이"]
        medical_term_count = sum(1 for term in medical_terms if term in enhanced)
        confidence += min(medical_term_count * 0.1, 0.3)
        
        return min(confidence, 0.95)  # 최대 0.95