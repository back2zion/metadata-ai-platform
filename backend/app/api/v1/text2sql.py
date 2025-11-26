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
    enhancement_type: Optional[str] = "financial"

class PromptEnhancementResponse(BaseModel):
    original_question: str
    enhanced_question: str
    enhancements_applied: List[str]
    confidence: float

class EnhancedText2SQLRequest(BaseModel):
    question: str
    enhancement_type: Optional[str] = "financial"
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
        print(f"🔍 Executing SQL: {request.sql}")
        result = await service.execute_sql(
            sql=request.sql,
            limit=request.limit
        )
        print(f"✅ SQL execution successful: {result.get('row_count', 0)} rows")
        return result
    except Exception as e:
        error_msg = f"SQL execution error: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"❌ SQL that failed: {request.sql}")
        raise HTTPException(status_code=400, detail=error_msg)

@router.get("/examples")
async def get_example_questions():
    """Get example questions for K-Bank Text2SQL"""
    return {
        "examples": [
            {
                "category": "고객 세분화 분석",
                "description": "고객별 특성 및 세그먼트 분석을 위한 질의",
                "questions": [
                    "VIP등급별 고객 수와 평균 이용금액은?",
                    "40대 여성 고객 중 신용카드 이용률이 높은 지역 상위 5곳은?",
                    "경기도 거주 고객의 연령대별 분포와 평균 거래금액은?"
                ]
            },
            {
                "category": "카드 사용 패턴 분석",
                "description": "카드 결제 행동 및 업종별 이용 패턴 분석",
                "questions": [
                    "신용카드 대비 체크카드 이용 비중이 높은 고객 세그먼트는?",
                    "쇼핑, 요식, 교통 업종별 월평균 이용금액 상위 10% 고객의 특성은?",
                    "이용가맹점수가 10개 이상인 고객의 주요 이용 카테고리는?"
                ]
            },
            {
                "category": "지역별 분석",
                "description": "지역별 고객 행동 및 트렌드 분석",
                "questions": [
                    "서울지역 고객의 VIP등급 분포와 평균 거래금액은?",
                    "지역별 쇼핑 이용금액이 가장 높은 상위 3개 지역은?",
                    "부산지역 20대 고객의 교통비 지출 패턴은?"
                ]
            },
            {
                "category": "상품 성과 분석",
                "description": "금융상품별 성과 및 고객 선호도 분석",
                "questions": [
                    "펀드상품별 1년 수익률 상위 10개와 해당 상품의 투자위험등급 분포는?",
                    "체크카드 vs 신용카드 이용 패턴 차이와 평균 거래금액은?",
                    "투자위험등급 1-3등급 펀드 중 순자산 규모가 큰 상품들은?"
                ]
            },
            {
                "category": "리워드 및 혜택 분석",
                "description": "캐시백 적립 및 고객 혜택 분석",
                "questions": [
                    "월평균 캐시백 적립금액이 높은 고객층의 특성은?",
                    "쇼핑 vs 요식 vs 교통 카테고리별 캐시백 적립 현황은?",
                    "VIP등급별 리워드 적립금액과 만료 예정 금액은?"
                ]
            },
            {
                "category": "운영 분석",
                "description": "고객 거래 패턴 및 서비스 이용 분석",
                "questions": [
                    "월별 거래 건수가 증가 추세인 고객 특성은?",
                    "연령대별 주요 이용 카테고리와 평균 거래금액은?",
                    "성별에 따른 카드 선호도와 이용 패턴 차이는?"
                ]
            }
        ]
    }

