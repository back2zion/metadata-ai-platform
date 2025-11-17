"""
Medical Test Data Fixtures
의료 도메인 테스트 데이터 생성기
"""
import factory
from datetime import datetime, date
from typing import List, Dict, Any
from factory import Faker, LazyAttribute, Sequence


class PatientFactory(factory.Factory):
    """환자 데이터 팩토리"""
    
    class Meta:
        model = dict
    
    patient_id = Sequence(lambda n: f"P{n:06d}")
    age = factory.Faker('random_int', min=18, max=90)
    gender = factory.Faker('random_element', elements=['M', 'F'])
    blood_type = factory.Faker('random_element', elements=['A', 'B', 'O', 'AB'])
    region = factory.Faker('random_element', elements=['서울', '경기', '부산', '대구', '인천'])
    registered_date = factory.Faker('date_between', start_date='-5y', end_date='today')


class DiagnosisFactory(factory.Factory):
    """진단 데이터 팩토리"""
    
    class Meta:
        model = dict
    
    kcd_code = factory.Faker('random_element', elements=[
        'E11', 'E119', 'I10', 'I109',  # 당뇨병, 고혈압
        'C50', 'C509', 'J45', 'J459',  # 유방암, 천식
        'K29', 'K299', 'N18', 'N189'   # 위염, 만성신부전
    ])
    diagnosis_name = LazyAttribute(lambda obj: {
        'E11': '2형 당뇨병',
        'E119': '2형 당뇨병, 상세불명',
        'I10': '본태성 고혈압',
        'I109': '본태성 고혈압, 상세불명',
        'C50': '유방의 악성신생물',
        'C509': '유방의 악성신생물, 상세불명',
        'J45': '천식',
        'J459': '천식, 상세불명',
        'K29': '위염 및 십이지장염',
        'K299': '위염, 상세불명',
        'N18': '만성 신장병',
        'N189': '만성 신장병, 상세불명'
    }.get(obj.kcd_code, '기타 질환'))
    
    category = LazyAttribute(lambda obj: {
        'E': '내분비, 영양 및 대사 질환',
        'I': '순환계통의 질환',
        'C': '신생물',
        'J': '호흡계통의 질환',
        'K': '소화계통의 질환',
        'N': '비뇨생식계통의 질환'
    }.get(obj.kcd_code[0], '기타'))


class MedicalVisitFactory(factory.Factory):
    """진료 방문 데이터 팩토리"""
    
    class Meta:
        model = dict
    
    visit_id = Sequence(lambda n: f"V{n:08d}")
    patient_key = factory.Faker('random_int', min=1, max=1000)
    diagnosis_key = factory.Faker('random_int', min=1, max=100)
    visit_date = factory.Faker('date_between', start_date='-2y', end_date='today')
    visit_type = factory.Faker('random_element', elements=['외래', '입원', '응급'])
    department = factory.Faker('random_element', elements=[
        '내과', '외과', '소아과', '산부인과', '정형외과',
        '신경과', '정신과', '피부과', '안과', '이비인후과'
    ])
    length_of_stay = factory.LazyAttribute(
        lambda obj: factory.Faker('random_int', min=1, max=30).generate() 
        if obj.visit_type == '입원' else 0
    )
    total_cost = factory.Faker('random_int', min=50000, max=5000000)


