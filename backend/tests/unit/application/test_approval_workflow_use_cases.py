"""
Unit Tests for Approval Workflow Use Cases (Application Layer)
어플리케이션 계층 - 승인 워크플로우 유스케이스 테스트

TDD 원칙에 따라 Red-Green-Refactor 사이클로 개발
"""
import pytest
from datetime import datetime, timedelta
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock

from app.domain.entities.approval_request import (
    ApprovalRequest, ApprovalType, ApprovalStatus, Priority
)
from app.domain.value_objects.risk_level import RiskLevel


class TestCreateApprovalRequestUseCase:
    """승인 요청 생성 Use Case 테스트"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_should_create_approval_request_successfully(self, tdd_case):
        """
        TDD Case 1: 승인 요청 성공적 생성
        
        Given: 유효한 SQL 쿼리와 메타데이터가 주어졌을 때
        When: 승인 요청을 생성하면
        Then: ApprovalRequest가 생성되고 저장된다
        """
        tdd_case.given("유효한 승인 요청 데이터가 준비됨")
        
        # Mock dependencies
        approval_repo = Mock()
        humanlayer_service = AsyncMock()
        notification_service = AsyncMock()
        
        # Input data
        request_data = {
            "sql": "SELECT COUNT(*) FROM patients WHERE age > 65",
            "natural_language": "65세 이상 환자 수 조회",
            "requester_id": "dr.kim@hospital.com",
            "priority": "medium",
            "metadata": {"database": "medical_dw", "purpose": "research"}
        }
        
        tdd_case.when("승인 요청 생성 Use Case를 실행함")
        
        # Green 단계 - 실제 구현 테스트
        from app.application.use_cases.create_approval_request_use_case import (
            CreateApprovalRequestUseCase
        )
        
        # Mock 설정
        approval_repo.save = AsyncMock()
        humanlayer_service.create_approval_request.return_value = {"id": "hl_123", "status": "created"}
        
        use_case = CreateApprovalRequestUseCase(
            approval_repo, humanlayer_service, notification_service
        )
        
        result = await use_case.execute(request_data)
        
        tdd_case.then("승인 요청이 성공적으로 생성됨")
        
        assert result["success"] is True
        assert "approval_id" in result
        approval_repo.save.assert_called_once()
        humanlayer_service.create_approval_request.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_should_handle_high_risk_sql_queries(self, tdd_case):
        """
        TDD Case 2: 고위험 SQL 쿼리 처리
        
        Given: 고위험 SQL 쿼리가 주어졌을 때
        When: 승인 요청을 생성하면
        Then: 적절한 승인자 레벨과 긴급 알림이 설정된다
        """
        tdd_case.given("고위험 SQL 쿼리가 준비됨")
        
        # Mock dependencies
        approval_repo = Mock()
        humanlayer_service = AsyncMock()
        notification_service = AsyncMock()
        
        high_risk_data = {
            "sql": "SELECT patient_id, name, ssn, email FROM patients WHERE patient_id = 'P123'",
            "natural_language": "특정 환자의 개인정보 조회",
            "requester_id": "admin.user@hospital.com",
            "priority": "urgent"
        }
        
        tdd_case.when("고위험 쿼리로 승인 요청을 생성함")
        
        from app.application.use_cases.create_approval_request_use_case import (
            CreateApprovalRequestUseCase
        )
        
        # Mock 설정
        approval_repo.save = AsyncMock()
        humanlayer_service.create_approval_request.return_value = {"id": "hl_456", "status": "created"}
        
        use_case = CreateApprovalRequestUseCase(
            approval_repo, humanlayer_service, notification_service
        )
        
        result = await use_case.execute(high_risk_data)
        
        tdd_case.then("고위험 승인 요청이 생성되고 적절한 알림이 전송됨")
        
        assert result["approval_request"]["required_approver_level"] in ["senior_manager", "chief_officer"]
        assert result["approval_request"]["priority"] == "urgent"
        notification_service.send_urgent_notification.assert_called_once()


class TestProcessApprovalDecisionUseCase:
    """승인 결정 처리 Use Case 테스트"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_should_approve_pending_request(self, tdd_case):
        """
        TDD Case 3: 대기 중인 요청 승인
        
        Given: 대기 중인 승인 요청이 있을 때
        When: 승인 결정을 처리하면
        Then: 요청이 승인되고 실행 준비된다
        """
        tdd_case.given("대기 중인 승인 요청이 준비됨")
        
        # Mock dependencies
        approval_repo = Mock()
        humanlayer_service = AsyncMock()
        notification_service = AsyncMock()
        
        # Mock existing approval request
        approval_request = ApprovalRequest(
            approval_type=ApprovalType.SQL_EXECUTION,
            title="Test SQL Execution",
            description="Test approval request",
            requester_id="test.user",
            risk_level=RiskLevel.from_factors(["select_query"]),
            metadata={"sql": "SELECT COUNT(*) FROM patients"}
        )
        approval_repo.get_by_id = AsyncMock(return_value=approval_request)
        
        decision_data = {
            "approval_id": approval_request.id,
            "approver_id": "supervisor.lee",
            "decision": "approve",
            "reason": "정당한 의료 데이터 조회",
            "conditions": ["30분 내 실행 완료"]
        }
        
        tdd_case.when("승인 결정 Use Case를 실행함")
        
        from app.application.use_cases.process_approval_decision_use_case import (
            ProcessApprovalDecisionUseCase
        )
        
        # Mock 설정
        approval_repo.save = AsyncMock()
        humanlayer_service.update_approval_status = AsyncMock()
        
        use_case = ProcessApprovalDecisionUseCase(
            approval_repo, humanlayer_service, notification_service
        )
        
        result = await use_case.execute(decision_data)
        
        tdd_case.then("승인 요청이 성공적으로 승인됨")
        
        assert result["success"] is True
        assert result["status"] == "approved"
        approval_repo.save.assert_called_once()
        notification_service.notify_requester.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_should_reject_inappropriate_request(self, tdd_case):
        """
        TDD Case 4: 부적절한 요청 거부
        
        Given: 부적절한 승인 요청이 있을 때
        When: 거부 결정을 처리하면
        Then: 요청이 거부되고 사유가 기록된다
        """
        tdd_case.given("부적절한 승인 요청이 준비됨")
        
        # Mock dependencies
        approval_repo = Mock()
        humanlayer_service = AsyncMock()
        notification_service = AsyncMock()
        
        # Mock existing approval request
        approval_request = ApprovalRequest(
            approval_type=ApprovalType.SQL_EXECUTION,
            title="Risky SQL Execution", 
            description="Potentially dangerous operation",
            requester_id="test.user",
            risk_level=RiskLevel.from_factors(["dangerous_keyword_delete", "pii_access_ssn"]),
            metadata={"sql": "DELETE FROM patients WHERE ssn = '123-45-6789'"}
        )
        approval_repo.get_by_id = AsyncMock(return_value=approval_request)
        
        decision_data = {
            "approval_id": approval_request.id,
            "approver_id": "security.officer",
            "decision": "reject",
            "reason": "보안 정책 위반: 개인정보 삭제는 허용되지 않음"
        }
        
        tdd_case.when("거부 결정 Use Case를 실행함")
        
        from app.application.use_cases.process_approval_decision_use_case import (
            ProcessApprovalDecisionUseCase
        )
        
        # Mock 설정
        approval_repo.save = AsyncMock()
        humanlayer_service.update_approval_status = AsyncMock()
        
        use_case = ProcessApprovalDecisionUseCase(
            approval_repo, humanlayer_service, notification_service
        )
        
        result = await use_case.execute(decision_data)
        
        tdd_case.then("승인 요청이 적절히 거부됨")
        
        assert result["success"] is True
        assert result["status"] == "rejected"
        assert result["reason"] == decision_data["reason"]


