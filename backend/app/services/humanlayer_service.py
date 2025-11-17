import httpx
import asyncio
import uuid
from typing import Optional, Dict, Any, List
from app.core.config import settings
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
import json

class HumanLayerService:
    """
    Service for integrating with HumanLayer for human-in-the-loop AI operations
    """
    
    def __init__(self):
        self.daemon_url = settings.HUMANLAYER_DAEMON_URL
        self.api_key = settings.HUMANLAYER_API_KEY
        self.pending_tasks = {}  # In-memory storage for demo
        
        # Initialize LLM for agent tasks
        if settings.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model="gpt-4-turbo-preview",
                temperature=0
            )
    
    async def create_task(
        self,
        task_type: str,
        description: str,
        context: Optional[Dict[str, Any]] = None,
        require_approval: bool = True,
        priority: str = "medium"
    ) -> str:
        """Create a new AI agent task"""
        task_id = str(uuid.uuid4())
        
        task_data = {
            "id": task_id,
            "type": task_type,
            "description": description,
            "context": context or {},
            "require_approval": require_approval,
            "priority": priority,
            "status": "pending_approval" if require_approval else "ready",
            "created_at": asyncio.get_event_loop().time()
        }
        
        self.pending_tasks[task_id] = task_data
        
        if require_approval:
            # Send approval request to HumanLayer daemon
            await self._request_approval(task_data)
        
        return task_id
    
    async def _request_approval(self, task_data: Dict[str, Any]):
        """Send approval request to HumanLayer daemon"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.daemon_url}/api/v1/approvals",
                    json={
                        "id": task_data["id"],
                        "type": "agent_task",
                        "description": task_data["description"],
                        "metadata": {
                            "task_type": task_data["type"],
                            "priority": task_data["priority"],
                            "context": task_data["context"]
                        }
                    },
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
        except Exception as e:
            print(f"Failed to send approval request to HumanLayer: {e}")
    
    async def execute_task(self, task_id: str, feedback: Optional[str] = None):
        """Execute an approved task"""
        if task_id not in self.pending_tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.pending_tasks[task_id]
        task["status"] = "executing"
        
        try:
            # Route to appropriate handler based on task type
            if task["type"] == "data_analysis":
                result = await self._execute_data_analysis(task)
            elif task["type"] == "etl_pipeline":
                result = await self._execute_etl_pipeline(task)
            elif task["type"] == "query_generation":
                result = await self._execute_query_generation(task)
            else:
                result = await self._execute_generic_task(task)
            
            task["status"] = "completed"
            task["result"] = result
            
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
    
    async def _execute_data_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data analysis task"""
        # This would integrate with your data analysis pipelines
        return {
            "analysis_type": "descriptive",
            "insights": ["Sample insight 1", "Sample insight 2"],
            "visualizations": ["chart1.png", "chart2.png"]
        }
    
    async def _execute_etl_pipeline(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute ETL pipeline task"""
        # This would trigger Airflow DAGs or other ETL processes
        return {
            "pipeline_id": "etl_001",
            "status": "running",
            "estimated_completion": "15 minutes"
        }
    
    async def _execute_query_generation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SQL query from natural language"""
        description = task["description"]
        
        # Use LLM to generate SQL
        if hasattr(self, 'llm'):
            prompt = f"""
            Generate a SQL query for the following request:
            {description}
            
            Database schema context:
            - dim_patient: patient_key, age_group, gender, region
            - dim_diagnosis: diagnosis_key, kcd_code, diagnosis_name
            - fact_visit: visit_key, patient_key, diagnosis_key, visit_count
            
            Return only the SQL query.
            """
            
            sql_query = self.llm.predict(prompt)
            
            return {
                "query": sql_query,
                "confidence": 0.85,
                "explanation": f"Generated SQL for: {description}"
            }
        
        return {
            "query": "SELECT COUNT(*) FROM fact_visit",
            "confidence": 0.5,
            "explanation": "Default query - LLM not configured"
        }
    
    async def _execute_generic_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute generic AI agent task"""
        return {
            "status": "completed",
            "message": f"Task {task['type']} completed successfully"
        }
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the current status of a task"""
        if task_id not in self.pending_tasks:
            raise ValueError(f"Task {task_id} not found")
        
        return self.pending_tasks[task_id]
    
    async def reject_task(self, task_id: str, feedback: Optional[str] = None):
        """Reject a pending task"""
        if task_id not in self.pending_tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.pending_tasks[task_id]
        task["status"] = "rejected"
        task["feedback"] = feedback
    
    async def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks pending approval"""
        return [
            task for task in self.pending_tasks.values()
            if task["status"] == "pending_approval"
        ]
    
    async def launch_claude_session(
        self,
        project_path: str,
        instructions: Optional[str] = None
    ) -> str:
        """Launch a Claude Code session via HumanLayer daemon"""
        session_id = str(uuid.uuid4())
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.daemon_url}/api/v1/sessions",
                    json={
                        "project_path": project_path,
                        "instructions": instructions,
                        "metadata": {
                            "launched_by": "asan_idp",
                            "purpose": "code_generation"
                        }
                    },
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("session_id", session_id)
        except Exception as e:
            print(f"Failed to launch Claude session: {e}")
            return session_id
    
    async def get_claude_sessions(self) -> List[Dict[str, Any]]:
        """Get all active Claude Code sessions"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.daemon_url}/api/v1/sessions",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                return response.json().get("sessions", [])
        except Exception as e:
            print(f"Failed to get Claude sessions: {e}")
            return []