from fastapi import APIRouter
from api.v1.endpoints import documents, answering, smart_query

api_router = APIRouter()
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(answering.router, prefix="/answering", tags=["Answering"])
api_router.include_router(smart_query.router, prefix="/smart-query", tags=["Smart Query"])
