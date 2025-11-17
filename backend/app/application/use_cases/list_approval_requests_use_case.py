"""
List Approval Requests Use Case
승인 요청 목록 조회 유스케이스
"""
import logging
from typing import Dict, Any, List

from ..interfaces.approval_repository import ApprovalRepositoryInterface
from ..dto.approval_request_dto import ApprovalRequestFilterDTO

logger = logging.getLogger(__name__)


class ListApprovalRequestsUseCase:
    """승인 요청 목록 조회 Use Case"""
    
    def __init__(self, approval_repository: ApprovalRepositoryInterface):
        self.approval_repository = approval_repository
    
    async def execute(
        self, 
        filters: Dict[str, Any], 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """승인 요청 목록 조회 실행"""
        try:
            logger.info(f"Listing approval requests with filters: {filters}")
            
            # 저장소에서 필터링된 목록 조회
            result = await self.approval_repository.list_with_filters(
                filters, page=page, page_size=page_size
            )
            
            # 응답 형식으로 변환
            requests_data = []
            for request in result["requests"]:
                request_data = {
                    "id": request.id,
                    "type": request.type.value,
                    "title": request.title,
                    "description": request.description,
                    "status": request.status.value,
                    "priority": request.priority.value,
                    "risk_level": request.risk_level.to_dict(),
                    "requester_id": request.requester_id,
                    "required_approver_level": request.required_approver_level,
                    "created_at": request.created_at.isoformat(),
                    "expires_at": request.expires_at.isoformat(),
                    "is_expired": request.is_expired(),
                    "remaining_minutes": request.get_remaining_time_minutes(),
                    "requires_urgent_attention": request.requires_urgent_attention()
                }
                
                # 승인 결정 정보 추가
                if request.decision:
                    request_data["decision"] = {
                        "approved": request.decision.approved,
                        "approver_id": request.decision.approver_id,
                        "decided_at": request.decision.decided_at.isoformat()
                    }
                
                requests_data.append(request_data)
            
            # 페이지네이션 정보
            pagination = {
                "page": result.get("page", page),
                "page_size": result.get("page_size", page_size),
                "total_count": result.get("total_count", 0),
                "total_pages": (result.get("total_count", 0) + page_size - 1) // page_size
            }
            
            # 상태별 통계 계산 (간단한 버전)
            summary = {
                "total": result.get("total_count", 0),
                "pending": len([r for r in requests_data if r["status"] == "pending"]),
                "approved": len([r for r in requests_data if r["status"] == "approved"]),
                "rejected": len([r for r in requests_data if r["status"] == "rejected"]),
                "expired": len([r for r in requests_data if r["status"] == "expired"])
            }
            
            logger.info(f"Retrieved {len(requests_data)} approval requests")
            
            return {
                "requests": requests_data,
                "pagination": pagination,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Failed to list approval requests: {e}")
            return {
                "success": False,
                "error": "listing_failed",
                "message": str(e)
            }