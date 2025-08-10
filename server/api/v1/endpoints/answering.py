import logging
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from services.answering.rag_service import RAGService
from core.config import settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Global service instances
_rag_service: Optional[RAGService] = None


class QuestionRequest(BaseModel):
    """Base request model for questions"""
    question: str = Field(..., min_length=1, max_length=1000, description="The user's question")
    selected_documents: Optional[List[str]] = Field(None, description="Optional list of selected document IDs")


class QueryResponse(BaseModel):
    """Response model for query processing"""
    text: str = Field(..., description="The generated answer")
    chunks_used: int = Field(..., description="Number of chunks used for answer")
    processing_time: float = Field(..., description="Processing time in seconds")
    filter_applied: str = Field(..., description="Description of filter applied")


def get_rag_service() -> RAGService:
    """Dependency to get RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service




@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QuestionRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Process a question through the RAG pipeline:
    1. Check if user specified documents - if yes, filter by those
    2. If not, extract intent (companies, years) from question
    3. Filter documents based on intent or user selection
    4. Retrieve relevant chunks from filtered documents
    5. Generate answer using LLM
    """
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        logger.info(f"Processing query: {request.question[:100]}...")
        
        # Process query through RAG service
        result = rag_service.process_query(
            question=request.question.strip(),
            selected_documents=request.selected_documents
        )
        
        response = QueryResponse(
            text=result.answer,
            chunks_used=result.chunks_used,
            processing_time=result.processing_time,
            filter_applied=result.filter_applied
        )
        
        logger.info(f"Query processed: {result.chunks_used} chunks used in {result.processing_time:.2f}s")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")
