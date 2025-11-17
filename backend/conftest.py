"""
Pytest configuration and fixtures for TDD testing
서울아산병원 AI 플랫폼 테스트 설정
"""
import pytest
import asyncio
import os
from typing import Generator, AsyncGenerator
from unittest.mock import MagicMock, AsyncMock

import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

# from app.main import app  # 임시 주석 처리
# from app.core.database import Base, get_db  # 임시 주석 처리
# from app.core.config import settings


# # 테스트용 데이터베이스 설정
# TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# test_engine = create_async_engine(
#     TEST_DATABASE_URL,
#     echo=False,
#     future=True
# )

# TestAsyncSession = sessionmaker(
#     test_engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
#     autoflush=False,
#     autocommit=False,
# )


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# @pytest_asyncio.fixture
# async def test_db() -> AsyncGenerator[AsyncSession, None]:
#     """테스트용 데이터베이스 세션 생성"""
#     # 테이블 생성
#     async with test_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     
#     # 세션 생성
#     async with TestAsyncSession() as session:
#         yield session
#     
#     # 테이블 정리
#     async with test_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)


# @pytest.fixture
# def test_client() -> TestClient:
#     """FastAPI 테스트 클라이언트"""
#     return TestClient(app)


# @pytest_asyncio.fixture
# async def async_client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
#     """비동기 HTTP 클라이언트"""
#     def override_get_db():
#         yield test_db
#     
#     app.dependency_overrides[get_db] = override_get_db
#     
#     async with AsyncClient(app=app, base_url="http://testserver") as client:
#         yield client
#     
#     app.dependency_overrides.clear()


# Mock 객체들
@pytest.fixture
def mock_llm_service() -> MagicMock:
    """LLM 서비스 Mock"""
    mock = MagicMock()
    mock.predict = AsyncMock(return_value="SELECT COUNT(*) FROM patients")
    mock.apredict = AsyncMock(return_value="SELECT COUNT(*) FROM patients")
    return mock


@pytest.fixture
def mock_vector_store() -> MagicMock:
    """Vector Store Mock"""
    mock = MagicMock()
    mock.similarity_search = AsyncMock(return_value=[
        {"content": "당뇨병 환자", "score": 0.9},
        {"content": "혈당 관리", "score": 0.8}
    ])
    return mock


@pytest.fixture
def mock_humanlayer_client() -> MagicMock:
    """HumanLayer Client Mock"""
    mock = MagicMock()
    mock.create_approval_request = AsyncMock(return_value={"id": "approval-123", "status": "pending"})
    mock.get_approval_status = AsyncMock(return_value={"status": "approved"})
    return mock


# 테스트 데이터 Fixtures
@pytest.fixture
def sample_medical_query() -> dict:
    """샘플 의료 쿼리 데이터"""
    return {
        "question": "당뇨병 환자 수를 알려주세요",
        "expected_sql": "SELECT COUNT(*) FROM patients WHERE diagnosis LIKE '%diabetes%'",
        "confidence": 0.9,
        "risk_level": "low"
    }


@pytest.fixture
def sample_patient_data() -> list:
    """샘플 환자 데이터"""
    return [
        {
            "patient_id": "P001",
            "age": 45,
            "gender": "M",
            "diagnosis": "Type 2 Diabetes",
            "region": "Seoul"
        },
        {
            "patient_id": "P002",
            "age": 32,
            "gender": "F",
            "diagnosis": "Hypertension",
            "region": "Busan"
        },
        {
            "patient_id": "P003",
            "age": 67,
            "gender": "M",
            "diagnosis": "Type 2 Diabetes",
            "region": "Seoul"
        }
    ]


@pytest.fixture
def sample_approval_request() -> dict:
    """샘플 승인 요청 데이터"""
    return {
        "id": "approval-test-001",
        "type": "sql_execution",
        "sql": "SELECT COUNT(*) FROM patients WHERE age > 65",
        "requester": "test_user",
        "risk_level": "medium",
        "reason": "노인 환자 수 조회"
    }


# Environment Variables Override
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """테스트 환경 변수 설정"""
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("HUMANLAYER_API_KEY", "test-humanlayer-key")
    monkeypatch.setenv("HUMANLAYER_DAEMON_URL", "http://localhost:8080")


# Custom Pytest Markers
def pytest_configure(config):
    """Pytest 설정 및 커스텀 마커 등록"""
    config.addinivalue_line(
        "markers", "unit: 단위 테스트"
    )
    config.addinivalue_line(
        "markers", "integration: 통합 테스트"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-End 테스트"
    )
    config.addinivalue_line(
        "markers", "slow: 느린 테스트 (실제 API 호출 등)"
    )
    config.addinivalue_line(
        "markers", "medical: 의료 도메인 관련 테스트"
    )


# 테스트 유틸리티 함수들
@pytest.fixture
def assert_sql_equivalent():
    """SQL 쿼리 동등성 검사 함수"""
    def _assert_sql_equivalent(actual: str, expected: str) -> bool:
        """공백과 대소문자를 무시하고 SQL 동등성 검사"""
        actual_clean = " ".join(actual.strip().lower().split())
        expected_clean = " ".join(expected.strip().lower().split())
        return actual_clean == expected_clean
    
    return _assert_sql_equivalent


@pytest.fixture
def create_test_medical_data():
    """테스트용 의료 데이터 생성 함수"""
    async def _create_data(session: AsyncSession, count: int = 10):
        """지정된 수만큼 테스트 의료 데이터 생성"""
        # 실제 구현에서는 SQLAlchemy 모델을 사용
        # 현재는 기본 구조만 제공
        pass
    
    return _create_data


# TDD 헬퍼 함수들
class TDDTestCase:
    """TDD 테스트 케이스 기본 클래스"""
    
    def given(self, description: str):
        """Given 단계 - 테스트 조건 설정"""
        print(f"GIVEN: {description}")
        return self
    
    def when(self, description: str):
        """When 단계 - 테스트 실행"""
        print(f"WHEN: {description}")
        return self
    
    def then(self, description: str):
        """Then 단계 - 결과 검증"""
        print(f"THEN: {description}")
        return self


@pytest.fixture
def tdd_case():
    """TDD 케이스 헬퍼"""
    return TDDTestCase()