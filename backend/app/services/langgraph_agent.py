"""
서울아산병원 AI 플랫폼 - LangGraph 에이전트 시스템
의료진을 위한 지능형 AI 에이전트
"""
from typing import Dict, List, Any, Optional, TypedDict, Literal, Annotated
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.tools import BaseTool, tool
# from langchain.agents import AgentExecutor  # Not needed for LangGraph
from pydantic import BaseModel, Field
import asyncio
import logging
from datetime import datetime
import json
import uuid

from vector_store import medical_vector_store
from graph_rag import medical_graph_rag
from qwen_model import qwen_model

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """LangGraph 에이전트 상태"""
    messages: Annotated[list, add_messages]
    user_type: str
    session_id: str
    context: Dict[str, Any]
    tools_used: List[str]
    knowledge_retrieved: List[Dict[str, Any]]
    current_step: str
    reasoning: List[str]

class MedicalSearchInput(BaseModel):
    """의료 검색 입력 스키마"""
    query: str = Field(description="검색 쿼리")
    user_type: str = Field(default="patient", description="사용자 유형")
    search_type: str = Field(default="hybrid", description="검색 유형: vector, graph, hybrid")

class MedicalAnalysisInput(BaseModel):
    """의료 분석 입력 스키마"""
    symptoms: List[str] = Field(description="증상 목록")
    patient_info: Dict[str, Any] = Field(default={}, description="환자 정보")
    analysis_type: str = Field(default="diagnosis", description="분석 유형")

@tool("medical_knowledge_search", args_schema=MedicalSearchInput)
def medical_knowledge_search(query: str, user_type: str = "patient", search_type: str = "hybrid") -> Dict[str, Any]:
    """의료 지식베이스에서 정보 검색"""
    try:
        results = {"vector_results": [], "graph_results": {}, "combined_context": ""}
        
        if search_type in ["vector", "hybrid"]:
            # 벡터 검색
            vector_results = medical_vector_store.search_by_medical_context(
                query=query, 
                user_type=user_type
            )
            results["vector_results"] = vector_results[:3]
        
        if search_type in ["graph", "hybrid"]:
            # GraphRAG 검색
            graph_results = medical_graph_rag.graphrag_search(
                query=query,
                user_type=user_type,
                max_results=3
            )
            results["graph_results"] = graph_results
        
        # 통합 컨텍스트 생성
        context_parts = []
        
        if results["vector_results"]:
            vector_context = "\\n".join([
                f"**{result['metadata'].get('title', 'No title')}**: {result['content'][:200]}..."
                for result in results["vector_results"]
            ])
            context_parts.append(f"📚 **문서 검색 결과:**\\n{vector_context}")
        
        if results["graph_results"].get("graph_context"):
            context_parts.append(f"🔗 **지식 그래프:**\\n{results['graph_results']['graph_context']}")
        
        results["combined_context"] = "\\n\\n".join(context_parts)
        
        return {
            "success": True,
            "query": query,
            "user_type": user_type,
            "results": results,
            "summary": f"검색 완료: 벡터 {len(results['vector_results'])}개, 그래프 엔티티 {results['graph_results'].get('num_entities', 0)}개"
        }
        
    except Exception as e:
        logger.error(f"Medical knowledge search error: {e}")
        return {
            "success": False,
            "error": str(e),
            "results": {"vector_results": [], "graph_results": {}, "combined_context": ""}
        }