class TestExpireApprovalRequestsUseCase:
    """승인 요청 만료 처리 Use Case 테스트"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_should_expire_old_pending_requests(self, tdd_case):
        """
        TDD Case 5: 오래된 대기 요청 만료
        
        Given: 만료 시간이 지난 대기 요청들이 있을 때
        When: 만료 처리 Use Case를 실행하면
        Then: 해당 요청들이 만료 상태로 변경된다
        """
        tdd_case.given("만료된 대기 요청들이 준비됨")
        
        # Mock dependencies
        approval_repo = Mock()
        notification_service = AsyncMock()
        
        # Mock expired requests
        expired_request1 = ApprovalRequest(
            approval_type=ApprovalType.SQL_EXECUTION,
            title="Expired Request 1",
            description="First expired request",
            requester_id="user1",
            risk_level=RiskLevel.from_factors(["select_query"]),
            metadata={},
            expires_in_hours=-1  # Already expired
        )
        
        expired_request2 = ApprovalRequest(
            approval_type=ApprovalType.DATA_EXPORT,
            title="Expired Request 2", 
            description="Second expired request",
            requester_id="user2",
            risk_level=RiskLevel.from_factors(["patient_data"]),
            metadata={},
            expires_in_hours=-2  # Already expired
        )
        
        approval_repo.get_pending_expired = AsyncMock(return_value=[expired_request1, expired_request2])
        
        tdd_case.when("만료 처리 Use Case를 실행함")
        
        from app.application.use_cases.expire_approval_requests_use_case import (
            ExpireApprovalRequestsUseCase
        )
        
        # Mock 설정
        approval_repo.save_batch = AsyncMock()
        
        use_case = ExpireApprovalRequestsUseCase(
            approval_repo, notification_service
        )
        
        result = await use_case.execute()
        
        tdd_case.then("만료된 요청들이 적절히 처리됨")
        
        assert result["expired_count"] == 2
        assert approval_repo.save_batch.call_count == 1
        assert notification_service.notify_expiration.call_count == 2


class TestGetApprovalRequestStatusUseCase:
    """승인 요청 상태 조회 Use Case 테스트"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_should_get_approval_request_details(self, tdd_case):
        """
        TDD Case 6: 승인 요청 상세 정보 조회
        
        Given: 승인 요청 ID가 주어졌을 때
        When: 상태 조회 Use Case를 실행하면
        Then: 상세한 승인 요청 정보가 반환된다
        """
        tdd_case.given("승인 요청 ID가 준비됨")
        
        # Mock dependencies
        approval_repo = Mock()
        
        # Mock approval request
        approval_request = ApprovalRequest(
            approval_type=ApprovalType.SQL_EXECUTION,
            title="Patient Statistics Query",
            description="환자 통계 데이터 조회",
            requester_id="dr.kim@hospital.com",
            risk_level=RiskLevel.from_factors(["select_query", "patient_data"]),
            metadata={"sql": "SELECT region, COUNT(*) FROM patients GROUP BY region"}
        )
        
        # Approve the request for testing
        approval_request.approve(
            approver_id="supervisor.lee",
            reason="정당한 연구 목적",
            conditions=["결과 데이터 7일 후 삭제"]
        )
        
        approval_repo.get_by_id = AsyncMock(return_value=approval_request)
        
        tdd_case.when("상태 조회 Use Case를 실행함")
        
        from app.application.use_cases.get_approval_request_status_use_case import (
            GetApprovalRequestStatusUseCase
        )
        
        use_case = GetApprovalRequestStatusUseCase(approval_repo)
        
        result = await use_case.execute(approval_request.id)
        
        tdd_case.then("상세한 승인 요청 정보가 반환됨")
        
        assert result["id"] == approval_request.id
        assert result["status"] == "approved"
        assert result["risk_level"]["level"] == "medium"
        assert result["decision"]["approved"] is True
        assert "remaining_execution_time" in result["decision"]


