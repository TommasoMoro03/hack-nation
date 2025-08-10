import json
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
from utils.prompts import CLASSIFICATION_PROMPT

# You'll need to install: pip install openai
# Or use any other LLM client (Anthropic, etc.)
from openai import OpenAI


class ComponentType(Enum):
    """Enum for response component types"""
    TEXT = "text"
    RECOMMENDATION = "recommendation"
    CHARTS = "charts"
    PREVIEW = "preview"


@dataclass
class ClassificationResult:
    """Data class for classification results"""
    text: bool = True  # Always true - every response needs text
    recommendation: bool = False
    charts: bool = False
    preview: bool = False

    def to_dict(self) -> Dict[str, bool]:
        """Convert to dictionary format"""
        return {
            "text": self.text,
            "recommendation": self.recommendation,
            "charts": self.charts,
            "preview": self.preview
        }

    @classmethod
    def from_dict(cls, data: Dict[str, bool]) -> 'ClassificationResult':
        """Create from dictionary"""
        return cls(
            text=data.get("text", True),
            recommendation=data.get("recommendation", False),
            charts=data.get("charts", False),
            preview=data.get("preview", False)
        )


class QuestionClassifier:
    """
    Classifies user questions to determine response components needed.

    Uses LLM to analyze questions and determine what should be included:
    - text: Always included (basic answer)
    - recommendation: Strategic advice, decisions, next steps
    - charts: Data visualization, trends, comparisons
    - preview: Specific document/page references needed
    """

    def __init__(
            self,
            llm_client: Any,
            model_name: str = "gpt-4o-mini",
            temperature: float = 0.1,
            max_retries: int = 3
    ):
        """
        Initialize the classifier.

        Args:
            llm_client: LLM client (OpenAI, Anthropic, etc.)
            model_name: Model to use for classification
            temperature: LLM temperature (low for consistent classification)
            max_retries: Number of retry attempts for failed API calls
        """
        self.llm_client = llm_client
        self.model_name = model_name
        self.temperature = temperature
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)

    def classify(self, question: str, context: Optional[Dict] = None) -> ClassificationResult:
        """
        Classify a question to determine response components.

        Args:
            question: User's question/query
            context: Optional context (available companies, years, etc.)

        Returns:
            ClassificationResult with component flags

        Raises:
            Exception: If classification fails after all retries
        """
        if not question.strip():
            self.logger.warning("Empty question provided")
            return ClassificationResult()  # Default: only text

        # Prepare the prompt with context if available
        prompt = self._prepare_prompt(CLASSIFICATION_PROMPT, question, context)

        # Attempt classification with retries
        for attempt in range(self.max_retries):
            try:
                result = self._call_llm(prompt)
                classification = self._parse_response(result)

                self.logger.info(
                    f"Question classified: {question[:50]}... -> {classification.to_dict()}"
                )
                return classification

            except Exception as e:
                self.logger.warning(
                    f"Classification attempt {attempt + 1} failed: {str(e)}"
                )
                if attempt == self.max_retries - 1:
                    self.logger.error(f"All classification attempts failed for: {question}")
                    # Return safe default on failure
                    return ClassificationResult()

        # Fallback (should not reach here)
        return ClassificationResult()

    def _prepare_prompt(
            self,
            base_prompt: str,
            question: str,
            context: Optional[Dict] = None
    ) -> str:
        """Prepare the full prompt with question and context"""

        context_str = ""
        if context:
            context_str = f"\nAvailable context: {json.dumps(context, indent=2)}\n"

        return f"{base_prompt}{context_str}\nQuestion: {question}\n\nClassification:"

    def _call_llm(self, prompt: str) -> str:
        """Make API call to LLM"""
        try:
            response = self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise classifier for financial Q&A systems. Always respond with valid JSON only."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=150  # Short response needed
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            self.logger.error(f"LLM API call failed: {str(e)}")
            raise

    def _parse_response(self, response: str) -> ClassificationResult:
        """Parse LLM response into ClassificationResult"""
        try:
            # Clean response (remove markdown code blocks if present)
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:-3].strip()
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:-3].strip()

            # Parse JSON
            data = json.loads(cleaned)

            # Validate required fields
            if not isinstance(data, dict):
                raise ValueError("Response is not a JSON object")

            # Ensure text is always True
            data["text"] = True

            return ClassificationResult.from_dict(data)

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {response}")
            raise ValueError(f"Invalid JSON in LLM response: {str(e)}")

        except Exception as e:
            self.logger.error(f"Failed to parse response: {response}")
            raise ValueError(f"Cannot parse classification result: {str(e)}")


# Factory function for easy instantiation
def create_classifier(
        api_key: str,
        model_name: str = "gpt-4o-mini",
        provider: str = "openai"
) -> QuestionClassifier:
    """
    Factory function to create a QuestionClassifier instance.

    Args:
        api_key: API key for the LLM provider
        model_name: Model to use
        provider: LLM provider ("openai", "anthropic", etc.)

    Returns:
        Configured QuestionClassifier instance
    """
    if provider.lower() == "openai":
        client = OpenAI(api_key=api_key)
        return QuestionClassifier(client, model_name)

    # Add other providers as needed
    # elif provider.lower() == "anthropic":
    #     client = Anthropic(api_key=api_key)
    #     return QuestionClassifier(client, model_name)

    else:
        raise ValueError(f"Unsupported provider: {provider}")