@tool("symptom_analysis")
def symptom_analysis(symptoms: List[str], patient_info: Dict[str, Any] = {}) -> Dict[str, Any]:
    """증상 분석 및 예비 진단"""
    try:
        # 증상 기반 지식베이스 검색
        symptom_query = " ".join(symptoms)
        search_results = medical_knowledge_search.func(
            query=f"증상 {symptom_query}",
            user_type="doctor",
            search_type="hybrid"
        )
        
        # 분석 결과 구성
        analysis = {
            "input_symptoms": symptoms,
            "patient_info": patient_info,
            "related_conditions": [],
            "recommended_tests": [],
            "urgency_level": "medium",
            "differential_diagnosis": []
        }
        
        # 검색 결과에서 관련 질환 추출
        if search_results["success"]:
            for result in search_results["results"]["vector_results"]:
                if result["metadata"].get("document_type") == "guideline":
                    analysis["related_conditions"].append({
                        "condition": result["metadata"].get("title", "Unknown"),
                        "relevance": 1.0 - result["distance"],
                        "source": result["metadata"].get("source", "Unknown")
                    })
        
        # 간단한 규칙 기반 분석
        high_risk_symptoms = ["가슴 통증", "호흡곤란", "의식 잃음", "심한 두통"]
        if any(symptom in " ".join(symptoms) for symptom in high_risk_symptoms):
            analysis["urgency_level"] = "high"
            analysis["recommended_tests"].append("응급실 방문")
        
        return {
            "success": True,
            "analysis": analysis,
            "search_context": search_results["results"]["combined_context"]
        }
        
    except Exception as e:
        logger.error(f"Symptom analysis error: {e}")
        return {
            "success": False,
            "error": str(e),
            "analysis": {}
        }

@tool("drug_interaction_check")
def drug_interaction_check(medications: List[str]) -> Dict[str, Any]:
    """약물 상호작용 확인"""
    try:
        interactions = []
        
        # 각 약물에 대한 정보 검색
        for med in medications:
            search_result = medical_knowledge_search.func(
                query=f"약물 {med} 상호작용",
                user_type="doctor",
                search_type="vector"
            )
            
            if search_result["success"] and search_result["results"]["vector_results"]:
                interactions.append({
                    "medication": med,
                    "interactions": search_result["results"]["vector_results"][0]["content"][:300],
                    "source": search_result["results"]["vector_results"][0]["metadata"].get("source", "Unknown")
                })
        
        return {
            "success": True,
            "medications": medications,
            "interactions": interactions,
            "summary": f"{len(interactions)}개 약물의 상호작용 정보 확인"
        }
        
    except Exception as e:
        logger.error(f"Drug interaction check error: {e}")
        return {
            "success": False,
            "error": str(e),
            "interactions": []
        }

