"""
HumanLayer Service Interface
HumanLayer 서비스 인터페이스
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from ...domain.entities.approval_request import ApprovalRequest


class HumanLayerServiceInterface(ABC):
    """HumanLayer 서비스 인터페이스"""
    
    @abstractmethod
    async def create_approval_request(
        self, 
        approval_request: ApprovalRequest
    ) -> Dict[str, Any]:
        """HumanLayer에 승인 요청 생성"""
        pass
    
    @abstractmethod
    async def update_approval_status(
        self,
        approval_id: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """HumanLayer에서 승인 상태 업데이트"""
        pass
    
    @abstractmethod
    async def get_approval_status(self, approval_id: str) -> Dict[str, Any]:
        """HumanLayer에서 승인 상태 조회"""
        pass
    
    @abstractmethod
    async def cancel_approval_request(self, approval_id: str) -> Dict[str, Any]:
        """HumanLayer에서 승인 요청 취소"""
        pass
    
    @abstractmethod
    async def get_available_approvers(
        self, 
        required_level: str
    ) -> List[Dict[str, Any]]:
        """필요한 승인자 레벨에 해당하는 승인자 목록 조회"""
        pass