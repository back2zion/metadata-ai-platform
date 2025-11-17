"""
Approval Request Entity
승인 요청 도메인 엔티티
"""
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum

from ..value_objects.risk_level import RiskLevel
from ..exceptions.domain_exceptions import DomainException


class ApprovalStatus(Enum):
    """승인 상태"""
    PENDING = "pending"
    APPROVED = "approved"  
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApprovalType(Enum):
    """승인 유형"""
    SQL_EXECUTION = "sql_execution"
    DATA_EXPORT = "data_export"
    PII_ACCESS = "pii_access"
    MODEL_DEPLOYMENT = "model_deployment"
    SYSTEM_CONFIG = "system_config"


class Priority(Enum):
    """우선순위"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class ApprovalDecision:
    """승인 결정"""
    approved: bool
    approver_id: str
    reason: str
    decided_at: datetime
    conditions: List[str] = field(default_factory=list)
    expires_at: Optional[datetime] = None


class ApprovalRequestExpiredError(DomainException):
    """승인 요청 만료 예외"""
    pass


class InvalidApprovalStateError(DomainException):
    """잘못된 승인 상태 예외"""
    pass


class ApprovalRequest:
    """승인 요청 도메인 엔티티"""
    
    def __init__(self,
                 approval_type: ApprovalType,
                 title: str,
                 description: str,
                 requester_id: str,
                 risk_level: RiskLevel,
                 metadata: Dict[str, Any],
                 priority: Priority = Priority.MEDIUM,
                 expires_in_hours: int = 24):
        """승인 요청 생성자"""
        self.id = str(uuid.uuid4())
        self.type = approval_type
        self.title = title
        self.description = description
        self.requester_id = requester_id
        self.risk_level = risk_level
        self.priority = priority
        self.metadata = metadata or {}
        
        # 시간 정보
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(hours=expires_in_hours)
        self.updated_at = self.created_at
        
        # 상태
        self.status = ApprovalStatus.PENDING
        self.decision: Optional[ApprovalDecision] = None
        
        # 승인 관련
        self.required_approver_level = self._determine_required_approver_level()
        self.notification_sent = False
    
    def _determine_required_approver_level(self) -> str:
        """필요한 승인자 레벨 결정"""
        if self.risk_level.score >= 4:  # critical
            return "chief_officer"
        elif self.risk_level.score >= 3:  # high
            return "senior_manager"
        elif self.risk_level.score >= 2:  # medium
            return "manager"
        else:  # low
            return "supervisor"
    
    def approve(self, 
                approver_id: str, 
                reason: str = "Approved",
                conditions: List[str] = None,
                execution_expires_in_minutes: int = 60) -> None:
        """승인 처리"""
        self._validate_can_decide()
        
        execution_expires_at = datetime.utcnow() + timedelta(minutes=execution_expires_in_minutes)
        
        self.decision = ApprovalDecision(
            approved=True,
            approver_id=approver_id,
            reason=reason,
            decided_at=datetime.utcnow(),
            conditions=conditions or [],
            expires_at=execution_expires_at
        )
        
        self.status = ApprovalStatus.APPROVED
        self.updated_at = datetime.utcnow()
    
    def reject(self, 
               approver_id: str, 
               reason: str) -> None:
        """승인 거부"""
        self._validate_can_decide()
        
        self.decision = ApprovalDecision(
            approved=False,
            approver_id=approver_id,
            reason=reason,
            decided_at=datetime.utcnow()
        )
        
        self.status = ApprovalStatus.REJECTED
        self.updated_at = datetime.utcnow()
    
    def cancel(self, reason: str = "Cancelled by requester") -> None:
        """승인 요청 취소"""
        if self.status not in [ApprovalStatus.PENDING]:
            raise InvalidApprovalStateError(f"Cannot cancel request in status: {self.status.value}")
        
        self.status = ApprovalStatus.CANCELLED
        self.metadata["cancellation_reason"] = reason
        self.updated_at = datetime.utcnow()
    
    def mark_expired(self) -> None:
        """만료 처리"""
        if self.status == ApprovalStatus.PENDING:
            self.status = ApprovalStatus.EXPIRED
            self.updated_at = datetime.utcnow()
    
    def _validate_can_decide(self) -> None:
        """승인 결정 가능 여부 검증"""
        if self.status != ApprovalStatus.PENDING:
            raise InvalidApprovalStateError(f"Cannot decide on request in status: {self.status.value}")
        
        if self.is_expired():
            raise ApprovalRequestExpiredError(f"Approval request {self.id} has expired")
    
    def is_expired(self) -> bool:
        """만료 여부 확인"""
        return datetime.utcnow() > self.expires_at
    
    def is_pending(self) -> bool:
        """대기 중인지 확인"""
        return self.status == ApprovalStatus.PENDING and not self.is_expired()
    
    def is_approved(self) -> bool:
        """승인되었는지 확인"""
        return self.status == ApprovalStatus.APPROVED
    
    def is_execution_expired(self) -> bool:
        """실행 기한 만료 확인"""
        if not self.is_approved() or not self.decision or not self.decision.expires_at:
            return False
        return datetime.utcnow() > self.decision.expires_at
    
    def get_remaining_time_minutes(self) -> int:
        """남은 시간 (분)"""
        if self.is_expired():
            return 0
        
        remaining = self.expires_at - datetime.utcnow()
        return max(0, int(remaining.total_seconds() / 60))
    
    def get_execution_remaining_time_minutes(self) -> int:
        """실행 남은 시간 (분)"""
        if not self.is_approved() or not self.decision or not self.decision.expires_at:
            return 0
        
        if self.is_execution_expired():
            return 0
        
        remaining = self.decision.expires_at - datetime.utcnow()
        return max(0, int(remaining.total_seconds() / 60))
    
    def requires_urgent_attention(self) -> bool:
        """긴급 주의 필요 여부"""
        return (
            self.priority == Priority.URGENT or
            self.risk_level.score >= 4 or  # critical risk
            self.get_remaining_time_minutes() < 60  # 1시간 이내 만료
        )
    
    def to_humanlayer_payload(self) -> Dict[str, Any]:
        """HumanLayer API 페이로드 생성"""
        return {
            "id": self.id,
            "type": "approval_request",
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "metadata": {
                "request_type": self.type.value,
                "requester_id": self.requester_id,
                "risk_level": self.risk_level.to_dict(),
                "required_approver_level": self.required_approver_level,
                "expires_at": self.expires_at.isoformat(),
                "remaining_minutes": self.get_remaining_time_minutes(),
                "urgent": self.requires_urgent_attention(),
                **self.metadata
            }
        }
    
    def add_metadata(self, key: str, value: Any) -> None:
        """메타데이터 추가"""
        self.metadata[key] = value
        self.updated_at = datetime.utcnow()
    
    def update_priority(self, new_priority: Priority) -> None:
        """우선순위 변경"""
        if self.status != ApprovalStatus.PENDING:
            raise InvalidApprovalStateError("Cannot update priority of non-pending request")
        
        self.priority = new_priority
        self.updated_at = datetime.utcnow()
    
    def extend_expiration(self, additional_hours: int) -> None:
        """만료 시간 연장"""
        if self.status != ApprovalStatus.PENDING:
            raise InvalidApprovalStateError("Cannot extend expiration of non-pending request")
        
        self.expires_at += timedelta(hours=additional_hours)
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        result = {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "description": self.description,
            "requester_id": self.requester_id,
            "status": self.status.value,
            "priority": self.priority.value,
            "risk_level": self.risk_level.to_dict(),
            "required_approver_level": self.required_approver_level,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_expired": self.is_expired(),
            "remaining_minutes": self.get_remaining_time_minutes(),
            "requires_urgent_attention": self.requires_urgent_attention(),
            "metadata": self.metadata
        }
        
        if self.decision:
            result["decision"] = {
                "approved": self.decision.approved,
                "approver_id": self.decision.approver_id,
                "reason": self.decision.reason,
                "decided_at": self.decision.decided_at.isoformat(),
                "conditions": self.decision.conditions,
                "expires_at": self.decision.expires_at.isoformat() if self.decision.expires_at else None,
                "execution_expired": self.is_execution_expired(),
                "execution_remaining_minutes": self.get_execution_remaining_time_minutes()
            }
        
        return result
    
    def __str__(self) -> str:
        return f"ApprovalRequest(id={self.id[:8]}..., type={self.type.value}, status={self.status.value})"
    
    def __repr__(self) -> str:
        return (f"ApprovalRequest(id='{self.id}', type='{self.type.value}', "
                f"status='{self.status.value}', risk='{self.risk_level.value}')")