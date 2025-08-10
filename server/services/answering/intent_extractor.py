import json
import logging
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from utils.prompts import INTENT_EXTRACTION_PROMPT

@dataclass
class ExtractedIntent:
    """Container for extracted intent information"""
    companies: List[str]
    years: List[int]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "companies": self.companies,
            "years": self.years
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExtractedIntent':
        """Create from dictionary"""
        return cls(
            companies=data.get("companies", []),
            years=data.get("years", [])
        )

class IntentExtractor:
    """
    Extracts intent from user questions to identify companies and years mentioned.
    """

    def __init__(
            self,
            llm_client: Any,
            model_name: str = "gpt-4o-mini",
            temperature: float = 0.1,
            max_retries: int = 3
    ):
        """
        Initialize the extractor.

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

    def extract(self, question: str, context: Optional[Dict] = None) -> ExtractedIntent:
        """
        Extract intent from a question to identify companies and years.

        Args:
            question: User's question/query
            context: Optional context (available companies, years, etc.)

        Returns:
            ExtractedIntent with component flags
        """
        if not question.strip():
            self.logger.warning("Empty question provided")
            return ExtractedIntent([], [])  # Default: only text

        # Prepare the prompt with context if available
        prompt = self._prepare_prompt(INTENT_EXTRACTION_PROMPT, question, context)

        # Attempt classification with retries
        for attempt in range(self.max_retries):
            try:
                result = self._call_llm(prompt)
                extraction = self._parse_response(result)

                self.logger.info(
                    f"Question classified: {question[:50]}... -> {extraction.to_dict()}"
                )
                return extraction

            except Exception as e:
                self.logger.warning(
                    f"Classification attempt {attempt + 1} failed: {str(e)}"
                )
                if attempt == self.max_retries - 1:
                    self.logger.error(f"All classification attempts failed for: {question}")
                    # Return safe default on failure
                    return ExtractedIntent([], [])

        # Fallback (should not reach here)
        return ExtractedIntent([], [])

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
                        "content": "You are a precise extractor for companies and years data. Always respond with valid JSON only."
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

    def _parse_response(self, response: str) -> ExtractedIntent:
        """Parse the LLM response into ExtractedIntent"""
        try:
            data = json.loads(response)
            companies = data.get("companies", [])
            years = data.get("years", [])
            return ExtractedIntent(
                companies=[c.lower() for c in companies],  # Normalize to lowercase
                years=[int(y) for y in years]  # Ensure years are integers
            )
        except (json.JSONDecodeError, TypeError) as e:
            self.logger.error(f"Failed to parse response: {str(e)}")
            return ExtractedIntent([], [])

