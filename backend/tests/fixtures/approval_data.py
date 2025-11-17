"""
HumanLayer Approval Test Data Fixtures
승인 워크플로우 테스트 데이터 생성기
"""
import factory
from datetime import datetime, timedelta
from typing import List, Dict, Any
from factory import Faker, LazyAttribute, Sequence
import uuid


class ApprovalRequestFactory(factory.Factory):
    """승인 요청 데이터 팩토리"""
    
    class Meta:
        model = dict
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    type = factory.Faker('random_element', elements=[
        'sql_execution', 'data_export', 'model_deployment',
        'patient_data_access', 'research_query'
    ])
    
    title = LazyAttribute(lambda obj: {
        'sql_execution': 'SQL 쿼리 실행 승인',
        'data_export': '데이터 내보내기 승인',
        'model_deployment': '모델 배포 승인',
        'patient_data_access': '환자 데이터 접근 승인',
        'research_query': '연구용 쿼리 승인'
    }.get(obj.type, 'AI 작업 승인'))
    
    description = LazyAttribute(lambda obj: {
        'sql_execution': f'{obj.requester}님이 의료 데이터베이스 쿼리 실행을 요청했습니다.',
        'data_export': f'{obj.requester}님이 분석 결과 데이터 내보내기를 요청했습니다.',
        'model_deployment': f'{obj.requester}님이 AI 모델 배포를 요청했습니다.',
        'patient_data_access': f'{obj.requester}님이 환자 개인정보 접근을 요청했습니다.',
        'research_query': f'{obj.requester}님이 연구목적 데이터 조회를 요청했습니다.'
    }.get(obj.type, f'{obj.requester}님이 AI 작업을 요청했습니다.'))
    
    requester = factory.Faker('random_element', elements=[
        'dr.kim', 'researcher.lee', 'analyst.park', 'admin.choi', 'nurse.jung'
    ])
    
    risk_level = factory.Faker('random_element', elements=['low', 'medium', 'high', 'critical'])
    
    priority = LazyAttribute(lambda obj: {
        'critical': 'urgent',
        'high': 'high',
        'medium': 'medium',
        'low': 'low'
    }.get(obj.risk_level, 'medium'))
    
    status = factory.Faker('random_element', elements=[
        'pending', 'approved', 'rejected', 'expired', 'cancelled'
    ])
    
    created_at = factory.Faker('date_time_between', start_date='-7d', end_date='now')
    updated_at = LazyAttribute(lambda obj: obj.created_at + timedelta(minutes=factory.Faker('random_int', min=1, max=1440).generate()))
    expires_at = LazyAttribute(lambda obj: obj.created_at + timedelta(hours=24))  # 24시간 후 만료
    
    metadata = factory.LazyAttribute(lambda obj: {
        'sql_execution': {
            'sql': obj.sql_query if hasattr(obj, 'sql_query') else 'SELECT COUNT(*) FROM patients',
            'database': 'medical_dw',
            'estimated_rows': factory.Faker('random_int', min=1, max=10000).generate(),
            'contains_pii': factory.Faker('boolean').generate()
        },
        'data_export': {
            'format': factory.Faker('random_element', elements=['CSV', 'JSON', 'Excel']).generate(),
            'destination': 'secure_folder',
            'row_count': factory.Faker('random_int', min=100, max=5000).generate()
        },
        'model_deployment': {
            'model_name': f'medical_ai_v{factory.Faker("random_int", min=1, max=10).generate()}',
            'accuracy': factory.Faker('random_int', min=85, max=98).generate() / 100,
            'environment': 'production'
        }
    }.get(obj.type, {}))


class ApprovalDecisionFactory(factory.Factory):
    """승인 결정 데이터 팩토리"""
    
    class Meta:
        model = dict
    
    request_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    approver = factory.Faker('random_element', elements=[
        'supervisor.kim', 'chief.lee', 'admin.park', 'security.officer'
    ])
    decision = factory.Faker('random_element', elements=['approved', 'rejected'])
    reason = LazyAttribute(lambda obj: {
        'approved': factory.Faker('random_element', elements=[
            '요청이 적절하고 보안 기준을 충족합니다.',
            '의료진의 정당한 업무 요청입니다.',
            '연구 목적이 명확하고 IRB 승인이 있습니다.',
            '데이터 보호 조치가 충분합니다.'
        ]).generate(),
        'rejected': factory.Faker('random_element', elements=[
            '보안 위험이 너무 높습니다.',
            '개인정보 보호 정책에 위반됩니다.',
            '요청 사유가 불분명합니다.',
            'IRB 승인이 필요합니다.',
            '권한이 부족합니다.'
        ]).generate()
    }.get(obj.decision, '기타'))
    
    decided_at = factory.Faker('date_time_between', start_date='-3d', end_date='now')
    conditions = LazyAttribute(lambda obj: [
        '30분 내 실행 완료',
        '결과 데이터 7일 후 자동 삭제',
        '접근 로그 실시간 모니터링'
    ] if obj.decision == 'approved' else [])


