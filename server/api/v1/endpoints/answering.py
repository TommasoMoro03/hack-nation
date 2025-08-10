import logging
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from services.answering.document_filter import DocumentFilter
from services.answering.intent_extractor import IntentExtractor
from services.answering.question_classifier import QuestionClassifier, create_classifier
from services.answering.response_generator import ResponseGenerator
from core.config import settings
from services.answering.retriever import Retriever
from storage.vector_store import get_vector_store
from openai import OpenAI

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Global instances (initialized on startup)
_classifier: Optional[QuestionClassifier] = None

vector_store = get_vector_store()

retriever = Retriever(
    vector_store=vector_store,
    logger=logger
)


class QuestionRequest(BaseModel):
    """Base request model for questions"""
    question: str = Field(..., min_length=1, max_length=1000, description="The user's question")
    selected_documents: Optional[List[str]] = Field(None, description="Optional list of selected document IDs")


class ClassificationResponse(BaseModel):
    """Response model for question classification"""
    text: bool = Field(..., description="Whether response should include explanatory text")
    recommendation: bool = Field(..., description="Whether response should include strategic recommendations")
    charts: bool = Field(..., description="Whether response should include data visualizations")
    preview: bool = Field(..., description="Whether response should include document previews")
    success: bool = Field(True, description="Whether classification was successful")


class FinalResponse(BaseModel):
    """Response model for document retrieval"""
    text: str = Field(..., description="The main text response to the question")
    recommendation: str = Field(True, description="The explanatory text")
    data_charts: Optional[List[str]] = Field(None, description="List of data charts included in the response")
    preview: str = Field(True, description="Document previews")


def get_classifier() -> QuestionClassifier:
    """Dependency to get the classifier instance"""
    global _classifier

    if _classifier is None:
        try:
            _classifier = create_classifier(
                api_key=settings.OPENAI_API_KEY,
                model_name=getattr(settings, 'CLASSIFICATION_MODEL', 'gpt-3.5-turbo'),
                provider="openai"
            )
            logger.info("Question classifier initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize classifier: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize question classification service"
            )

    return _classifier

def get_intent_extractor() -> IntentExtractor:
    """Dependency to get the intent extractor instance"""
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        extractor = IntentExtractor(
            llm_client=client,
            model_name=getattr(settings, 'INTENT_EXTRACTION_MODEL', 'gpt-3.5-turbo'),
            temperature=0.1,
            max_retries=3
        )
        logger.info("Intent extractor initialized successfully")
        return extractor
    except Exception as e:
        logger.error(f"Failed to initialize intent extractor: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize intent extraction service"
        )


@router.post(
    "/classify",
    response_model=ClassificationResponse,
    summary="Classify Question",
    description="Analyze a user question to determine what components should be included in the response"
)
async def classify_question(
    request: QuestionRequest,
    classifier: QuestionClassifier = Depends(get_classifier)
):
    """
    Classify a user question to determine response components.
    """
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        logger.info(f"Classifying question: {request.question[:100]}...")

        result = classifier.classify(question=request.question.strip())

        response = ClassificationResponse(
            text=result.text,
            recommendation=result.recommendation,
            charts=result.charts,
            preview=result.preview,
            success=True
        )

        logger.info(f"Classification result: {result.to_dict()}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Classification failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@router.post(
    "/query",
    response_model=FinalResponse,
    summary="Complete Query Answering",
    description="Perform complete query processing including classification and retrieval"
)
async def answer_query(
    request: QuestionRequest,
    classifier: QuestionClassifier = Depends(get_classifier),
    extractor: IntentExtractor = Depends(get_intent_extractor),
):
    """
    Process a complete query including both classification and retrieval.

    This is the main endpoint that combines:
    1. Question classification
    2. Intent extraction and document filtering
    3. Semantic retrieval
    4. Query complexity analysis
    """
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        logger.info(f"Processing complete query: {request.question[:100]}...")

        # Step 1: Classify the question
        classification_result = classifier.classify(question=request.question.strip())

        # Step 2: Filter only documents that matches filters
        # Step 2.1: If selected documents are provided, use them directly
        if request.selected_documents:
            # Convert string IDs to document objects
            selected_docs = []
            for doc_id in request.selected_documents:
                doc = vector_store.get_document_by_id(doc_id)
                if doc:
                    selected_docs.append(doc)
        else:
            # Step 2.2: Extract intent to filter documents
            intent = extractor.extract(request.question.strip())
            document_filter = DocumentFilter(vector_store)
            selected_docs = document_filter.filter_by_intent(intent).documents

        if not selected_docs:
            raise HTTPException(status_code=404, detail="No relevant documents found for the query")

        # Step 3: Retrieve documents based on classification
        retrieved_chunks = retriever.retrieve(
            question=request.question.strip(),
            selected_documents=selected_docs,
        )

        # Step 4: Generate final answer
        answer = ResponseGenerator.generate_answer(
            question=request.question.strip(),
            retrieved_chunks=retrieved_chunks.chunks,
            vector_store=vector_store,
            classification=classification_result
        )

        # Step 5: Prepare final response
        response = FinalResponse(
            text=answer,
            recommendation="",
            data_charts=[],
            preview=""
        )

        logger.info(f"Answer generated successfully")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Complete query processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")
