"""
Process Approval Decision Use Case
승인 결정 처리 유스케이스
"""
import logging
from typing import Dict, Any

from ..interfaces.approval_repository import ApprovalRepositoryInterface
from ..interfaces.humanlayer_service import HumanLayerServiceInterface
from ..interfaces.notification_service import NotificationServiceInterface
from ..dto.approval_request_dto import ApprovalDecisionDTO
from ...domain.entities.approval_request import ApprovalRequestExpiredError, InvalidApprovalStateError
from ...domain.exceptions.domain_exceptions import DomainException

logger = logging.getLogger(__name__)


class ProcessApprovalDecisionUseCase:
    """승인 결정 처리 Use Case"""
    
    def __init__(
        self,
        approval_repository: ApprovalRepositoryInterface,
        humanlayer_service: HumanLayerServiceInterface,
        notification_service: NotificationServiceInterface
    ):
        self.approval_repository = approval_repository
        self.humanlayer_service = humanlayer_service
        self.notification_service = notification_service
    
    async def execute(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """승인 결정 처리 실행"""
        try:
            logger.info(f"Processing approval decision: {decision_data.get('approval_id')}")
            
            # 1. 승인 요청 조회
            approval_request = await self.approval_repository.get_by_id(
                decision_data["approval_id"]
            )
            
            if not approval_request:
                logger.error(f"Approval request not found: {decision_data['approval_id']}")
                return {
                    "success": False,
                    "error": "approval_not_found",
                    "message": "승인 요청을 찾을 수 없습니다."
                }
            
            # 2. 승인/거부 처리
            if decision_data["decision"] == "approve":
                approval_request.approve(
                    approver_id=decision_data["approver_id"],
                    reason=decision_data["reason"],
                    conditions=decision_data.get("conditions", []),
                    execution_expires_in_minutes=decision_data.get("execution_expires_in_minutes", 60)
                )
                
                logger.info(f"Approval request approved: {approval_request.id}")
                
                # 승인 알림
                await self.notification_service.notify_requester(
                    approval_request,
                    f"승인 요청이 승인되었습니다. 사유: {decision_data['reason']}",
                    "success"
                )
                
            elif decision_data["decision"] == "reject":
                approval_request.reject(
                    approver_id=decision_data["approver_id"],
                    reason=decision_data["reason"]
                )
                
                logger.info(f"Approval request rejected: {approval_request.id}")
                
                # 거부 알림
                await self.notification_service.notify_requester(
                    approval_request,
                    f"승인 요청이 거부되었습니다. 사유: {decision_data['reason']}",
                    "warning"
                )
                
            else:
                return {
                    "success": False,
                    "error": "invalid_decision",
                    "message": "올바르지 않은 결정입니다. 'approve' 또는 'reject'만 허용됩니다."
                }
            
            # 3. 저장소에 저장
            await self.approval_repository.save(approval_request)
            
            # 4. HumanLayer 상태 업데이트
            await self.humanlayer_service.update_approval_status(
                approval_request.id,
                approval_request.status.value,
                {
                    "decision": approval_request.decision.approved if approval_request.decision else None,
                    "approver_id": approval_request.decision.approver_id if approval_request.decision else None,
                    "reason": approval_request.decision.reason if approval_request.decision else None,
                    "decided_at": approval_request.decision.decided_at.isoformat() if approval_request.decision else None
                }
            )
            
            logger.info(f"Approval decision processed successfully: {approval_request.id}")
            
            return {
                "success": True,
                "status": approval_request.status.value,
                "approval_id": approval_request.id,
                "reason": decision_data["reason"],
                "approver_id": decision_data["approver_id"],
                "decided_at": approval_request.decision.decided_at.isoformat() if approval_request.decision else None,
                "execution_expires_at": approval_request.decision.expires_at.isoformat() if (
                    approval_request.decision and approval_request.decision.expires_at
                ) else None
            }
            
        except ApprovalRequestExpiredError as e:
            logger.warning(f"Cannot process expired approval request: {e}")
            return {
                "success": False,
                "error": "approval_expired",
                "message": "만료된 승인 요청은 처리할 수 없습니다."
            }
            
        except InvalidApprovalStateError as e:
            logger.warning(f"Invalid approval state: {e}")
            return {
                "success": False,
                "error": "invalid_state",
                "message": "현재 상태에서는 승인 결정을 처리할 수 없습니다."
            }
            
        except DomainException as e:
            logger.error(f"Domain error in approval decision: {e}")
            return {
                "success": False,
                "error": "domain_error",
                "message": str(e)
            }
            
        except Exception as e:
            logger.error(f"Failed to process approval decision: {e}")
            return {
                "success": False,
                "error": "processing_failed",
                "message": str(e)
            }