class AITaskFactory(factory.Factory):
    """AI 작업 데이터 팩토리"""
    
    class Meta:
        model = dict
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    type = factory.Faker('random_element', elements=[
        'text2sql', 'data_analysis', 'model_inference', 
        'report_generation', 'anomaly_detection'
    ])
    
    description = LazyAttribute(lambda obj: {
        'text2sql': '자연어를 SQL로 변환',
        'data_analysis': '의료 데이터 통계 분석',
        'model_inference': 'AI 모델 추론 실행',
        'report_generation': '분석 보고서 생성',
        'anomaly_detection': '이상치 탐지 분석'
    }.get(obj.type, 'AI 작업'))
    
    input_data = LazyAttribute(lambda obj: {
        'text2sql': {
            'question': '당뇨병 환자 수를 알려주세요',
            'schema_context': 'medical_database'
        },
        'data_analysis': {
            'dataset': 'patient_demographics',
            'analysis_type': 'descriptive_statistics'
        },
        'model_inference': {
            'model_id': 'diabetes_risk_model_v2',
            'input_features': ['age', 'bmi', 'family_history']
        }
    }.get(obj.type, {}))
    
    status = factory.Faker('random_element', elements=[
        'pending_approval', 'approved', 'running', 'completed', 'failed', 'cancelled'
    ])
    
    created_by = factory.Faker('random_element', elements=[
        'system', 'user_request', 'scheduled_task', 'api_client'
    ])
    
    estimated_duration = factory.Faker('random_int', min=30, max=3600)  # seconds
    actual_duration = factory.LazyAttribute(
        lambda obj: factory.Faker('random_int', min=obj.estimated_duration//2, 
                                 max=obj.estimated_duration*2).generate() 
        if obj.status == 'completed' else None
    )
    
    created_at = factory.Faker('date_time_between', start_date='-2d', end_date='now')
    started_at = LazyAttribute(
        lambda obj: obj.created_at + timedelta(minutes=factory.Faker('random_int', min=1, max=60).generate()) 
        if obj.status in ['running', 'completed', 'failed'] else None
    )
    completed_at = LazyAttribute(
        lambda obj: obj.started_at + timedelta(seconds=obj.actual_duration) 
        if obj.status == 'completed' and obj.started_at and obj.actual_duration else None
    )


class HumanLayerSessionFactory(factory.Factory):
    """HumanLayer 세션 데이터 팩토리"""
    
    class Meta:
        model = dict
    
    session_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    user_id = factory.Faker('random_element', elements=[
        'medical_staff_001', 'researcher_002', 'admin_003', 'analyst_004'
    ])
    
    session_type = factory.Faker('random_element', elements=[
        'approval_review', 'task_monitoring', 'system_admin', 'data_exploration'
    ])
    
    status = factory.Faker('random_element', elements=[
        'active', 'idle', 'expired', 'terminated'
    ])
    
    created_at = factory.Faker('date_time_between', start_date='-1d', end_date='now')
    last_activity = LazyAttribute(
        lambda obj: obj.created_at + timedelta(minutes=factory.Faker('random_int', min=1, max=120).generate())
    )
    expires_at = LazyAttribute(lambda obj: obj.created_at + timedelta(hours=8))  # 8시간 세션
    
    permissions = factory.LazyAttribute(lambda obj: {
        'medical_staff_001': ['view_patient_data', 'approve_low_risk', 'execute_queries'],
        'researcher_002': ['view_anonymized_data', 'run_analysis', 'export_results'],
        'admin_003': ['approve_all_requests', 'manage_users', 'system_config'],
        'analyst_004': ['view_reports', 'create_dashboards', 'approve_medium_risk']
    }.get(obj.user_id, ['basic_access']))
    
    activity_log = factory.LazyAttribute(lambda obj: [
        {
            'timestamp': obj.created_at.isoformat(),
            'action': 'session_started',
            'details': f'User {obj.user_id} logged in'
        },
        {
            'timestamp': obj.last_activity.isoformat(),
            'action': 'approval_reviewed',
            'details': 'Reviewed SQL execution request'
        }
    ])


