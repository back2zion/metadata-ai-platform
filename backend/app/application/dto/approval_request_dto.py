"""
Approval Request DTOs
승인 요청 데이터 전송 객체들
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime


@dataclass
class CreateApprovalRequestDTO:
    """승인 요청 생성 DTO"""
    sql: str
    natural_language: str
    requester_id: str
    priority: str = "medium"
    metadata: Dict[str, Any] = None
    expires_in_hours: int = 24
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ApprovalDecisionDTO:
    """승인 결정 DTO"""
    approval_id: str
    approver_id: str
    decision: str  # "approve" or "reject"
    reason: str
    conditions: List[str] = None
    execution_expires_in_minutes: int = 60
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = []


@dataclass
class ApprovalRequestFilterDTO:
    """승인 요청 필터 DTO"""
    status: Optional[str] = None
    requester_id: Optional[str] = None
    approver_id: Optional[str] = None
    risk_level: Optional[str] = None
    priority: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    approval_type: Optional[str] = None


@dataclass
class ApprovalRequestResponseDTO:
    """승인 요청 응답 DTO"""
    id: str
    type: str
    title: str
    description: str
    status: str
    priority: str
    risk_level: Dict[str, Any]
    requester_id: str
    required_approver_level: str
    created_at: str
    expires_at: str
    updated_at: str
    is_expired: bool
    remaining_minutes: int
    requires_urgent_attention: bool
    metadata: Dict[str, Any]
    decision: Optional[Dict[str, Any]] = None


@dataclass
class ApprovalRequestListResponseDTO:
    """승인 요청 목록 응답 DTO"""
    requests: List[ApprovalRequestResponseDTO]
    pagination: Dict[str, Any]
    summary: Dict[str, int]