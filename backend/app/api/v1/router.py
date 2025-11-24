from fastapi import APIRouter
from app.api.v1 import mocks, text2sql

api_router = APIRouter()

# Include lightweight mock endpoints for local frontend integration
api_router.include_router(mocks.router, prefix="", tags=["mocks"])

# Include Text2SQL router for CDW research functionality
api_router.include_router(text2sql.router, prefix="/text2sql", tags=["SFR-007 Text2SQL"])

# Other feature routers (keep commented until dependencies are ready)
# api_router.include_router(datamart.router, prefix="/datamart", tags=["SFR-002 DataMart"])
# api_router.include_router(olap.router, prefix="/olap", tags=["SFR-004 OLAP"])
# api_router.include_router(etl.router, prefix="/etl", tags=["SFR-005 ETL"])
# api_router.include_router(ai_agents.router, prefix="/agents", tags=["AI Agents"])