class MedicalAgent:
    """서울아산병원 의료 AI 에이전트"""
    
    def __init__(self):
        # 의료 도구들
        self.tools = [
            medical_knowledge_search,
            symptom_analysis, 
            drug_interaction_check
        ]
        
        # 사용자 유형별 시스템 프롬프트
        self.system_prompts = {
            "patient": """당신은 서울아산병원의 친근한 의료 상담 AI입니다.
            
**역할:**
- 환자의 질문에 이해하기 쉽게 답변
- 의학적 정보를 안전하게 제공
- 필요시 의료진 상담 권고
- 응급 상황에서는 즉시 응급실 방문 안내

**주의사항:**
- 진단을 대신하지 않음을 명시
- 복잡한 의학 용어는 쉽게 설명
- 불안감을 주지 않도록 신중하게 표현""",

            "doctor": """당신은 서울아산병원의 전문 의료 AI입니다.
            
**역할:**
- 임상 의사결정 지원
- 최신 진료 가이드라인 제공
- 감별진단 도움
- 약물 정보 및 상호작용 확인

**기능:**
- 지식베이스에서 관련 정보 검색
- 증상 분석 및 예비 진단
- Evidence-based 답변 제공""",

            "researcher": """당신은 서울아산병원의 의료 연구 AI입니다.
            
**역할:**
- 최신 연구 동향 제공
- 데이터 분석 지원
- 연구 방법론 자문
- 통계적 해석 도움

**특징:**
- Evidence-based medicine 관점
- 연구 논문 및 데이터 활용
- 비판적 사고 지원"""
        }
        
        # LangGraph 초기화
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """LangGraph 워크플로우 구성"""
        # 워크플로우 정의
        workflow = StateGraph(AgentState)
        
        # 노드들 추가
        workflow.add_node("classifier", self._classify_intent)
        workflow.add_node("knowledge_search", self._knowledge_search_node)
        workflow.add_node("symptom_analyzer", self._symptom_analysis_node)
        workflow.add_node("response_generator", self._generate_response)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # 엣지 설정
        workflow.set_entry_point("classifier")
        
        workflow.add_conditional_edges(
            "classifier",
            self._route_intent,
            {
                "knowledge_search": "knowledge_search",
                "symptom_analysis": "symptom_analyzer",
                "direct_response": "response_generator"
            }
        )
        
        workflow.add_edge("knowledge_search", "response_generator")
        workflow.add_edge("symptom_analyzer", "response_generator") 
        workflow.add_edge("response_generator", END)
        
        return workflow.compile()
    
    def _classify_intent(self, state: AgentState) -> AgentState:
        """사용자 의도 분류"""
        try:
            last_message = state["messages"][-1]
            content = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            # 간단한 의도 분류
            content_lower = content.lower()
            
            if any(keyword in content_lower for keyword in ["증상", "아픔", "통증", "열", "기침"]):
                state["current_step"] = "증상 분석"
                state["context"]["intent"] = "symptom_analysis"
            elif any(keyword in content_lower for keyword in ["약", "처방", "복용", "상호작용"]):
                state["current_step"] = "약물 정보 검색"
                state["context"]["intent"] = "drug_inquiry"
            else:
                state["current_step"] = "의료 지식 검색"
                state["context"]["intent"] = "knowledge_search"
            
            state["reasoning"].append(f"의도 분류 완료: {state['context']['intent']}")
            
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            state["context"]["intent"] = "knowledge_search"
            state["current_step"] = "의료 지식 검색 (기본)"
        
        return state
    
    def _route_intent(self, state: AgentState) -> str:
        """의도에 따른 라우팅"""
        intent = state["context"].get("intent", "knowledge_search")
        
        if intent == "symptom_analysis":
            return "symptom_analysis"
        elif intent in ["drug_inquiry", "knowledge_search"]:
            return "knowledge_search"
        else:
            return "direct_response"
    
    def _knowledge_search_node(self, state: AgentState) -> AgentState:
        """지식베이스 검색 노드"""
        try:
            last_message = state["messages"][-1]
            query = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            # 지식 검색 수행 (도구 함수 직접 호출)
            search_result = medical_knowledge_search.func(
                query=query,
                user_type=state["user_type"],
                search_type="hybrid"
            )
            
            if search_result["success"]:
                state["knowledge_retrieved"].extend([search_result])
                state["reasoning"].append("지식베이스 검색 완료")
            else:
                state["reasoning"].append(f"지식베이스 검색 실패: {search_result.get('error', 'Unknown error')}")
            
            state["tools_used"].append("medical_knowledge_search")
            
        except Exception as e:
            logger.error(f"Knowledge search node error: {e}")
            state["reasoning"].append(f"지식베이스 검색 오류: {str(e)}")
        
        return state
    
    def _symptom_analysis_node(self, state: AgentState) -> AgentState:
        """증상 분석 노드"""
        try:
            last_message = state["messages"][-1]
            content = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            # 증상 추출 (간단한 키워드 추출)
            symptoms = []
            symptom_keywords = ["두통", "발열", "기침", "가슴 통증", "호흡곤란", "어지러움", "복통"]
            for keyword in symptom_keywords:
                if keyword in content:
                    symptoms.append(keyword)
            
            if not symptoms:
                symptoms = [content]  # 전체 내용을 증상으로 처리
            
            # 증상 분석 수행 (도구 함수 직접 호출)
            analysis_result = symptom_analysis.func(symptoms=symptoms)
            
            if analysis_result["success"]:
                state["knowledge_retrieved"].append(analysis_result)
                state["reasoning"].append(f"증상 분석 완료: {len(symptoms)}개 증상")
            else:
                state["reasoning"].append(f"증상 분석 실패: {analysis_result.get('error', 'Unknown error')}")
            
            state["tools_used"].append("symptom_analysis")
            
        except Exception as e:
            logger.error(f"Symptom analysis node error: {e}")
            state["reasoning"].append(f"증상 분석 오류: {str(e)}")
        
        return state
    
    def _generate_response(self, state: AgentState) -> AgentState:
        """응답 생성 노드"""
        try:
            # 컨텍스트 수집
            context_parts = []
            
            # 지식베이스 검색 결과 추가
            for knowledge in state["knowledge_retrieved"]:
                if "results" in knowledge and knowledge["results"].get("combined_context"):
                    context_parts.append(knowledge["results"]["combined_context"])
                elif "analysis" in knowledge:
                    context_parts.append(f"**증상 분석:**\\n{json.dumps(knowledge['analysis'], ensure_ascii=False, indent=2)}")
            
            combined_context = "\\n\\n".join(context_parts) if context_parts else "관련 정보를 찾지 못했습니다."
            
            # 시스템 프롬프트 선택
            system_prompt = self.system_prompts.get(state["user_type"], self.system_prompts["patient"])
            
            # 사용자 질의
            last_message = state["messages"][-1]
            user_query = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            # 전체 프롬프트 구성
            full_prompt = f"""{system_prompt}

**검색된 의료 정보:**
{combined_context}

**사용자 질의:** {user_query}

**지침:**
- 위의 검색 결과를 바탕으로 정확하고 도움이 되는 답변 제공
- 사용자 유형({state["user_type"]})에 맞는 수준으로 설명
- 불확실한 정보는 추가 상담을 권유
- 응급 상황 시에는 즉시 의료진 상담 안내

**답변:**"""
            
            # Qwen 모델로 응답 생성
            if qwen_model.model and qwen_model.tokenizer:
                response = qwen_model.generate_response(
                    query=full_prompt,
                    user_type=state["user_type"],
                    max_length=1000
                )
            else:
                response = f"""죄송합니다. 현재 AI 모델이 로드되지 않아 기본 응답을 제공합니다.

**검색 결과 요약:**
{combined_context[:500]}...

**권고사항:**
- 정확한 진단을 위해 전문의 상담을 받으시기 바랍니다.
- 응급 상황 시에는 즉시 응급실을 방문하세요.
- 추가 질문이 있으시면 언제든 문의하세요."""
            
            # AI 응답 메시지 추가
            ai_message = AIMessage(content=response)
            state["messages"].append(ai_message)
            
            state["current_step"] = "응답 생성 완료"
            state["reasoning"].append("AI 응답 생성 완료")
            
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            error_response = "죄송합니다. 응답 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
            ai_message = AIMessage(content=error_response)
            state["messages"].append(ai_message)
            state["reasoning"].append(f"응답 생성 오류: {str(e)}")
        
        return state
    
    async def process_query(self, 
                           query: str, 
                           user_type: str = "patient", 
                           session_id: str = None) -> Dict[str, Any]:
        """사용자 질의 처리"""
        try:
            session_id = session_id or f"session_{uuid.uuid4().hex[:8]}"
            
            # 초기 상태 설정
            initial_state: AgentState = {
                "messages": [HumanMessage(content=query)],
                "user_type": user_type,
                "session_id": session_id,
                "context": {},
                "tools_used": [],
                "knowledge_retrieved": [],
                "current_step": "시작",
                "reasoning": []
            }
            
            # LangGraph 실행
            final_state = await self.graph.ainvoke(initial_state)
            
            # 결과 정리
            ai_response = final_state["messages"][-1].content if final_state["messages"] else "응답을 생성할 수 없습니다."
            
            return {
                "response": ai_response,
                "session_id": session_id,
                "user_type": user_type,
                "tools_used": final_state["tools_used"],
                "reasoning": final_state["reasoning"],
                "knowledge_count": len(final_state["knowledge_retrieved"]),
                "current_step": final_state["current_step"]
            }
            
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return {
                "response": "죄송합니다. 질의 처리 중 오류가 발생했습니다.",
                "session_id": session_id,
                "user_type": user_type,
                "tools_used": [],
                "reasoning": [f"처리 오류: {str(e)}"],
                "knowledge_count": 0,
                "current_step": "오류 발생"
            }

# 전역 에이전트 인스턴스
medical_agent = MedicalAgent()

if __name__ == "__main__":
    # 테스트 실행
    import asyncio
    
    async def test_agent():
        # 테스트 질의들
        test_queries = [
            ("고혈압이 있는데 어떤 약을 복용해야 하나요?", "patient"),
            ("두통과 발열 증상이 있습니다", "patient"),
            ("ACE 억제제와 ARB의 차이점을 알려주세요", "doctor")
        ]
        
        for query, user_type in test_queries:
            print(f"\\n질의: {query} (사용자: {user_type})")
            result = await medical_agent.process_query(query, user_type)
            print(f"응답: {result['response'][:200]}...")
            print(f"사용된 도구: {result['tools_used']}")
            print(f"지식 개수: {result['knowledge_count']}")
    
    asyncio.run(test_agent())