@router.get("/schema")
async def get_database_schema():
    """Get K-Bank database schema information for Text2SQL context"""
    return {
        "database_info": {
            "name": "K-Bank 합성데이터베이스",
            "description": "케이뱅크 300만 고객 실제 합성데이터 (2018년 8-12월 기준)",
            "total_records": "5,848,553개 레코드",
            "last_updated": "2024-11-24"
        },
        "tables": [
            {
                "name": "dim_customer_real",
                "alias": "dim_customer", 
                "description": "고객 차원 테이블 (300만 고객)",
                "record_count": "3,000,000",
                "columns": [
                    {"name": "customer_key", "type": "integer", "description": "고객 키 (PK)"},
                    {"name": "customer_id", "type": "varchar", "description": "발급회원번호 (SYN_0~SYN_2999999)"},
                    {"name": "customer_name", "type": "varchar", "description": "고객명 (익명화)"},
                    {"name": "age_group", "type": "varchar", "description": "연령대 (20대,30대,40대,50대,60대)"},
                    {"name": "gender", "type": "varchar", "description": "성별 (남,여)"},
                    {"name": "region", "type": "varchar", "description": "거주지역 (서울,경기,부산,대구,인천,광주,대전,울산 등)"},
                    {"name": "customer_grade", "type": "varchar", "description": "VIP등급 (일반,실버,골드,플래티넘,VIP,VVIP,프리미엄)"},
                    {"name": "join_date", "type": "date", "description": "가입일자"}
                ]
            },
            {
                "name": "fact_transaction_real",
                "alias": "fact_transaction",
                "description": "거래 사실 테이블 (141만 거래)",
                "record_count": "1,412,553",
                "columns": [
                    {"name": "transaction_key", "type": "integer", "description": "거래 키 (PK)"},
                    {"name": "customer_key", "type": "integer", "description": "고객 키 (FK)"},
                    {"name": "product_type", "type": "varchar", "description": "상품타입 (신용카드,체크카드,기타)"},
                    {"name": "transaction_amount", "type": "decimal", "description": "거래금액"},
                    {"name": "transaction_type", "type": "varchar", "description": "거래유형 (카드결제)"},
                    {"name": "transaction_date", "type": "date", "description": "거래일자"},
                    {"name": "shopping_amount", "type": "decimal", "description": "쇼핑 이용금액"},
                    {"name": "dining_amount", "type": "decimal", "description": "요식 이용금액"},
                    {"name": "transport_amount", "type": "decimal", "description": "교통 이용금액"},
                    {"name": "merchant_count", "type": "integer", "description": "이용가맹점수"},
                    {"name": "primary_category", "type": "varchar", "description": "주요카테고리 (쇼핑,요식,교통)"}
                ]
            },
            {
                "name": "dim_product_real", 
                "alias": "dim_product",
                "description": "금융상품 차원 테이블 (펀드상품)",
                "record_count": "24,181",
                "columns": [
                    {"name": "product_key", "type": "integer", "description": "상품 키 (PK)"},
                    {"name": "product_code", "type": "varchar", "description": "펀드코드"},
                    {"name": "product_name", "type": "varchar", "description": "펀드명"},
                    {"name": "product_type", "type": "varchar", "description": "대유형 (주식형,채권형,혼합형,MMF,기타)"},
                    {"name": "risk_level", "type": "varchar", "description": "투자위험등급 (1-6등급)"},
                    {"name": "annual_return", "type": "decimal", "description": "1년 수익률"},
                    {"name": "net_assets", "type": "decimal", "description": "순자산 규모"}
                ]
            },
            {
                "name": "dim_merchant_real",
                "alias": "dim_merchant", 
                "description": "가맹점 차원 테이블",
                "record_count": "10",
                "columns": [
                    {"name": "merchant_key", "type": "integer", "description": "가맹점 키 (PK)"},
                    {"name": "merchant_id", "type": "varchar", "description": "가맹점 ID"},
                    {"name": "merchant_name", "type": "varchar", "description": "가맹점명"},
                    {"name": "category", "type": "varchar", "description": "업종분류 (온라인쇼핑,편의점,카페/음료,대형마트 등)"}
                ]
            },
            {
                "name": "fact_reward_real",
                "alias": "fact_reward",
                "description": "리워드 사실 테이블 (캐시백 적립)",
                "record_count": "1,411,078", 
                "columns": [
                    {"name": "reward_key", "type": "integer", "description": "리워드 키 (PK)"},
                    {"name": "customer_key", "type": "integer", "description": "고객 키 (FK)"},
                    {"name": "reward_amount", "type": "decimal", "description": "적립금액"},
                    {"name": "reward_type", "type": "varchar", "description": "리워드타입 (캐시백)"},
                    {"name": "reward_source", "type": "varchar", "description": "적립원천 (쇼핑,요식,교통)"},
                    {"name": "expiry_date", "type": "date", "description": "만료일자"},
                    {"name": "earn_date", "type": "date", "description": "적립일자"}
                ]
            },
            {
                "name": "dim_time_real",
                "alias": "dim_time",
                "description": "시간 차원 테이블 (2018-2019년)",
                "record_count": "731",
                "columns": [
                    {"name": "time_key", "type": "integer", "description": "시간 키 (PK)"},
                    {"name": "date_value", "type": "date", "description": "날짜"},
                    {"name": "year", "type": "integer", "description": "년"},
                    {"name": "quarter", "type": "integer", "description": "분기"},
                    {"name": "month", "type": "integer", "description": "월"},
                    {"name": "day", "type": "integer", "description": "일"},
                    {"name": "day_of_week", "type": "integer", "description": "요일"},
                    {"name": "is_weekend", "type": "boolean", "description": "주말여부"}
                ]
            }
        ],
        "business_context": {
            "domain": "K-Bank 디지털 금융",
            "key_metrics": [
                "고객별 월평균 이용금액", "VIP등급별 수익성", "상품별 가입률",
                "지역별 시장점유율", "연령대별 금융행동 패턴", "캐시백 적립률"
            ],
            "common_analysis": [
                "고객 세분화", "상품 성과 분석", "리스크 관리", "마케팅 효과 측정",
                "운영 최적화", "수익성 분석"
            ]
        }
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
async def enhance_financial_prompt(
    request: PromptEnhancementRequest,
    service: Text2SQLService = Depends(get_text2sql_service)
):
    """
    K-Bank 금융 질의를 전문적이고 구조화된 프롬프트로 강화
    
    Examples:
    - Input: "VIP등급별 고객 수는?"
    - Output: "고객 가치 등급(VIP) 기준 고객 세그먼트 분포와 각 등급별 평균 수익성(ARPU), 거래 활성도 지표를 포함한 포트폴리오 현황 분석"
    """
    try:
        result = await service.enhance_financial_prompt(
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
        enhancement_result = await service.enhance_financial_prompt(
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