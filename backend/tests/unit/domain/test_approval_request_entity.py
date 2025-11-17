"""
Unit Tests for Approval Request Entity (Domain Layer)
도메인 계층 - 승인 요청 엔티티 테스트

TDD 원칙에 따라 Red-Green-Refactor 사이클로 개발
"""
import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

from app.domain.entities.approval_request import (
    ApprovalRequest, ApprovalType, ApprovalStatus, Priority,
    ApprovalRequestExpiredError, InvalidApprovalStateError
)
from app.domain.value_objects.risk_level import RiskLevel


class TestApprovalRequestEntity:
    """Approval Request Entity 테스트 클래스"""
    
    @pytest.mark.unit
    def test_should_create_approval_request_with_valid_data(self, tdd_case):
        """
        TDD Case 1: 유효한 데이터로 승인 요청 생성
        
        Given: 유효한 승인 요청 정보가 주어졌을 때
        When: ApprovalRequest 엔티티를 생성하면
        Then: 올바른 속성을 가진 엔티티가 생성된다
        """
        tdd_case.given("유효한 승인 요청 데이터가 준비됨")
        
        # 테스트 데이터
        approval_type = ApprovalType.SQL_EXECUTION
        title = "SQL 쿼리 실행 승인"
        description = "환자 통계 데이터 조회를 위한 SQL 실행"
        requester_id = "dr.kim"
        risk_level = RiskLevel.from_factors(["select_query", "patient_data"])
        metadata = {"sql": "SELECT COUNT(*) FROM patients", "database": "medical_dw"}
        
        tdd_case.when("ApprovalRequest 엔티티를 생성함")
        
        approval_request = ApprovalRequest(
            approval_type=approval_type,
            title=title,
            description=description,
            requester_id=requester_id,
            risk_level=risk_level,
            metadata=metadata
        )
        
        tdd_case.then("올바른 속성을 가진 엔티티가 생성됨")
        
        assert approval_request.type == approval_type
        assert approval_request.title == title
        assert approval_request.description == description
        assert approval_request.requester_id == requester_id
        assert approval_request.risk_level == risk_level
        assert approval_request.metadata == metadata
        assert approval_request.status == ApprovalStatus.PENDING
        assert approval_request.priority == Priority.MEDIUM  # default
        assert approval_request.created_at is not None
        assert approval_request.expires_at > approval_request.created_at
        assert approval_request.decision is None
    
    @pytest.mark.unit
    def test_should_approve_pending_request(self, tdd_case):
        """
        TDD Case 2: 대기 중인 요청 승인
        
        Given: 대기 중인 승인 요청이 있을 때
        When: 승인 처리하면
        Then: 상태가 APPROVED로 변경되고 결정 정보가 저장된다
        """
        tdd_case.given("대기 중인 승인 요청이 준비됨")
        
        approval_request = self._create_sample_request()
        approver_id = "supervisor.lee"
        reason = "정당한 의료 데이터 조회 목적"
        conditions = ["30분 내 실행 완료", "결과 데이터 7일 후 삭제"]
        
        tdd_case.when("승인 처리함")
        
        approval_request.approve(
            approver_id=approver_id,
            reason=reason,
            conditions=conditions,
            execution_expires_in_minutes=30
        )
        
        tdd_case.then("승인 상태로 변경되고 결정 정보가 저장됨")
        
        assert approval_request.status == ApprovalStatus.APPROVED
        assert approval_request.decision is not None
        assert approval_request.decision.approved is True
        assert approval_request.decision.approver_id == approver_id
        assert approval_request.decision.reason == reason
        assert approval_request.decision.conditions == conditions
        assert approval_request.decision.expires_at is not None
        assert approval_request.is_approved() is True
    
    @pytest.mark.unit
    def test_should_reject_pending_request(self, tdd_case):
        """
        TDD Case 3: 대기 중인 요청 거부
        
        Given: 대기 중인 승인 요청이 있을 때
        When: 거부 처리하면
        Then: 상태가 REJECTED로 변경되고 거부 사유가 저장된다
        """
        tdd_case.given("대기 중인 승인 요청이 준비됨")
        
        approval_request = self._create_sample_request()
        approver_id = "security.officer"
        reason = "보안 정책 위반: 개인정보 노출 위험"
        
        tdd_case.when("거부 처리함")
        
        approval_request.reject(approver_id=approver_id, reason=reason)
        
        tdd_case.then("거부 상태로 변경되고 거부 사유가 저장됨")
        
        assert approval_request.status == ApprovalStatus.REJECTED
        assert approval_request.decision is not None
        assert approval_request.decision.approved is False
        assert approval_request.decision.approver_id == approver_id
        assert approval_request.decision.reason == reason
        assert approval_request.is_approved() is False
    
    @pytest.mark.unit
    def test_should_handle_expired_request(self, tdd_case):
        """
        TDD Case 4: 만료된 요청 처리
        
        Given: 만료 시간이 지난 승인 요청이 있을 때
        When: 만료 처리하면
        Then: 상태가 EXPIRED로 변경된다
        """
        tdd_case.given("만료 시간이 지난 승인 요청이 준비됨")
        
        # 이미 만료된 요청 생성 (과거 시간으로 설정)
        approval_request = ApprovalRequest(
            approval_type=ApprovalType.SQL_EXECUTION,
            title="만료된 요청",
            description="테스트용 만료 요청",
            requester_id="test.user",
            risk_level=RiskLevel.from_factors(["test"]),
            metadata={},
            expires_in_hours=-1  # 이미 만료됨
        )
        
        tdd_case.when("만료 처리함")
        
        approval_request.mark_expired()
        
        tdd_case.then("만료 상태로 변경됨")
        
        assert approval_request.status == ApprovalStatus.EXPIRED
        assert approval_request.is_expired() is True
        assert approval_request.is_pending() is False
        assert approval_request.get_remaining_time_minutes() == 0
    
    @pytest.mark.unit
    def test_should_prevent_approval_of_expired_request(self, tdd_case):
        """
        TDD Case 5: 만료된 요청 승인 방지
        
        Given: 만료된 승인 요청이 있을 때
        When: 승인 처리를 시도하면
        Then: ApprovalRequestExpiredError가 발생한다
        """
        tdd_case.given("만료된 승인 요청이 준비됨")
        
        # 만료된 요청 생성
        approval_request = ApprovalRequest(
            approval_type=ApprovalType.SQL_EXECUTION,
            title="만료된 요청",
            description="테스트용 만료 요청",
            requester_id="test.user",
            risk_level=RiskLevel.from_factors(["test"]),
            metadata={},
            expires_in_hours=-1  # 이미 만료됨
        )
        
        tdd_case.when("만료된 요청에 대해 승인 처리를 시도함")
        
        tdd_case.then("ApprovalRequestExpiredError가 발생함")
        
        with pytest.raises(ApprovalRequestExpiredError):
            approval_request.approve(
                approver_id="test.approver",
                reason="Should fail"
            )
    
    @pytest.mark.unit
    def test_should_prevent_double_approval(self, tdd_case):
        """
        TDD Case 6: 중복 승인 방지
        
        Given: 이미 승인된 요청이 있을 때
        When: 다시 승인 처리를 시도하면
        Then: InvalidApprovalStateError가 발생한다
        """
        tdd_case.given("이미 승인된 요청이 준비됨")
        
        approval_request = self._create_sample_request()
        approval_request.approve(approver_id="first.approver", reason="First approval")
        
        tdd_case.when("이미 승인된 요청에 대해 다시 승인 처리를 시도함")
        
        tdd_case.then("InvalidApprovalStateError가 발생함")
        
        with pytest.raises(InvalidApprovalStateError):
            approval_request.approve(
                approver_id="second.approver",
                reason="Should fail"
            )
    
    @pytest.mark.unit
    def test_should_determine_required_approver_level(self, tdd_case):
        """
        TDD Case 7: 필요한 승인자 레벨 결정
        
        Given: 다양한 위험도의 요청들이 있을 때
        When: 필요한 승인자 레벨을 확인하면
        Then: 위험도에 맞는 적절한 승인자 레벨이 결정된다
        """
        tdd_case.given("다양한 위험도의 요청들이 준비됨")
        
        test_cases = [
            {
                "risk_factors": ["select_query"],
                "expected_level": "supervisor",
                "description": "저위험 - supervisor 승인"
            },
            {
                "risk_factors": ["patient_data"],
                "expected_level": "manager",
                "description": "중위험 - manager 승인"
            },
            {
                "risk_factors": ["dangerous_keyword_delete", "pii_access_ssn"],
                "expected_level": "senior_manager",
                "description": "고위험 - senior_manager 승인"
            },
            {
                "risk_factors": ["dangerous_keyword_drop", "system_critical", "pii_access_name", "pii_access_ssn"],
                "expected_level": "chief_officer",
                "description": "최고위험 - chief_officer 승인"
            }
        ]
        
        tdd_case.when("각 위험도에 대해 필요한 승인자 레벨을 확인함")
        
        for case in test_cases:
            tdd_case.then(case["description"])
            
            risk_level = RiskLevel.from_factors(case["risk_factors"])
            approval_request = ApprovalRequest(
                approval_type=ApprovalType.SQL_EXECUTION,
                title="Test Request",
                description="Test",
                requester_id="test.user",
                risk_level=risk_level,
                metadata={}
            )
            
            assert approval_request.required_approver_level == case["expected_level"]
    
    @pytest.mark.unit
    def test_should_handle_urgent_priority_requests(self, tdd_case):
        """
        TDD Case 8: 긴급 우선순위 요청 처리
        
        Given: 긴급 우선순위 요청이 있을 때
        When: 긴급 주의 필요 여부를 확인하면
        Then: True가 반환된다
        """
        tdd_case.given("긴급 우선순위 요청이 준비됨")
        
        approval_request = ApprovalRequest(
            approval_type=ApprovalType.SQL_EXECUTION,
            title="긴급 요청",
            description="응급 상황 데이터 조회",
            requester_id="emergency.user",
            risk_level=RiskLevel.from_factors(["emergency_query"]),
            metadata={},
            priority=Priority.URGENT
        )
        
        tdd_case.when("긴급 주의 필요 여부를 확인함")
        
        urgent_attention = approval_request.requires_urgent_attention()
        
        tdd_case.then("긴급 주의가 필요하다고 반환됨")
        
        assert urgent_attention is True
        assert approval_request.priority == Priority.URGENT
    
    @pytest.mark.unit
    def test_should_cancel_pending_request(self, tdd_case):
        """
        TDD Case 9: 대기 중인 요청 취소
        
        Given: 대기 중인 승인 요청이 있을 때
        When: 요청을 취소하면
        Then: 상태가 CANCELLED로 변경된다
        """
        tdd_case.given("대기 중인 승인 요청이 준비됨")
        
        approval_request = self._create_sample_request()
        cancellation_reason = "더 이상 필요하지 않음"
        
        tdd_case.when("요청을 취소함")
        
        approval_request.cancel(reason=cancellation_reason)
        
        tdd_case.then("취소 상태로 변경됨")
        
        assert approval_request.status == ApprovalStatus.CANCELLED
        assert approval_request.metadata["cancellation_reason"] == cancellation_reason
    
    @pytest.mark.unit
    def test_should_generate_humanlayer_payload(self, tdd_case):
        """
        TDD Case 10: HumanLayer API 페이로드 생성
        
        Given: 승인 요청이 있을 때
        When: HumanLayer API 페이로드를 생성하면
        Then: 필요한 모든 정보가 포함된 페이로드가 생성된다
        """
        tdd_case.given("승인 요청이 준비됨")
        
        approval_request = self._create_sample_request()
        
        tdd_case.when("HumanLayer API 페이로드를 생성함")
        
        payload = approval_request.to_humanlayer_payload()
        
        tdd_case.then("필요한 모든 정보가 포함된 페이로드가 생성됨")
        
        # 필수 필드 확인
        assert "id" in payload
        assert "type" in payload
        assert "title" in payload
        assert "description" in payload
        assert "priority" in payload
        assert "metadata" in payload
        
        # 메타데이터 내용 확인
        metadata = payload["metadata"]
        assert "request_type" in metadata
        assert "requester_id" in metadata
        assert "risk_level" in metadata
        assert "required_approver_level" in metadata
        assert "expires_at" in metadata
        assert "remaining_minutes" in metadata
        assert "urgent" in metadata
        
        # 값 검증
        assert payload["id"] == approval_request.id
        assert payload["type"] == "approval_request"
        assert metadata["request_type"] == approval_request.type.value
        assert metadata["requester_id"] == approval_request.requester_id
    
    @pytest.mark.unit
    def test_should_track_execution_expiration(self, tdd_case):
        """
        TDD Case 11: 실행 만료 시간 추적
        
        Given: 승인된 요청이 있을 때
        When: 실행 만료 시간을 확인하면
        Then: 올바른 만료 상태가 반환된다
        """
        tdd_case.given("승인된 요청이 준비됨")
        
        approval_request = self._create_sample_request()
        approval_request.approve(
            approver_id="test.approver",
            reason="Test approval",
            execution_expires_in_minutes=60  # 60분 후 만료
        )
        
        tdd_case.when("실행 만료 시간을 확인함")
        
        # 처음에는 만료되지 않음
        assert approval_request.is_execution_expired() is False
        assert approval_request.get_execution_remaining_time_minutes() > 0
        
        # 만료 시간을 과거로 설정하여 만료 상태 시뮬레이션
        approval_request.decision.expires_at = datetime.utcnow() - timedelta(minutes=1)
        
        tdd_case.then("실행 만료 상태가 올바르게 반환됨")
        
        assert approval_request.is_execution_expired() is True
        assert approval_request.get_execution_remaining_time_minutes() == 0
    
    def _create_sample_request(self) -> ApprovalRequest:
        """테스트용 샘플 승인 요청 생성"""
        return ApprovalRequest(
            approval_type=ApprovalType.SQL_EXECUTION,
            title="테스트 SQL 실행",
            description="테스트용 SQL 쿼리 실행 요청",
            requester_id="test.user",
            risk_level=RiskLevel.from_factors(["select_query", "patient_data"]),
            metadata={"sql": "SELECT COUNT(*) FROM patients"}
        )