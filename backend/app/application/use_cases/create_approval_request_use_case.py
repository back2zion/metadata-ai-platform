"""
Create Approval Request Use Case
승인 요청 생성 유스케이스
"""
import logging
from typing import Dict, Any

from ..interfaces.approval_repository import ApprovalRepositoryInterface
from ..interfaces.humanlayer_service import HumanLayerServiceInterface
from ..interfaces.notification_service import NotificationServiceInterface
from ..dto.approval_request_dto import CreateApprovalRequestDTO, ApprovalRequestResponseDTO
from ...domain.entities.approval_request import ApprovalRequest, ApprovalType, Priority
from ...domain.entities.sql_query import SQLQuery
from ...domain.exceptions.domain_exceptions import InvalidSQLSyntaxError

logger = logging.getLogger(__name__)


class CreateApprovalRequestUseCase:
    """승인 요청 생성 Use Case"""
    
    def __init__(
        self,
        approval_repository: ApprovalRepositoryInterface,
        humanlayer_service: HumanLayerServiceInterface,
        notification_service: NotificationServiceInterface
    ):
        self.approval_repository = approval_repository
        self.humanlayer_service = humanlayer_service
        self.notification_service = notification_service
    
    async def execute(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """승인 요청 생성 실행"""
        try:
            logger.info(f"Creating approval request for requester: {request_data.get('requester_id')}")
            
            # 1. SQL 쿼리 분석 및 검증
            sql_query = SQLQuery(
                text=request_data["sql"],
                natural_language=request_data["natural_language"],
                confidence=0.9  # Default confidence for manual requests
            )
            
            # 2. 승인 요청 생성
            approval_request = ApprovalRequest(
                approval_type=ApprovalType.SQL_EXECUTION,
                title=f"SQL Execution: {request_data['natural_language'][:50]}",
                description=request_data["natural_language"],
                requester_id=request_data["requester_id"],
                risk_level=sql_query.risk_level,
                metadata={
                    **request_data.get("metadata", {}),
                    "sql_query_id": sql_query.id,
                    "sql": sql_query.text,
                    "estimated_execution_time": sql_query.estimated_execution_time,
                    "estimated_rows": sql_query.estimated_rows,
                    "tables_accessed": sql_query.tables_accessed,
                    **sql_query.generate_approval_metadata()
                },
                priority=Priority(request_data.get("priority", "medium")),
                expires_in_hours=request_data.get("expires_in_hours", 24)
            )
            
            # 3. 저장소에 저장
            await self.approval_repository.save(approval_request)
            
            # 4. HumanLayer에 승인 요청 생성
            humanlayer_response = await self.humanlayer_service.create_approval_request(
                approval_request
            )
            
            # 5. 긴급 알림이 필요한 경우 알림 전송
            if approval_request.requires_urgent_attention():
                await self.notification_service.send_urgent_notification(
                    approval_request,
                    recipients=[f"approver_{approval_request.required_approver_level}"]
                )
                logger.warning(f"Urgent approval request created: {approval_request.id}")
            
            # 6. 요청자에게 승인 요청 생성 알림
            await self.notification_service.notify_requester(
                approval_request,
                f"승인 요청이 생성되었습니다. ID: {approval_request.id}",
                "success"
            )
            
            logger.info(f"Approval request created successfully: {approval_request.id}")
            
            return {
                "success": True,
                "approval_id": approval_request.id,
                "approval_request": self._to_response_dto(approval_request),
                "humanlayer_response": humanlayer_response
            }
            
        except InvalidSQLSyntaxError as e:
            logger.error(f"Invalid SQL syntax: {e}")
            return {
                "success": False,
                "error": "invalid_sql_syntax",
                "message": str(e)
            }
        except Exception as e:
            logger.error(f"Failed to create approval request: {e}")
            return {
                "success": False,
                "error": "creation_failed",
                "message": str(e)
            }
    
    def _to_response_dto(self, approval_request: ApprovalRequest) -> Dict[str, Any]:
        """ApprovalRequest를 응답 DTO로 변환"""
        return {
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