class LabResultFactory(factory.Factory):
    """검사 결과 데이터 팩토리"""
    
    class Meta:
        model = dict
    
    result_id = Sequence(lambda n: f"L{n:08d}")
    patient_key = factory.Faker('random_int', min=1, max=1000)
    test_code = factory.Faker('random_element', elements=[
        'HbA1c', 'FBG', 'PP2', 'TC', 'TG', 'HDL', 'LDL',
        'BUN', 'Cr', 'eGFR', 'AST', 'ALT', 'ALP'
    ])
    test_name = LazyAttribute(lambda obj: {
        'HbA1c': '당화혈색소',
        'FBG': '공복혈당',
        'PP2': '식후2시간혈당',
        'TC': '총콜레스테롤',
        'TG': '중성지방',
        'HDL': 'HDL콜레스테롤',
        'LDL': 'LDL콜레스테롤',
        'BUN': '혈중요소질소',
        'Cr': '크레아티닌',
        'eGFR': '추정사구체여과율',
        'AST': 'AST',
        'ALT': 'ALT',
        'ALP': 'ALP'
    }.get(obj.test_code, obj.test_code))
    
    result_value = LazyAttribute(lambda obj: {
        'HbA1c': factory.Faker('random_int', min=50, max=120).generate() / 10,  # 5.0-12.0%
        'FBG': factory.Faker('random_int', min=70, max=200).generate(),         # 70-200 mg/dL
        'PP2': factory.Faker('random_int', min=100, max=300).generate(),        # 100-300 mg/dL
        'TC': factory.Faker('random_int', min=150, max=300).generate(),         # 150-300 mg/dL
        'TG': factory.Faker('random_int', min=50, max=400).generate(),          # 50-400 mg/dL
        'HDL': factory.Faker('random_int', min=30, max=80).generate(),          # 30-80 mg/dL
        'LDL': factory.Faker('random_int', min=70, max=200).generate(),         # 70-200 mg/dL
        'BUN': factory.Faker('random_int', min=8, max=25).generate(),           # 8-25 mg/dL
        'Cr': factory.Faker('random_int', min=60, max=150).generate() / 100,    # 0.6-1.5 mg/dL
        'eGFR': factory.Faker('random_int', min=30, max=120).generate(),        # 30-120 mL/min/1.73m²
        'AST': factory.Faker('random_int', min=10, max=100).generate(),         # 10-100 U/L
        'ALT': factory.Faker('random_int', min=10, max=100).generate(),         # 10-100 U/L
        'ALP': factory.Faker('random_int', min=40, max=150).generate()          # 40-150 U/L
    }.get(obj.test_code, factory.Faker('random_int', min=1, max=100).generate()))
    
    result_unit = LazyAttribute(lambda obj: {
        'HbA1c': '%',
        'FBG': 'mg/dL', 'PP2': 'mg/dL',
        'TC': 'mg/dL', 'TG': 'mg/dL', 'HDL': 'mg/dL', 'LDL': 'mg/dL',
        'BUN': 'mg/dL', 'Cr': 'mg/dL',
        'eGFR': 'mL/min/1.73m²',
        'AST': 'U/L', 'ALT': 'U/L', 'ALP': 'U/L'
    }.get(obj.test_code, 'unit'))
    
    test_date = factory.Faker('date_between', start_date='-1y', end_date='today')


class MedicalQueryFactory(factory.Factory):
    """의료 질의 데이터 팩토리"""
    
    class Meta:
        model = dict
    
    question = factory.Faker('random_element', elements=[
        "당뇨병 환자 수를 알려주세요",
        "고혈압 환자의 평균 연령은?",
        "최근 6개월간 입원 환자 수는?",
        "심혈관내과 외래 환자 수는?",
        "HbA1c 7.0 이상인 당뇨병 환자 비율은?",
        "지역별 환자 분포를 보여주세요",
        "가장 많이 진단되는 질병은?",
        "평균 재원일수가 가장 긴 진료과는?"
    ])
    
    expected_sql = LazyAttribute(lambda obj: {
        "당뇨병 환자 수를 알려주세요": "SELECT COUNT(DISTINCT patient_key) FROM fact_medical_visit fv JOIN dim_diagnosis dd ON fv.diagnosis_key = dd.diagnosis_key WHERE dd.kcd_code LIKE 'E11%'",
        "고혈압 환자의 평균 연령은?": "SELECT AVG(dp.age) FROM dim_patient dp JOIN fact_medical_visit fv ON dp.patient_key = fv.patient_key JOIN dim_diagnosis dd ON fv.diagnosis_key = dd.diagnosis_key WHERE dd.kcd_code LIKE 'I10%'",
        "최근 6개월간 입원 환자 수는?": "SELECT COUNT(DISTINCT patient_key) FROM fact_medical_visit WHERE visit_type = '입원' AND visit_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)",
        "심혈관내과 외래 환자 수는?": "SELECT COUNT(DISTINCT patient_key) FROM fact_medical_visit WHERE department = '심혈관내과' AND visit_type = '외래'",
        "HbA1c 7.0 이상인 당뇨병 환자 비율은?": "SELECT (COUNT(CASE WHEN flr.result_value >= 7.0 THEN 1 END) * 100.0 / COUNT(*)) as percentage FROM fact_lab_result flr WHERE flr.test_code = 'HbA1c'",
        "지역별 환자 분포를 보여주세요": "SELECT dp.region, COUNT(DISTINCT dp.patient_key) as patient_count FROM dim_patient dp GROUP BY dp.region ORDER BY patient_count DESC",
        "가장 많이 진단되는 질병은?": "SELECT dd.diagnosis_name, COUNT(*) as diagnosis_count FROM dim_diagnosis dd JOIN fact_medical_visit fv ON dd.diagnosis_key = fv.diagnosis_key GROUP BY dd.diagnosis_name ORDER BY diagnosis_count DESC LIMIT 1",
        "평균 재원일수가 가장 긴 진료과는?": "SELECT department, AVG(length_of_stay) as avg_los FROM fact_medical_visit WHERE visit_type = '입원' GROUP BY department ORDER BY avg_los DESC LIMIT 1"
    }.get(obj.question, "SELECT COUNT(*) FROM fact_medical_visit"))
    
    confidence = factory.Faker('random_int', min=70, max=95) / 100
    risk_level = factory.Faker('random_element', elements=['low', 'medium', 'high'])


