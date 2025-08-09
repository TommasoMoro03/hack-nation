"""
API endpoints for question answering and classification.
"""

import logging
from typing import Dict, Optional, Any

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from services.question_classifier import QuestionClassifier, create_classifier
from core.config import settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Global classifier instance (initialized on startup)
_classifier: Optional[QuestionClassifier] = None


class QuestionClassificationRequest(BaseModel):
    """Request model for question classification"""
    question: str = Field(..., min_length=1, max_length=1000, description="The user's question to classify")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context (available companies, years, etc.)")


class QuestionClassificationResponse(BaseModel):
    """Response model for question classification"""
    text: bool = Field(..., description="Whether response should include explanatory text")
    recommendation: bool = Field(..., description="Whether response should include strategic recommendations")
    charts: bool = Field(..., description="Whether response should include data visualizations")
    preview: bool = Field(..., description="Whether response should include document previews")
    success: bool = Field(True, description="Whether classification was successful")
    message: Optional[str] = Field(None, description="Optional message or error details")


class ErrorResponse(BaseModel):
    """Standard error response model"""
    success: bool = Field(False)
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")


def get_classifier() -> QuestionClassifier:
    """
    Dependency to get the classifier instance.
    Initializes it if not already done.
    """
    global _classifier

    if _classifier is None:
        try:
            _classifier = create_classifier(
                api_key=settings.OPENAI_API_KEY,  # You'll need this in your config
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


@router.post(
    "/classify",
    response_model=QuestionClassificationResponse,
    responses={
        200: {"description": "Question classified successfully"},
        400: {"description": "Invalid request data", "model": ErrorResponse},
        500: {"description": "Classification service error", "model": ErrorResponse}
    },
    summary="Classify Question",
    description="Analyze a user question to determine what components should be included in the response"
)
async def classify_question(
        request: QuestionClassificationRequest,
        classifier: QuestionClassifier = Depends(get_classifier)
):
    """
    Classify a user question to determine response components.

    This endpoint analyzes the user's question and returns a JSON object indicating
    what components should be included in the response:
    - text: Always true (basic explanatory response)
    - recommendation: Strategic advice, decisions, next steps
    - charts: Data visualizations, trends, comparisons
    - preview: Document previews and page references
    """
    try:
        # Validate input
        if not request.question.strip():
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )

        # Classify the question
        logger.info(f"Classifying question: {request.question[:100]}...")

        result = classifier.classify(
            question=request.question.strip(),
            context=request.context
        )

        # Convert to response format
        response = QuestionClassificationResponse(
            text=result.text,
            recommendation=result.recommendation,
            charts=result.charts,
            preview=result.preview,
            success=True
        )

        logger.info(f"Classification result: {result.to_dict()}")
        return response

    except HTTPException:
        # Re-raise HTTP exceptions (like validation errors)
        raise

    except Exception as e:
        logger.error(f"Classification failed for question: {request.question[:100]}...")
        logger.error(f"Error: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=f"Question classification failed: {str(e)}"
        )
