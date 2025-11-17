from fastapi import APIRouter
from app.api.v1 import text2sql

api_router = APIRouter()

# Include Text2SQL router for MVP testing
api_router.include_router(text2sql.router, prefix="/text2sql", tags=["SFR-007 Text2SQL"])

# TODO: Add other routers after fixing dependencies
# api_router.include_router(datamart.router, prefix="/datamart", tags=["SFR-002 DataMart"])
# api_router.include_router(olap.router, prefix="/olap", tags=["SFR-004 OLAP"])
# api_router.include_router(etl.router, prefix="/etl", tags=["SFR-005 ETL"])
# api_router.include_router(ai_agents.router, prefix="/agents", tags=["AI Agents"])