# 의료 데이터 생성 헬퍼 함수들
def create_sample_medical_dataset(
    patient_count: int = 100,
    diagnosis_count: int = 20,
    visit_count: int = 500,
    lab_result_count: int = 1000
) -> Dict[str, List[Dict[str, Any]]]:
    """완전한 의료 데이터셋 생성"""
    
    return {
        "patients": PatientFactory.create_batch(patient_count),
        "diagnoses": DiagnosisFactory.create_batch(diagnosis_count),
        "visits": MedicalVisitFactory.create_batch(visit_count),
        "lab_results": LabResultFactory.create_batch(lab_result_count)
    }


def create_diabetes_patient_scenario() -> Dict[str, Any]:
    """당뇨병 환자 시나리오 데이터"""
    patient = PatientFactory.create(age=55, gender='M')
    diagnosis = DiagnosisFactory.create(kcd_code='E119', diagnosis_name='2형 당뇨병')
    visit = MedicalVisitFactory.create(
        visit_type='외래',
        department='내분비내과'
    )
    hba1c_result = LabResultFactory.create(
        test_code='HbA1c',
        result_value=8.5,  # 높은 수치
        result_unit='%'
    )
    
    return {
        "patient": patient,
        "diagnosis": diagnosis,
        "visit": visit,
        "lab_result": hba1c_result,
        "scenario": "poorly_controlled_diabetes"
    }


def create_hypertension_patient_scenario() -> Dict[str, Any]:
    """고혈압 환자 시나리오 데이터"""
    patient = PatientFactory.create(age=62, gender='F')
    diagnosis = DiagnosisFactory.create(kcd_code='I109', diagnosis_name='본태성 고혈압')
    visit = MedicalVisitFactory.create(
        visit_type='외래',
        department='심혈관내과'
    )
    
    return {
        "patient": patient,
        "diagnosis": diagnosis,
        "visit": visit,
        "scenario": "hypertension_management"
    }


def create_emergency_visit_scenario() -> Dict[str, Any]:
    """응급실 내원 시나리오 데이터"""
    patient = PatientFactory.create(age=78)
    visit = MedicalVisitFactory.create(
        visit_type='응급',
        department='응급의학과',
        total_cost=2500000
    )
    
    return {
        "patient": patient,
        "visit": visit,
        "scenario": "emergency_visit"
    }


# Test Query Templates
MEDICAL_TEST_QUERIES = [
    {
        "name": "diabetes_patient_count",
        "question": "당뇨병 환자 수를 알려주세요",
        "expected_sql_pattern": r"SELECT.*COUNT.*diabetes|E11",
        "expected_result_type": "count"
    },
    {
        "name": "hypertension_age_analysis",
        "question": "고혈압 환자의 평균 연령은?",
        "expected_sql_pattern": r"SELECT.*AVG.*age.*hypertension|I10",
        "expected_result_type": "average"
    },
    {
        "name": "recent_admissions",
        "question": "최근 3개월간 입원 환자 수는?",
        "expected_sql_pattern": r"SELECT.*COUNT.*입원.*INTERVAL.*MONTH",
        "expected_result_type": "count"
    },
    {
        "name": "department_analysis",
        "question": "진료과별 환자 수를 보여주세요",
        "expected_sql_pattern": r"SELECT.*department.*COUNT.*GROUP BY",
        "expected_result_type": "group_by"
    }
]