"""
Expire Approval Requests Use Case
승인 요청 만료 처리 유스케이스
"""
import logging
from typing import Dict, Any, List

from ..interfaces.approval_repository import ApprovalRepositoryInterface
from ..interfaces.notification_service import NotificationServiceInterface
from ...domain.entities.approval_request import ApprovalRequest

logger = logging.getLogger(__name__)


class ExpireApprovalRequestsUseCase:
    """승인 요청 만료 처리 Use Case"""
    
    def __init__(
        self,
        approval_repository: ApprovalRepositoryInterface,
        notification_service: NotificationServiceInterface
    ):
        self.approval_repository = approval_repository
        self.notification_service = notification_service
    
    async def execute(self) -> Dict[str, Any]:
        """만료된 승인 요청들 처리 실행"""
        try:
            logger.info("Starting expiration process for approval requests")
            
            # 1. 만료된 대기 요청들 조회
            expired_requests = await self.approval_repository.get_pending_expired()
            
            if not expired_requests:
                logger.info("No expired requests found")
                return {
                    "success": True,
                    "expired_count": 0,
                    "message": "처리할 만료된 요청이 없습니다."
                }
            
            # 2. 각 요청을 만료 처리
            processed_requests = []
            for request in expired_requests:
                try:
                    request.mark_expired()
                    processed_requests.append(request)
                    
                    # 만료 알림 전송
                    await self.notification_service.notify_expiration(request)
                    
                    logger.info(f"Expired approval request: {request.id}")
                    
                except Exception as e:
                    logger.error(f"Failed to expire request {request.id}: {e}")
                    continue
            
            # 3. 배치 저장
            if processed_requests:
                await self.approval_repository.save_batch(processed_requests)
            
            expired_count = len(processed_requests)
            logger.info(f"Expired {expired_count} approval requests")
            
            return {
                "success": True,
                "expired_count": expired_count,
                "expired_request_ids": [req.id for req in processed_requests],
                "message": f"{expired_count}개의 승인 요청이 만료 처리되었습니다."
            }
            
        except Exception as e:
            logger.error(f"Failed to process expired requests: {e}")
            return {
                "success": False,
                "error": "expiration_failed",
                "message": str(e)
            }