"""
서울아산병원 AI 플랫폼 - ChromaDB 벡터 스토어
의료 문서 임베딩 및 검색을 위한 벡터 데이터베이스 관리
"""
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os
import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MedicalVectorStore:
    """의료 데이터용 벡터 스토어 클래스"""
    
    def __init__(self, 
                 persist_directory: str = "./chroma_medical_db",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        ChromaDB 벡터 스토어 초기화
        
        Args:
            persist_directory: ChromaDB 데이터 저장 디렉토리
            embedding_model: 임베딩 모델명
        """
        self.persist_directory = persist_directory
        self.embedding_model_name = embedding_model
        
        # ChromaDB 클라이언트 설정
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                allow_reset=True,
                anonymized_telemetry=False
            )
        )
        
        # 임베딩 모델 설정
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # 텍스트 분할기 설정
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # 컬렉션들 초기화
        self.collections = {
            'medical_documents': None,
            'clinical_guidelines': None,
            'research_papers': None,
            'patient_records': None,
            'drug_information': None
        }
        
        self._initialize_collections()
    
    def _initialize_collections(self):
        """벡터 스토어 컬렉션들 초기화"""
        try:
            for collection_name in self.collections.keys():
                try:
                    collection = self.client.get_collection(collection_name)
                    logger.info(f"기존 컬렉션 로드됨: {collection_name}")
                except:
                    collection = self.client.create_collection(
                        name=collection_name,
                        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                            model_name=self.embedding_model_name
                        ),
                        metadata={"created_at": datetime.now().isoformat()}
                    )
                    logger.info(f"새 컬렉션 생성됨: {collection_name}")
                
                self.collections[collection_name] = collection
                
        except Exception as e:
            logger.error(f"컬렉션 초기화 오류: {e}")
    
    def add_documents(self, 
                     documents: List[Dict[str, Any]], 
                     collection_name: str = 'medical_documents') -> List[str]:
        """
        문서들을 벡터 스토어에 추가
        
        Args:
            documents: 추가할 문서들 리스트
            collection_name: 대상 컬렉션명
            
        Returns:
            추가된 문서들의 ID 리스트
        """
        try:
            collection = self.collections.get(collection_name)
            if not collection:
                raise ValueError(f"컬렉션을 찾을 수 없음: {collection_name}")
            
            ids = []
            texts = []
            metadatas = []
            
            for doc in documents:
                # 문서 텍스트 분할
                doc_text = doc.get('content', '')
                chunks = self.text_splitter.split_text(doc_text)
                
                for i, chunk in enumerate(chunks):
                    doc_id = f"{doc.get('id', str(uuid.uuid4()))}_{i}"
                    ids.append(doc_id)
                    texts.append(chunk)
                    
                    metadata = {
                        'source': doc.get('source', 'unknown'),
                        'title': doc.get('title', ''),
                        'document_type': doc.get('type', 'general'),
                        'chunk_index': i,
                        'total_chunks': len(chunks),
                        'created_at': datetime.now().isoformat(),
                        'hospital_department': doc.get('department', ''),
                        'medical_specialty': doc.get('specialty', ''),
                        'confidence_level': doc.get('confidence', 1.0)
                    }
                    metadatas.append(metadata)
            
            # ChromaDB에 추가
            collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"{len(ids)}개 청크를 {collection_name}에 추가함")
            return ids
            
        except Exception as e:
            logger.error(f"문서 추가 오류: {e}")
            return []
    
    def similarity_search(self, 
                         query: str, 
                         collection_name: str = 'medical_documents',
                         k: int = 5,
                         filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        유사도 검색 수행
        
        Args:
            query: 검색 쿼리
            collection_name: 검색할 컬렉션명  
            k: 반환할 결과 수
            filter_criteria: 메타데이터 필터링 조건
            
        Returns:
            검색 결과 리스트
        """
        try:
            collection = self.collections.get(collection_name)
            if not collection:
                raise ValueError(f"컬렉션을 찾을 수 없음: {collection_name}")
            
            # 검색 수행
            results = collection.query(
                query_texts=[query],
                n_results=k,
                where=filter_criteria
            )
            
            # 결과 정리
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    result = {
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        'id': results['ids'][0][i] if results['ids'] and results['ids'][0] else '',
                        'distance': results['distances'][0][i] if results['distances'] and results['distances'][0] else 0.0
                    }
                    search_results.append(result)
            
            logger.info(f"검색 완료: {len(search_results)}개 결과 반환")
            return search_results
            
        except Exception as e:
            logger.error(f"검색 오류: {e}")
            return []
    
    def add_medical_knowledge(self, knowledge_base: List[Dict[str, Any]]):
        """
        의료 지식베이스 데이터 추가
        
        Args:
            knowledge_base: 의료 지식 데이터 리스트
        """
        try:
            # 진료 가이드라인
            guidelines = [kb for kb in knowledge_base if kb.get('type') == 'guideline']
            if guidelines:
                self.add_documents(guidelines, 'clinical_guidelines')
            
            # 연구 논문
            papers = [kb for kb in knowledge_base if kb.get('type') == 'research']
            if papers:
                self.add_documents(papers, 'research_papers')
            
            # 약물 정보
            drugs = [kb for kb in knowledge_base if kb.get('type') == 'drug']
            if drugs:
                self.add_documents(drugs, 'drug_information')
            
            # 일반 의료 문서
            general_docs = [kb for kb in knowledge_base if kb.get('type') not in ['guideline', 'research', 'drug']]
            if general_docs:
                self.add_documents(general_docs, 'medical_documents')
                
            logger.info(f"의료 지식베이스 {len(knowledge_base)}개 문서 처리 완료")
            
        except Exception as e:
            logger.error(f"의료 지식베이스 추가 오류: {e}")
    
    def get_collection_stats(self) -> Dict[str, int]:
        """각 컬렉션의 문서 수 반환"""
        stats = {}
        try:
            for name, collection in self.collections.items():
                if collection:
                    stats[name] = collection.count()
                else:
                    stats[name] = 0
        except Exception as e:
            logger.error(f"통계 조회 오류: {e}")
            stats = {name: 0 for name in self.collections.keys()}
        
        return stats
    
    def search_by_medical_context(self, 
                                 query: str, 
                                 user_type: str = 'patient',
                                 department: Optional[str] = None,
                                 specialty: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        의료 컨텍스트를 고려한 검색
        
        Args:
            query: 검색 쿼리
            user_type: 사용자 유형 (patient/doctor/researcher)  
            department: 진료과
            specialty: 전문 분야
            
        Returns:
            컨텍스트를 고려한 검색 결과
        """
        try:
            # 사용자 유형별 컬렉션 우선순위 설정
            if user_type == 'doctor':
                collections_to_search = ['clinical_guidelines', 'medical_documents', 'drug_information']
            elif user_type == 'researcher':
                collections_to_search = ['research_papers', 'medical_documents', 'clinical_guidelines']
            else:  # patient
                collections_to_search = ['medical_documents', 'drug_information']
            
            all_results = []
            
            for collection_name in collections_to_search:
                # 필터 조건 설정
                filter_criteria = {}
                if department:
                    filter_criteria['hospital_department'] = department
                if specialty:
                    filter_criteria['medical_specialty'] = specialty
                
                # 검색 수행
                results = self.similarity_search(
                    query=query,
                    collection_name=collection_name,
                    k=3,
                    filter_criteria=filter_criteria if filter_criteria else None
                )
                
                # 컬렉션 정보 추가
                for result in results:
                    result['collection'] = collection_name
                
                all_results.extend(results)
            
            # 거리(유사도) 기준으로 정렬
            all_results.sort(key=lambda x: x.get('distance', float('inf')))
            
            # 상위 결과만 반환
            return all_results[:10]
            
        except Exception as e:
            logger.error(f"의료 컨텍스트 검색 오류: {e}")
            return []

# 전역 벡터 스토어 인스턴스
medical_vector_store = MedicalVectorStore()

# 샘플 의료 지식베이스 데이터
SAMPLE_MEDICAL_KNOWLEDGE = [
    {
        'id': 'guideline_001',
        'title': '고혈압 진료 가이드라인',
        'content': '''고혈압은 수축기 혈압 140mmHg 이상 또는 이완기 혈압 90mmHg 이상으로 정의됩니다.
        
단계별 치료 접근:
1. 1단계: 생활습관 개선 (체중 감량, 나트륨 제한, 운동)
2. 2단계: ACE 억제제 또는 ARB 단독 요법
3. 3단계: 두 가지 이상 약물 병용 요법

정기적인 혈압 모니터링과 합병증 예방이 중요합니다.''',
        'type': 'guideline',
        'source': '서울아산병원 심장내과',
        'department': '심장내과',
        'specialty': '순환기내과',
        'confidence': 0.95
    },
    {
        'id': 'drug_001', 
        'title': '아스피린 (Aspirin)',
        'content': '''아스피린은 혈소판 응집 억제제로 심혈관 질환 예방에 사용됩니다.

용법·용량:
- 심혈관 예방: 75-100mg 1일 1회
- 해열·진통: 500mg 1일 3-4회

주의사항:
- 위장관 부작용 주의
- 출혈 위험 증가
- 천식 환자 금기

상호작용: 와파린, 헤파린과 병용시 출혈 위험 증가''',
        'type': 'drug',
        'source': '서울아산병원 약제과',
        'department': '약제과',
        'specialty': '임상약학',
        'confidence': 0.98
    },
    {
        'id': 'research_001',
        'title': 'AI 기반 의료영상 진단의 정확도 분석',
        'content': '''딥러닝을 활용한 의료영상 진단 시스템의 성능을 평가한 연구입니다.

연구 결과:
- 흉부 X-ray 폐렴 진단 정확도: 94.2%
- CT 뇌출혈 검출 감도: 96.8% 
- MRI 뇌종양 분류 특이도: 92.1%

결론: AI 시스템이 전문의와 유사한 진단 성능을 보여주며, 진단 보조 도구로서의 활용 가능성이 높음.

향후 연구 방향: 더 다양한 질환에 대한 AI 모델 개발 필요''',
        'type': 'research', 
        'source': '서울아산병원 의공학과',
        'department': '의공학과',
        'specialty': '의료인공지능',
        'confidence': 0.92
    }
]

def initialize_sample_data():
    """샘플 의료 데이터 초기화"""
    try:
        logger.info("샘플 의료 지식베이스 데이터 초기화 시작...")
        medical_vector_store.add_medical_knowledge(SAMPLE_MEDICAL_KNOWLEDGE)
        
        stats = medical_vector_store.get_collection_stats()
        logger.info(f"초기화 완료 - 컬렉션 통계: {stats}")
        
    except Exception as e:
        logger.error(f"샘플 데이터 초기화 오류: {e}")

if __name__ == "__main__":
    # 테스트 실행
    initialize_sample_data()
    
    # 검색 테스트
    test_query = "고혈압 치료 방법"
    results = medical_vector_store.search_by_medical_context(test_query, user_type='doctor')
    
    print(f"\n검색 쿼리: {test_query}")
    print(f"검색 결과 {len(results)}개:")
    for i, result in enumerate(results[:3]):
        print(f"{i+1}. {result['metadata'].get('title', 'No title')}")
        print(f"   Content: {result['content'][:100]}...")
        print(f"   Distance: {result['distance']:.3f}")
        print()