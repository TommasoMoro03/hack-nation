from fastapi import APIRouter
from .endpoints import documents, answering, smart_query

router = APIRouter()

# Include all endpoint routers
router.include_router(documents.router, prefix="/documents", tags=["documents"])
router.include_router(answering.router, prefix="/answering", tags=["answering"])
router.include_router(smart_query.router, prefix="/smart", tags=["smart-query"])
