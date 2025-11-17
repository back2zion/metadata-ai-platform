"""
Approval Repository Interface
승인 저장소 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...domain.entities.approval_request import ApprovalRequest


class ApprovalRepositoryInterface(ABC):
    """승인 저장소 인터페이스"""
    
    @abstractmethod
    async def save(self, approval_request: ApprovalRequest) -> None:
        """승인 요청 저장"""
        pass
    
    @abstractmethod
    async def save_batch(self, approval_requests: List[ApprovalRequest]) -> None:
        """승인 요청 배치 저장"""
        pass
    
    @abstractmethod
    async def get_by_id(self, approval_id: str) -> Optional[ApprovalRequest]:
        """ID로 승인 요청 조회"""
        pass
    
    @abstractmethod
    async def get_pending_expired(self) -> List[ApprovalRequest]:
        """만료된 대기 요청들 조회"""
        pass
    
    @abstractmethod
    async def list_with_filters(
        self, 
        filters: Dict[str, Any], 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """필터링된 승인 요청 목록 조회"""
        pass
    
    @abstractmethod
    async def count_by_status(self, status: str) -> int:
        """상태별 승인 요청 수 조회"""
        pass
    
    @abstractmethod
    async def get_by_requester(
        self, 
        requester_id: str,
        limit: int = 10
    ) -> List[ApprovalRequest]:
        """요청자별 승인 요청 조회"""
        pass