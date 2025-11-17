"""
서울아산병원 AI 플랫폼 - GraphRAG 시스템
그래프 기반 검색 증강 생성 (Retrieval Augmented Generation)
"""
from langchain_community.graphs import Neo4jGraph
from langchain_core.documents import Document
from langchain_community.vectorstores import Neo4jVector
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import networkx as nx
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
import uuid

logger = logging.getLogger(__name__)

class MedicalGraphRAG:
    """의료 도메인 GraphRAG 시스템"""
    
    def __init__(self, 
                 neo4j_url: str = "neo4j://localhost:7687",
                 neo4j_username: str = "neo4j", 
                 neo4j_password: str = "password",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        GraphRAG 시스템 초기화
        
        Args:
            neo4j_url: Neo4j 데이터베이스 URL
            neo4j_username: Neo4j 사용자명
            neo4j_password: Neo4j 비밀번호
            embedding_model: 임베딩 모델명
        """
        self.neo4j_url = neo4j_url
        self.neo4j_username = neo4j_username
        self.neo4j_password = neo4j_password
        self.embedding_model_name = embedding_model
        
        # Neo4j 연결 (실제 환경에서는 활성화)
        self.graph = None
        self.vector_store = None
        
        # NetworkX 그래프 (Neo4j 대신 메모리 기반)
        self.knowledge_graph = nx.MultiDiGraph()
        
        # 임베딩 모델
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # 텍스트 분할기
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len
        )
        
        # 의료 엔티티 및 관계 정의
        self.medical_entities = {
            'Disease': ['질병', '병명', '질환', '증후군'],
            'Symptom': ['증상', '징후', '소견'], 
            'Treatment': ['치료', '처치', '요법', '수술'],
            'Drug': ['약물', '의약품', '처방약', '약'],
            'Department': ['진료과', '과', '센터'],
            'Doctor': ['의사', '의료진', '전문의'],
            'Patient': ['환자', '병자'],
            'Anatomy': ['해부학', '장기', '기관', '조직'],
            'Test': ['검사', '검진', '진단'],
            'Equipment': ['의료기기', '장비', '기구']
        }
        
        self.medical_relations = [
            'TREATS', 'CAUSES', 'SYMPTOMS_OF', 'PRESCRIBED_FOR', 
            'DIAGNOSED_BY', 'PERFORMED_BY', 'WORKS_AT', 'SPECIALIZES_IN',
            'PART_OF', 'RELATED_TO', 'USES', 'PREVENTS'
        ]
        
        self.entity_embeddings = {}  # 엔티티 임베딩 캐시
        
    def _try_neo4j_connection(self) -> bool:
        """Neo4j 연결 시도 (선택적)"""
        try:
            self.graph = Neo4jGraph(
                url=self.neo4j_url,
                username=self.neo4j_username,
                password=self.neo4j_password
            )
            
            self.vector_store = Neo4jVector.from_existing_graph(
                self.embeddings,
                graph=self.graph,
                node_label="Document",
                text_node_properties=["text"],
                embedding_node_property="embedding"
            )
            
            logger.info("Neo4j 연결 성공")
            return True
            
        except Exception as e:
            logger.warning(f"Neo4j 연결 실패, 메모리 그래프 사용: {e}")
            return False
    
    def extract_medical_entities(self, text: str) -> List[Dict[str, Any]]:
        """텍스트에서 의료 엔티티 추출 (간단한 키워드 기반)"""
        entities = []
        
        for entity_type, keywords in self.medical_entities.items():
            for keyword in keywords:
                if keyword in text.lower():
                    entity_id = f"{entity_type}_{uuid.uuid4().hex[:8]}"
                    entities.append({
                        'id': entity_id,
                        'type': entity_type,
                        'name': keyword,
                        'context': text[:200],  # 컨텍스트 정보
                        'confidence': 0.8
                    })
        
        return entities
    
    def extract_medical_relations(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """텍스트와 엔티티에서 의료 관계 추출"""
        relations = []
        
        # 간단한 규칙 기반 관계 추출
        text_lower = text.lower()
        
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities):
                if i >= j:
                    continue
                
                # 관계 패턴 매칭
                if entity1['type'] == 'Drug' and entity2['type'] == 'Disease':
                    if any(word in text_lower for word in ['치료', '처방', '사용']):
                        relations.append({
                            'source': entity1['id'],
                            'target': entity2['id'], 
                            'type': 'TREATS',
                            'confidence': 0.7
                        })
                
                elif entity1['type'] == 'Symptom' and entity2['type'] == 'Disease':
                    if any(word in text_lower for word in ['증상', '나타남', '발생']):
                        relations.append({
                            'source': entity2['id'],
                            'target': entity1['id'],
                            'type': 'SYMPTOMS_OF', 
                            'confidence': 0.8
                        })
                
                elif entity1['type'] == 'Doctor' and entity2['type'] == 'Department':
                    if any(word in text_lower for word in ['소속', '근무', '전문']):
                        relations.append({
                            'source': entity1['id'],
                            'target': entity2['id'],
                            'type': 'WORKS_AT',
                            'confidence': 0.9
                        })
        
        return relations
    
    def build_knowledge_graph(self, documents: List[Dict[str, Any]]):
        """의료 문서들로부터 지식 그래프 구축"""
        try:
            logger.info(f"지식 그래프 구축 시작: {len(documents)}개 문서")
            
            for doc in documents:
                content = doc.get('content', '')
                doc_id = doc.get('id', str(uuid.uuid4()))
                
                # 텍스트 청킹
                chunks = self.text_splitter.split_text(content)
                
                for i, chunk in enumerate(chunks):
                    # 엔티티 추출
                    entities = self.extract_medical_entities(chunk)
                    
                    # 그래프에 엔티티 추가
                    for entity in entities:
                        self.knowledge_graph.add_node(
                            entity['id'],
                            type=entity['type'],
                            name=entity['name'],
                            document_id=doc_id,
                            chunk_index=i,
                            context=entity['context'],
                            confidence=entity['confidence'],
                            created_at=datetime.now().isoformat()
                        )
                        
                        # 엔티티 임베딩 생성 및 캐시
                        if entity['id'] not in self.entity_embeddings:
                            embedding_text = f"{entity['name']} {entity['context']}"
                            embedding = self.embeddings.embed_query(embedding_text)
                            self.entity_embeddings[entity['id']] = embedding
                    
                    # 관계 추출 및 추가
                    relations = self.extract_medical_relations(chunk, entities)
                    for relation in relations:
                        self.knowledge_graph.add_edge(
                            relation['source'],
                            relation['target'],
                            type=relation['type'],
                            confidence=relation['confidence'],
                            document_id=doc_id,
                            chunk_index=i,
                            created_at=datetime.now().isoformat()
                        )
            
            # 그래프 통계
            num_nodes = self.knowledge_graph.number_of_nodes()
            num_edges = self.knowledge_graph.number_of_edges()
            logger.info(f"지식 그래프 구축 완료: {num_nodes}개 노드, {num_edges}개 관계")
            
        except Exception as e:
            logger.error(f"지식 그래프 구축 오류: {e}")
    
    def graph_search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """그래프 기반 검색"""
        try:
            query_embedding = self.embeddings.embed_query(query)
            
            # 엔티티와의 유사도 계산
            similarities = []
            for entity_id, entity_embedding in self.entity_embeddings.items():
                # 코사인 유사도 계산 (간단한 내적 근사)
                similarity = sum(a * b for a, b in zip(query_embedding, entity_embedding))
                similarities.append((entity_id, similarity))
            
            # 유사도 순으로 정렬
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # 상위 k개 엔티티와 관련된 서브그래프 추출
            results = []
            for entity_id, similarity in similarities[:k]:
                if entity_id in self.knowledge_graph:
                    node_data = self.knowledge_graph.nodes[entity_id]
                    
                    # 연관된 엔티티들 찾기
                    neighbors = []
                    for neighbor in self.knowledge_graph.neighbors(entity_id):
                        edge_data = self.knowledge_graph[entity_id][neighbor]
                        neighbor_data = self.knowledge_graph.nodes[neighbor]
                        neighbors.append({
                            'entity': neighbor_data,
                            'relation': list(edge_data.values())[0] if edge_data else {}
                        })
                    
                    results.append({
                        'entity': node_data,
                        'similarity': similarity,
                        'neighbors': neighbors[:3],  # 상위 3개 이웃만
                        'entity_id': entity_id
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"그래프 검색 오류: {e}")
            return []
    
    def generate_graph_context(self, search_results: List[Dict[str, Any]]) -> str:
        """검색 결과로부터 그래프 컨텍스트 생성"""
        try:
            context_parts = []
            
            for result in search_results:
                entity = result['entity']
                neighbors = result['neighbors']
                
                # 엔티티 정보
                entity_context = f"**{entity['type']}**: {entity['name']}"
                if entity.get('context'):
                    entity_context += f" - {entity['context'][:100]}..."
                
                # 연관 관계 정보
                if neighbors:
                    relations = []
                    for neighbor in neighbors:
                        neighbor_entity = neighbor['entity']
                        relation = neighbor['relation']
                        relation_text = f"{relation.get('type', 'RELATED')} {neighbor_entity['name']}"
                        relations.append(relation_text)
                    
                    if relations:
                        entity_context += f"\n  관련: {', '.join(relations)}"
                
                context_parts.append(entity_context)
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"그래프 컨텍스트 생성 오류: {e}")
            return ""
    
    def graphrag_search(self, 
                       query: str, 
                       user_type: str = 'patient',
                       max_results: int = 5) -> Dict[str, Any]:
        """GraphRAG 통합 검색"""
        try:
            # 1. 그래프 기반 검색
            graph_results = self.graph_search(query, k=max_results * 2)
            
            # 2. 사용자 타입별 결과 필터링
            filtered_results = []
            for result in graph_results:
                entity_type = result['entity']['type']
                confidence = result['entity']['confidence']
                
                # 사용자 타입별 엔티티 우선순위
                if user_type == 'patient':
                    if entity_type in ['Disease', 'Symptom', 'Treatment', 'Drug'] and confidence > 0.6:
                        filtered_results.append(result)
                elif user_type == 'doctor':
                    if entity_type in ['Disease', 'Treatment', 'Drug', 'Test', 'Department'] and confidence > 0.5:
                        filtered_results.append(result)
                elif user_type == 'researcher':
                    if confidence > 0.4:  # 연구자는 모든 엔티티 허용
                        filtered_results.append(result)
                
                if len(filtered_results) >= max_results:
                    break
            
            # 3. 그래프 컨텍스트 생성
            graph_context = self.generate_graph_context(filtered_results)
            
            # 4. 결과 요약
            return {
                'query': query,
                'user_type': user_type,
                'graph_results': filtered_results,
                'graph_context': graph_context,
                'num_entities': len(filtered_results),
                'graph_stats': {
                    'total_nodes': self.knowledge_graph.number_of_nodes(),
                    'total_edges': self.knowledge_graph.number_of_edges()
                }
            }
            
        except Exception as e:
            logger.error(f"GraphRAG 검색 오류: {e}")
            return {
                'query': query,
                'user_type': user_type,
                'graph_results': [],
                'graph_context': '',
                'num_entities': 0,
                'graph_stats': {'total_nodes': 0, 'total_edges': 0}
            }
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """그래프 통계 정보 반환"""
        try:
            # 엔티티 타입별 개수
            entity_counts = {}
            for node_id in self.knowledge_graph.nodes():
                node_data = self.knowledge_graph.nodes[node_id]
                entity_type = node_data.get('type', 'Unknown')
                entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
            
            # 관계 타입별 개수
            relation_counts = {}
            for edge in self.knowledge_graph.edges(data=True):
                relation_type = edge[2].get('type', 'Unknown')
                relation_counts[relation_type] = relation_counts.get(relation_type, 0) + 1
            
            return {
                'total_nodes': self.knowledge_graph.number_of_nodes(),
                'total_edges': self.knowledge_graph.number_of_edges(),
                'entity_counts': entity_counts,
                'relation_counts': relation_counts,
                'avg_degree': sum(dict(self.knowledge_graph.degree()).values()) / max(self.knowledge_graph.number_of_nodes(), 1)
            }
            
        except Exception as e:
            logger.error(f"그래프 통계 오류: {e}")
            return {}

# 전역 GraphRAG 인스턴스
medical_graph_rag = MedicalGraphRAG()

# 샘플 의료 지식 그래프 데이터
SAMPLE_GRAPH_DOCUMENTS = [
    {
        'id': 'doc_hypertension',
        'title': '고혈압 진료 가이드라인',
        'content': '''고혈압은 심혈관 질환의 주요 위험 인자입니다. 
        김철수 의사는 심장내과에서 고혈압 환자를 전문으로 진료합니다.
        ACE 억제제와 ARB는 고혈압 치료에 사용되는 주요 약물입니다.
        두통과 어지러움은 고혈압의 일반적인 증상입니다.
        혈압 측정은 고혈압 진단을 위한 핵심 검사입니다.'''
    },
    {
        'id': 'doc_diabetes',
        'title': '당뇨병 관리 지침', 
        'content': '''제2형 당뇨병은 인슐린 저항성으로 인해 발생합니다.
        이영희 의사는 내분비내과에서 당뇨병 환자를 치료합니다.
        메트포르민은 당뇨병 치료의 1차 약물입니다.
        다뇨와 다음은 당뇨병의 전형적인 증상입니다.
        혈당 검사와 당화혈색소 검사가 당뇨병 진단에 필요합니다.'''
    },
    {
        'id': 'doc_cardiology',
        'title': '심장내과 진료 프로토콜',
        'content': '''심전도는 심장 질환 진단의 기본 검사입니다.
        관상동맥 조영술은 심혈관 센터에서 시행됩니다.
        스텐트 시술은 협착된 관상동맥 치료에 사용됩니다.
        가슴 통증은 심장 질환의 주요 증상입니다.
        심장초음파는 심기능 평가를 위한 중요한 검사입니다.'''
    }
]

def initialize_graph_knowledge():
    """샘플 그래프 지식 데이터 초기화"""
    try:
        logger.info("의료 지식 그래프 초기화 시작...")
        medical_graph_rag.build_knowledge_graph(SAMPLE_GRAPH_DOCUMENTS)
        
        stats = medical_graph_rag.get_graph_statistics()
        logger.info(f"지식 그래프 초기화 완료 - 통계: {stats}")
        
    except Exception as e:
        logger.error(f"그래프 지식 초기화 오류: {e}")

if __name__ == "__main__":
    # 테스트 실행
    initialize_graph_knowledge()
    
    # GraphRAG 검색 테스트
    test_query = "고혈압 치료 약물"
    result = medical_graph_rag.graphrag_search(test_query, user_type='doctor')
    
    print(f"\nGraphRAG 검색 쿼리: {test_query}")
    print(f"검색 결과: {result['num_entities']}개 엔티티")
    print(f"그래프 컨텍스트:\n{result['graph_context']}")