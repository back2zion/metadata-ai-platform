from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.text2sql_service import Text2SQLService

router = APIRouter()

class Text2SQLRequest(BaseModel):
    question: str
    context: Optional[Dict[str, Any]] = None
    include_explanation: bool = True

class PromptEnhancementRequest(BaseModel):
    question: str
    enhancement_type: Optional[str] = "medical"

class PromptEnhancementResponse(BaseModel):
    original_question: str
    enhanced_question: str
    enhancements_applied: List[str]
    confidence: float

class EnhancedText2SQLRequest(BaseModel):
    question: str
    enhancement_type: Optional[str] = "medical"
    include_explanation: bool = True
    auto_execute: bool = True

class EnhancedText2SQLResponse(BaseModel):
    original_question: str
    enhanced_question: str
    enhancements_applied: List[str]
    enhancement_confidence: float
    sql: str
    sql_explanation: str
    sql_confidence: float
    execution_result: Optional[Dict[str, Any]] = None

class Text2SQLResponse(BaseModel):
    sql: str
    explanation: str
    confidence: float
    execution_result: Optional[Dict[str, Any]] = None

class SQLExecuteRequest(BaseModel):
    sql: str
    limit: Optional[int] = 100

def get_text2sql_service():
    return Text2SQLService()

@router.post("/generate", response_model=Text2SQLResponse)
async def generate_sql_from_text(
    request: Text2SQLRequest,
    service: Text2SQLService = Depends(get_text2sql_service)
):
    """
    Generate SQL query from natural language question
    
    Examples:
    - "2023년에 당뇨병 진단받은 50대 환자는 몇 명?"
    - "지난 3개월간 가장 많이 처방된 약물 상위 10개"
    - "평균 입원 기간이 가장 긴 진료과는?"
    """
    try:
        result = await service.natural_language_to_sql(
            question=request.question,
            context=request.context,
            include_explanation=request.include_explanation
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute")
async def execute_sql_query(
    request: SQLExecuteRequest,
    service: Text2SQLService = Depends(get_text2sql_service)
):
    """Execute generated SQL query and return results"""
    try:
        result = await service.execute_sql(
            sql=request.sql,
            limit=request.limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQL execution error: {str(e)}")

@router.get("/examples")
async def get_example_questions():
    """Get example questions for Text2SQL"""
    return {
        "examples": [
            {
                "category": "환자 통계",
                "questions": [
                    "2023년에 당뇨병 진단받은 환자는 몇 명인가요?",
                    "50대 남성 중 고혈압 환자의 비율은?",
                    "지난 1년간 응급실을 방문한 환자 수는?"
                ]
            },
            {
                "category": "진료 분석",
                "questions": [
                    "평균 입원 기간이 가장 긴 진료과는?",
                    "재입원율이 가장 높은 질병은?",
                    "월별 외래 환자 수 추이는?"
                ]
            },
            {
                "category": "약물 처방",
                "questions": [
                    "가장 많이 처방된 약물 상위 10개는?",
                    "항생제 처방률이 가장 높은 진료과는?",
                    "당뇨병 환자의 평균 약물 처방 개수는?"
                ]
            }
        ]
    }

@router.get("/schema")
async def get_database_schema():
    """Get database schema information for Text2SQL context"""
    return {
        "tables": [
            {
                "name": "dim_patient",
                "description": "환자 차원 테이블",
                "columns": [
                    {"name": "patient_key", "type": "integer", "description": "환자 키"},
                    {"name": "age_group", "type": "varchar", "description": "연령대"},
                    {"name": "gender", "type": "varchar", "description": "성별"},
                    {"name": "region", "type": "varchar", "description": "거주 지역"}
                ]
            },
            {
                "name": "dim_diagnosis",
                "description": "진단 차원 테이블",
                "columns": [
                    {"name": "diagnosis_key", "type": "integer", "description": "진단 키"},
                    {"name": "kcd_code", "type": "varchar", "description": "KCD 질병 코드"},
                    {"name": "diagnosis_name", "type": "varchar", "description": "진단명"},
                    {"name": "category", "type": "varchar", "description": "질병 분류"}
                ]
            },
            {
                "name": "fact_visit",
                "description": "진료 사실 테이블",
                "columns": [
                    {"name": "visit_key", "type": "integer", "description": "방문 키"},
                    {"name": "patient_key", "type": "integer", "description": "환자 키"},
                    {"name": "diagnosis_key", "type": "integer", "description": "진단 키"},
                    {"name": "visit_date", "type": "date", "description": "방문 날짜"},
                    {"name": "visit_count", "type": "integer", "description": "방문 횟수"},
                    {"name": "duration_days", "type": "integer", "description": "입원 일수"},
                    {"name": "total_cost", "type": "decimal", "description": "진료비"}
                ]
            }
        ]
    }

@router.get("/history")
async def get_query_history(
    limit: int = 10,
    service: Text2SQLService = Depends(get_text2sql_service)
):
    """Get recent Text2SQL query history"""
    try:
        history = await service.get_query_history(limit)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enhance-prompt", response_model=PromptEnhancementResponse)
async def enhance_medical_prompt(
    request: PromptEnhancementRequest,
    service: Text2SQLService = Depends(get_text2sql_service)
):
    """
    의료 질의를 구조화된 프롬프트로 강화
    
    Examples:
    - Input: "내 진료내역 중 홍길동 환자에 대한 내분비내과와 연계된 당뇨 경과기록 정보 전체"
    - Output: "내 진료내역 중 환자이름이 홍길동에 대하여 진료과가 내분비내과와 연계된 입원경과기록 중에서 당뇨 경과기록 정보 전체"
    """
    try:
        result = await service.enhance_medical_prompt(
            question=request.question,
            enhancement_type=request.enhancement_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enhanced-generate", response_model=EnhancedText2SQLResponse)
async def enhanced_generate_sql(
    request: EnhancedText2SQLRequest,
    service: Text2SQLService = Depends(get_text2sql_service)
):
    """
    프롬프트 강화 → SQL 생성 → 실행 통합 API
    
    Example:
    - Input: "내 진료내역 중 홍길동 환자에 대한 당뇨 경과기록 정보와 TG 검사 결과 보여줘"
    - Enhancement: "내 진료내역 중 환자이름이 홍길동인 당뇨병 관련 입원경과기록 정보와 검사명이 중성지방인 검사 결과를 보여주세요"
    - SQL Generation + Execution
    """
    try:
        # Step 1: 프롬프트 강화
        enhancement_result = await service.enhance_medical_prompt(
            question=request.question,
            enhancement_type=request.enhancement_type
        )
        
        # Step 2: 강화된 프롬프트로 SQL 생성
        sql_result = await service.natural_language_to_sql(
            question=enhancement_result["enhanced_question"],
            include_explanation=request.include_explanation
        )
        
        # Step 3: SQL 실행 (선택사항)
        execution_result = None
        if request.auto_execute and sql_result["sql"]:
            try:
                execution_result = await service.execute_sql(sql_result["sql"])
            except Exception as exec_error:
                # SQL 실행 오류는 별도로 처리하되 전체 요청은 실패하지 않음
                execution_result = {
                    "error": f"SQL execution failed: {str(exec_error)}",
                    "results": [],
                    "row_count": 0
                }
        
        return EnhancedText2SQLResponse(
            original_question=enhancement_result["original_question"],
            enhanced_question=enhancement_result["enhanced_question"],
            enhancements_applied=enhancement_result["enhancements_applied"],
            enhancement_confidence=enhancement_result["confidence"],
            sql=sql_result["sql"],
            sql_explanation=sql_result["explanation"],
            sql_confidence=sql_result["confidence"],
            execution_result=execution_result
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))