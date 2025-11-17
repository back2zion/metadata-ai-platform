from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, Any
import uvicorn
import logging
from qwen_model import qwen_model
from vector_store import medical_vector_store, initialize_sample_data
from graph_rag import medical_graph_rag, initialize_graph_knowledge
from langgraph_agent import medical_agent

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="서울아산병원 AI 의료 플랫폼",
    description="LangChain 기반 의료 AI 데이터 분석 플랫폼",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 개발 서버
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 세션 상태 저장소 (실제 환경에서는 Redis 사용)
sessions = {}

# 모델 로드 상태
model_loaded = False

@app.on_event("startup")
async def startup_event():
    """서버 시작시 백그라운드에서 모델 로드"""
    logger.info("Server starting up...")
    # 백그라운드에서 모델 로드 (서버 시작을 블로킹하지 않음)
    asyncio.create_task(load_model_background())

async def load_model_background():
    """백그라운드에서 모델 및 지식베이스 로드"""
    global model_loaded
    logger.info("Starting to load Qwen model and knowledge bases in background...")
    try:
        await asyncio.sleep(1)  # 서버가 먼저 시작되도록 잠시 대기
        
        # Qwen 모델 로드
        success = qwen_model.load_model()
        if success:
            model_loaded = True
            logger.info("Qwen model loaded successfully")
        else:
            logger.error("Failed to load Qwen model")
        
        # 벡터 스토어 초기화
        logger.info("Initializing vector store...")
        initialize_sample_data()
        
        # GraphRAG 초기화
        logger.info("Initializing GraphRAG knowledge base...")
        initialize_graph_knowledge()
        
        logger.info("All background initialization completed")
        
    except Exception as e:
        logger.error(f"Error in background initialization: {e}")

@app.get("/")
async def root():
    return {"message": "서울아산병원 AI 의료 플랫폼 API"}

@app.get("/api/v1/streaming/session/{session_id}/status")
async def get_session_status(session_id: str):
    """세션 상태 확인"""
    return {
        "status": "connected", 
        "session_id": session_id,
        "model_loaded": model_loaded,
        "model_name": "Qwen/Qwen3-8B" if model_loaded else "Mock Model"
    }

