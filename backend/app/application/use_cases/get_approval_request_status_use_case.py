"""
Get Approval Request Status Use Case
승인 요청 상태 조회 유스케이스
"""
import logging
from typing import Dict, Any, Optional

from ..interfaces.approval_repository import ApprovalRepositoryInterface
from ...domain.entities.approval_request import ApprovalRequest

logger = logging.getLogger(__name__)


class GetApprovalRequestStatusUseCase:
    """승인 요청 상태 조회 Use Case"""
    
    def __init__(self, approval_repository: ApprovalRepositoryInterface):
        self.approval_repository = approval_repository
    
    async def execute(self, approval_id: str) -> Dict[str, Any]:
        """승인 요청 상태 조회 실행"""
        try:
            logger.info(f"Getting approval request status: {approval_id}")
            
            # 승인 요청 조회
            approval_request = await self.approval_repository.get_by_id(approval_id)
            
            if not approval_request:
                logger.warning(f"Approval request not found: {approval_id}")
                return {
                    "success": False,
                    "error": "approval_not_found",
                    "message": "승인 요청을 찾을 수 없습니다."
                }
            
            # 상세 정보 반환
            result = {
                "id": approval_request.id,
                "type": approval_request.type.value,
                "title": approval_request.title,
                "description": approval_request.description,
                "status": approval_request.status.value,
                "priority": approval_request.priority.value,
                "risk_level": approval_request.risk_level.to_dict(),
                "requester_id": approval_request.requester_id,
                "required_approver_level": approval_request.required_approver_level,
                "created_at": approval_request.created_at.isoformat(),
                "expires_at": approval_request.expires_at.isoformat(),
                "updated_at": approval_request.updated_at.isoformat(),
                "is_expired": approval_request.is_expired(),
                "remaining_minutes": approval_request.get_remaining_time_minutes(),
                "requires_urgent_attention": approval_request.requires_urgent_attention(),
                "metadata": approval_request.metadata
            }
            
            # 승인 결정 정보 추가
            if approval_request.decision:
                result["decision"] = {
                    "approved": approval_request.decision.approved,
                    "approver_id": approval_request.decision.approver_id,
                    "reason": approval_request.decision.reason,
                    "decided_at": approval_request.decision.decided_at.isoformat(),
                    "conditions": approval_request.decision.conditions,
                    "expires_at": approval_request.decision.expires_at.isoformat() if approval_request.decision.expires_at else None,
                    "execution_expired": approval_request.is_execution_expired(),
                    "remaining_execution_time": approval_request.get_execution_remaining_time_minutes()
                }
            
            logger.info(f"Retrieved approval request status: {approval_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get approval request status: {e}")
            return {
                "success": False,
                "error": "retrieval_failed",
                "message": str(e)
            }