class TestListApprovalRequestsUseCase:
    """승인 요청 목록 조회 Use Case 테스트"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_should_list_approval_requests_with_filters(self, tdd_case):
        """
        TDD Case 7: 필터링된 승인 요청 목록 조회
        
        Given: 다양한 상태의 승인 요청들이 있을 때
        When: 필터를 적용하여 목록 조회하면
        Then: 조건에 맞는 요청들만 반환된다
        """
        tdd_case.given("다양한 승인 요청들이 준비됨")
        
        # Mock dependencies
        approval_repo = Mock()
        
        # Create sample requests with different statuses
        requests = []
        for i in range(5):
            request = ApprovalRequest(
                approval_type=ApprovalType.SQL_EXECUTION,
                title=f"Test Request {i+1}",
                description=f"Test description {i+1}",
                requester_id=f"user{i+1}@hospital.com",
                risk_level=RiskLevel.from_factors(["select_query"]),
                metadata={"test": f"data{i+1}"}
            )
            
            # Approve some requests
            if i % 2 == 0:
                request.approve(f"approver{i}", f"Approved {i}")
            
            requests.append(request)
        
        approval_repo.list_with_filters = AsyncMock(return_value={
            "requests": requests[:3],  # Return first 3
            "total_count": 3,
            "page": 1,
            "page_size": 10
        })
        
        filters = {
            "status": "pending",
            "requester_id": "user1@hospital.com",
            "date_from": "2024-01-01",
            "date_to": "2024-12-31"
        }
        
        tdd_case.when("필터링된 목록 조회 Use Case를 실행함")
        
        from app.application.use_cases.list_approval_requests_use_case import (
            ListApprovalRequestsUseCase
        )
        
        use_case = ListApprovalRequestsUseCase(approval_repo)
        
        result = await use_case.execute(filters, page=1, page_size=10)
        
        tdd_case.then("필터링된 승인 요청 목록이 반환됨")
        
        assert "requests" in result
        assert "pagination" in result
        assert len(result["requests"]) <= 10
        approval_repo.list_with_filters.assert_called_once_with(
            filters, page=1, page_size=10
        )