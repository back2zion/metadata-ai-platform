from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.services.humanlayer_service import HumanLayerService
from app.core.config import settings

router = APIRouter()

class AgentTask(BaseModel):
    task_type: str  # "data_analysis", "etl_pipeline", "query_generation", etc.
    description: str
    context: Optional[Dict[str, Any]] = None
    require_approval: bool = True
    priority: str = "medium"  # low, medium, high, critical

class AgentTaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    result: Optional[Dict[str, Any]] = None

class ApprovalRequest(BaseModel):
    task_id: str
    approved: bool
    feedback: Optional[str] = None

@router.post("/execute", response_model=AgentTaskResponse)
async def execute_agent_task(
    task: AgentTask,
    background_tasks: BackgroundTasks,
    humanlayer_service: HumanLayerService = Depends()
):
    """
    Execute an AI agent task with optional human approval
    Uses HumanLayer for human-in-the-loop functionality
    """
    try:
        # Create task with HumanLayer
        task_id = await humanlayer_service.create_task(
            task_type=task.task_type,
            description=task.description,
            context=task.context,
            require_approval=task.require_approval,
            priority=task.priority
        )
        
        if task.require_approval:
            # Task needs approval - will be queued
            return AgentTaskResponse(
                task_id=task_id,
                status="pending_approval",
                message="Task created and waiting for human approval",
                result=None
            )
        else:
            # Execute immediately
            background_tasks.add_task(
                humanlayer_service.execute_task,
                task_id
            )
            return AgentTaskResponse(
                task_id=task_id,
                status="executing",
                message="Task is being executed",
                result=None
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    humanlayer_service: HumanLayerService = Depends()
):
    """Get the status of an agent task"""
    try:
        status = await humanlayer_service.get_task_status(task_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Task not found: {str(e)}")

@router.post("/approve")
async def approve_task(
    approval: ApprovalRequest,
    background_tasks: BackgroundTasks,
    humanlayer_service: HumanLayerService = Depends()
):
    """Approve or reject a pending task"""
    try:
        if approval.approved:
            # Execute the approved task
            background_tasks.add_task(
                humanlayer_service.execute_task,
                approval.task_id,
                approval.feedback
            )
            message = "Task approved and executing"
        else:
            await humanlayer_service.reject_task(
                approval.task_id,
                approval.feedback
            )
            message = "Task rejected"
        
        return {
            "task_id": approval.task_id,
            "status": "approved" if approval.approved else "rejected",
            "message": message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending")
async def get_pending_approvals(
    humanlayer_service: HumanLayerService = Depends()
):
    """Get all tasks pending approval"""
    try:
        pending_tasks = await humanlayer_service.get_pending_tasks()
        return {"pending_tasks": pending_tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/claude-code/launch")
async def launch_claude_code_session(
    project_path: str,
    instructions: Optional[str] = None,
    humanlayer_service: HumanLayerService = Depends()
):
    """
    Launch a Claude Code session for complex coding tasks
    This integrates with HumanLayer's Claude Code orchestration
    """
    try:
        session_id = await humanlayer_service.launch_claude_session(
            project_path=project_path,
            instructions=instructions
        )
        return {
            "session_id": session_id,
            "status": "launched",
            "message": "Claude Code session started"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/claude-code/sessions")
async def get_claude_sessions(
    humanlayer_service: HumanLayerService = Depends()
):
    """Get all active Claude Code sessions"""
    try:
        sessions = await humanlayer_service.get_claude_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))