async def generate_medical_response(query: str, session_id: str, user_type: str):
    """의료 AI 응답 생성 (스트리밍) - GraphRAG 및 벡터 검색 통합"""
    
    # 세션 시작 이벤트
    yield f"data: {json.dumps({'event_type': 'session_start', 'data': {'session_id': session_id}, 'timestamp': datetime.now().isoformat(), 'session_id': session_id})}\n\n"
    await asyncio.sleep(0.5)
    
    # GraphRAG 검색 수행
    yield f"data: {json.dumps({'event_type': 'step_update', 'data': {'step': 'GraphRAG 지식 그래프 검색 중...'}, 'timestamp': datetime.now().isoformat(), 'session_id': session_id})}\n\n"
    await asyncio.sleep(0.3)
    
    try:
        # GraphRAG 검색
        graph_results = medical_graph_rag.graphrag_search(query, user_type=user_type, max_results=3)
        graph_context = graph_results.get('graph_context', '')
        
        # 벡터 검색 수행
        yield f"data: {json.dumps({'event_type': 'step_update', 'data': {'step': '벡터 데이터베이스 검색 중...'}, 'timestamp': datetime.now().isoformat(), 'session_id': session_id})}\n\n"
        await asyncio.sleep(0.3)
        
        vector_results = medical_vector_store.search_by_medical_context(query, user_type=user_type)
        vector_context = ""
        if vector_results:
            vector_context = "\\n\\n".join([
                f"**{result['metadata'].get('title', 'No title')}**: {result['content'][:200]}..."
                for result in vector_results[:3]
            ])
        
        # 통합 컨텍스트 구성
        combined_context = ""
        if graph_context:
            combined_context += f"**그래프 지식:**\\n{graph_context}\\n\\n"
        if vector_context:
            combined_context += f"**문서 검색 결과:**\\n{vector_context}\\n\\n"
        
        # 메모리 컨텍스트 이벤트 (검색 결과 포함)
        memory_context = {
            "previous_symptoms": ["두통", "발열"] if "증상" in query else [],
            "medication_history": ["타이레놀"] if "약" in query else [],
            "message_count": 1,
            "graph_entities": len(graph_results.get('graph_results', [])),
            "vector_docs": len(vector_results),
            "knowledge_context": combined_context[:500] + "..." if len(combined_context) > 500 else combined_context
        }
        yield f"data: {json.dumps({'event_type': 'memory_context', 'data': memory_context, 'timestamp': datetime.now().isoformat(), 'session_id': session_id})}\n\n"
        await asyncio.sleep(0.3)
        
    except Exception as e:
        logger.error(f"Knowledge base search error: {e}")
        # 기본 메모리 컨텍스트
        memory_context = {
            "previous_symptoms": ["두통", "발열"] if "증상" in query else [],
            "medication_history": ["타이레놀"] if "약" in query else [],
            "message_count": 1,
            "search_error": str(e)
        }
        yield f"data: {json.dumps({'event_type': 'memory_context', 'data': memory_context, 'timestamp': datetime.now().isoformat(), 'session_id': session_id})}\n\n"
        await asyncio.sleep(0.3)
    
    # 처리 단계별 업데이트
    if model_loaded:
        steps = [
            "사용자 질의 분석 중...",
            "Qwen 3 8B 모델 로딩 중...",
            "의료 컨텍스트 적용 중...",
            "AI 응답 생성 중..."
        ]
    else:
        steps = [
            "사용자 질의 분석 중...",
            "모의 응답 모드로 처리 중...",
            "응답 생성 중..."
        ]
    
    for i, step in enumerate(steps):
        yield f"data: {json.dumps({'event_type': 'step_update', 'data': {'step': step}, 'timestamp': datetime.now().isoformat(), 'session_id': session_id})}\n\n"
        await asyncio.sleep(0.5)
    
    # LangGraph 에이전트 사용 또는 기본 응답
    if model_loaded:
        logger.info(f"Generating response with LangGraph agent for query: {query}")
        try:
            # LangGraph 에이전트로 처리
            yield f"data: {json.dumps({'event_type': 'step_update', 'data': {'step': 'LangGraph 에이전트 처리 중...'}, 'timestamp': datetime.now().isoformat(), 'session_id': session_id})}\n\n"
            await asyncio.sleep(0.3)
            
            agent_result = await medical_agent.process_query(
                query=query,
                user_type=user_type,
                session_id=session_id
            )
            
            # 에이전트 처리 과정을 스트리밍으로 전송
            if agent_result.get('tools_used'):
                yield f"data: {json.dumps({'event_type': 'step_update', 'data': {'step': f'도구 사용 완료: {', '.join(agent_result['tools_used'])}'}, 'timestamp': datetime.now().isoformat(), 'session_id': session_id})}\n\n"
                await asyncio.sleep(0.2)
            
            # 응답을 토큰 단위로 스트리밍
            response_text = agent_result.get('response', '응답을 생성할 수 없습니다.')
            words = response_text.split()
            for word in words:
                yield f"data: {json.dumps({'event_type': 'token', 'data': {'content': word + ' '}, 'timestamp': datetime.now().isoformat(), 'session_id': session_id})}\n\n"
                await asyncio.sleep(0.05)
                
        except Exception as e:
            logger.error(f"Error with LangGraph agent: {e}")
            error_msg = f"LangGraph 에이전트 처리 중 오류가 발생했습니다: {str(e)}"
            yield f"data: {json.dumps({'event_type': 'token', 'data': {'content': error_msg}, 'timestamp': datetime.now().isoformat(), 'session_id': session_id})}\n\n"
    else:
        # 모의 응답 (모델이 로드되지 않은 경우)
        logger.info("Using mock response - Qwen model not loaded")
        
        if user_type == "doctor":
            response_text = f"""안녕하세요. 의료진님의 질의 '{query}'에 대한 임상적 분석을 제공드립니다.

🏥 **임상 진단 지원**
- 환자의 증상을 종합적으로 분석한 결과
- 감별진단 항목들을 우선순위에 따라 정리
- 추가 검사가 필요한 항목들 제안

📊 **데이터 기반 인사이트**
- 유사 케이스 분석 결과
- 치료 효과 예측 모델
- 약물 상호작용 체크

⚠️ *현재 모의 응답 모드입니다. 실제 Qwen 3 8B 모델 로딩이 필요합니다.*"""
        
        elif user_type == "researcher":
            response_text = f"""연구자님의 질의 '{query}'에 대한 연구 분석을 제공합니다.

🔬 **연구 데이터 분석**
- 관련 의료 논문 및 연구 동향
- 통계적 분석 결과 및 p-value
- 코호트 연구 데이터 비교

📈 **연구 인사이트**
- 최신 임상시험 결과
- 메타분석 데이터
- 연구 방법론 제안

⚠️ *현재 모의 응답 모드입니다. 실제 Qwen 3 8B 모델 로딩이 필요합니다.*"""
        
        else:  # patient
            response_text = f"""안녕하세요! 환자분의 질문 '{query}'에 대해 친절하게 답변드리겠습니다.

💊 **건강 정보 안내**
- 증상에 대한 일반적인 설명
- 생활 속 관리 방법
- 언제 병원을 방문해야 하는지

⚕️ **주의사항**
- 이 정보는 의학적 조언을 대체할 수 없습니다
- 심각한 증상이 있다면 즉시 의료진과 상담하세요
- 정확한 진단은 전문의의 진료가 필요합니다

⚠️ *현재 모의 응답 모드입니다. 실제 Qwen 3 8B 모델 로딩이 필요합니다.*"""
        
        # 응답 텍스트를 토큰 단위로 스트리밍
        words = response_text.split()
        for word in words:
            yield f"data: {json.dumps({'event_type': 'token', 'data': {'content': word + ' '}, 'timestamp': datetime.now().isoformat(), 'session_id': session_id})}\n\n"
            await asyncio.sleep(0.1)
    
    # 완료 이벤트
    final_memory = memory_context.copy()
    final_memory["last_query"] = query
    final_memory["message_count"] += 1
    
    yield f"data: {json.dumps({'event_type': 'completion', 'data': {'final_memory': final_memory}, 'timestamp': datetime.now().isoformat(), 'session_id': session_id})}\n\n"