# 승인 워크플로우 시나리오 데이터
def create_sql_execution_approval_scenario() -> Dict[str, Any]:
    """SQL 실행 승인 시나리오"""
    request = ApprovalRequestFactory.create(
        type='sql_execution',
        risk_level='medium',
        status='pending',
        metadata={
            'sql': "SELECT p.age, d.diagnosis_name, COUNT(*) as patient_count FROM dim_patient p JOIN fact_medical_visit v ON p.patient_key = v.patient_key JOIN dim_diagnosis d ON v.diagnosis_key = d.diagnosis_key WHERE p.age > 65 GROUP BY p.age, d.diagnosis_name ORDER BY patient_count DESC",
            'database': 'medical_dw',
            'estimated_rows': 1500,
            'contains_pii': False,
            'purpose': '노인 환자 질병 분포 분석'
        }
    )
    
    return {
        'request': request,
        'scenario_name': 'elderly_patient_analysis',
        'expected_approval_time': 300,  # 5 minutes
        'required_approver_level': 'supervisor'
    }


def create_high_risk_approval_scenario() -> Dict[str, Any]:
    """고위험 승인 시나리오"""
    request = ApprovalRequestFactory.create(
        type='patient_data_access',
        risk_level='high',
        status='pending',
        metadata={
            'data_type': 'patient_identifiable_information',
            'purpose': '특정 환자 치료 이력 조회',
            'patient_count': 1,
            'contains_pii': True,
            'irb_approval': 'IRB-2024-001'
        }
    )
    
    return {
        'request': request,
        'scenario_name': 'pii_access_request',
        'expected_approval_time': 1800,  # 30 minutes
        'required_approver_level': 'chief_medical_officer',
        'additional_requirements': ['irb_documentation', 'patient_consent']
    }


def create_batch_approval_scenario(count: int = 5) -> Dict[str, Any]:
    """배치 승인 시나리오"""
    requests = [
        ApprovalRequestFactory.create(
            type='research_query',
            risk_level='low',
            status='pending'
        ) for _ in range(count)
    ]
    
    return {
        'requests': requests,
        'scenario_name': 'batch_research_approvals',
        'total_requests': count,
        'expected_batch_approval_time': 600,  # 10 minutes for all
        'approval_strategy': 'bulk_approve_low_risk'
    }


def create_expired_approval_scenario() -> Dict[str, Any]:
    """만료된 승인 시나리오"""
    past_time = datetime.now() - timedelta(days=2)
    request = ApprovalRequestFactory.create(
        status='expired',
        created_at=past_time,
        expires_at=past_time + timedelta(hours=24)
    )
    
    return {
        'request': request,
        'scenario_name': 'expired_approval',
        'expiry_reason': 'no_response_within_24_hours',
        'follow_up_action': 'notify_requester'
    }


# 승인 워크플로우 테스트 케이스
APPROVAL_TEST_CASES = [
    {
        'name': 'simple_sql_approval',
        'request_type': 'sql_execution',
        'risk_level': 'low',
        'expected_decision': 'approved',
        'expected_time_seconds': 60
    },
    {
        'name': 'pii_data_access',
        'request_type': 'patient_data_access',
        'risk_level': 'high',
        'expected_decision': 'requires_additional_approval',
        'expected_time_seconds': 1800
    },
    {
        'name': 'research_data_export',
        'request_type': 'data_export',
        'risk_level': 'medium',
        'expected_decision': 'conditional_approval',
        'expected_time_seconds': 300
    },
    {
        'name': 'emergency_query',
        'request_type': 'sql_execution',
        'risk_level': 'medium',
        'priority': 'urgent',
        'expected_decision': 'fast_track_approval',
        'expected_time_seconds': 30
    }
]


# Mock HumanLayer API Responses
MOCK_HUMANLAYER_RESPONSES = {
    'create_approval_success': {
        'status': 200,
        'data': {
            'id': 'hl_approval_123',
            'status': 'pending',
            'created_at': '2024-01-15T10:30:00Z',
            'expires_at': '2024-01-16T10:30:00Z'
        }
    },
    'approval_status_pending': {
        'status': 200,
        'data': {
            'id': 'hl_approval_123',
            'status': 'pending',
            'approver': None,
            'decision_at': None
        }
    },
    'approval_status_approved': {
        'status': 200,
        'data': {
            'id': 'hl_approval_123',
            'status': 'approved',
            'approver': 'supervisor.kim',
            'decision_at': '2024-01-15T10:35:00Z',
            'conditions': ['execute_within_30_minutes', 'log_all_queries']
        }
    },
    'approval_status_rejected': {
        'status': 200,
        'data': {
            'id': 'hl_approval_123',
            'status': 'rejected',
            'approver': 'security.officer',
            'decision_at': '2024-01-15T10:45:00Z',
            'reason': '보안 정책 위반: 개인정보 노출 위험'
        }
    }
}