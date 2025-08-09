from fastapi import APIRouter
from api.v1.endpoints import documents, answering

api_router = APIRouter()
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(answering.router, prefix="/answering", tags=["Answering"])