@app.post("/api/v1/streaming/medical-query")
async def stream_medical_query(request: Dict[Any, Any]):
    """의료 질의 스트리밍 처리"""
    query = request.get("query", "")
    session_id = request.get("session_id", f"session_{int(time.time())}")
    user_type = request.get("user_type", "patient")
    
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    return StreamingResponse(
        generate_medical_response(query, session_id, user_type),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@app.get("/api/v1/streaming/test-stream")
async def test_stream():
    """스트리밍 테스트"""
    async def generate():
        for i in range(5):
            yield f"data: 테스트 메시지 {i+1}\n\n"
            await asyncio.sleep(1)
    
    return StreamingResponse(generate(), media_type="text/plain")

@app.get("/api/v1/knowledge/vector-stats")
async def get_vector_stats():
    """벡터 스토어 통계"""
    try:
        stats = medical_vector_store.get_collection_stats()
        return {
            "status": "success",
            "vector_store_stats": stats,
            "total_documents": sum(stats.values())
        }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "vector_store_stats": {}
        }

@app.get("/api/v1/knowledge/graph-stats")
async def get_graph_stats():
    """그래프 스토어 통계"""
    try:
        stats = medical_graph_rag.get_graph_statistics()
        return {
            "status": "success",
            "graph_stats": stats
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e), 
            "graph_stats": {}
        }

@app.post("/api/v1/knowledge/vector-search")
async def vector_search(request: Dict[Any, Any]):
    """벡터 검색 테스트"""
    try:
        query = request.get("query", "")
        user_type = request.get("user_type", "patient")
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        results = medical_vector_store.search_by_medical_context(query, user_type=user_type)
        
        return {
            "status": "success",
            "query": query,
            "user_type": user_type,
            "num_results": len(results),
            "results": results
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "results": []
        }

@app.post("/api/v1/knowledge/graph-search")  
async def graph_search(request: Dict[Any, Any]):
    """GraphRAG 검색 테스트"""
    try:
        query = request.get("query", "")
        user_type = request.get("user_type", "patient")
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        results = medical_graph_rag.graphrag_search(query, user_type=user_type)
        
        return {
            "status": "success",
            "query": query,
            "user_type": user_type,
            "graph_results": results
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "graph_results": {}
        }

@app.post("/api/v1/agent/query")
async def agent_query(request: Dict[Any, Any]):
    """LangGraph 에이전트 질의 처리"""
    try:
        query = request.get("query", "")
        user_type = request.get("user_type", "patient")
        session_id = request.get("session_id", f"session_{int(time.time())}")
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        result = await medical_agent.process_query(
            query=query,
            user_type=user_type,
            session_id=session_id
        )
        
        return {
            "status": "success",
            "query": query,
            "user_type": user_type,
            "session_id": session_id,
            "agent_result": result
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "agent_result": {}
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)