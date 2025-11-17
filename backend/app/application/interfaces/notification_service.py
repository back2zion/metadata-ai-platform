"""
Notification Service Interface
알림 서비스 인터페이스
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from ...domain.entities.approval_request import ApprovalRequest


class NotificationServiceInterface(ABC):
    """알림 서비스 인터페이스"""
    
    @abstractmethod
    async def send_urgent_notification(
        self, 
        approval_request: ApprovalRequest,
        recipients: List[str]
    ) -> Dict[str, Any]:
        """긴급 알림 전송"""
        pass
    
    @abstractmethod
    async def notify_requester(
        self,
        approval_request: ApprovalRequest,
        message: str,
        notification_type: str = "info"
    ) -> Dict[str, Any]:
        """요청자에게 알림 전송"""
        pass
    
    @abstractmethod
    async def notify_approvers(
        self,
        approval_request: ApprovalRequest,
        approvers: List[str],
        message: str
    ) -> Dict[str, Any]:
        """승인자들에게 알림 전송"""
        pass
    
    @abstractmethod
    async def notify_expiration(
        self,
        approval_request: ApprovalRequest
    ) -> Dict[str, Any]:
        """만료 알림 전송"""
        pass
    
    @abstractmethod
    async def send_approval_decision_notification(
        self,
        approval_request: ApprovalRequest,
        decision_type: str,
        reason: str
    ) -> Dict[str, Any]:
        """승인 결정 알림 전송"""
        pass