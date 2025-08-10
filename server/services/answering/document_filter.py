import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from services.answering.intent_extractor import ExtractedIntent


@dataclass
class FilterResult:
    """Result of document filtering"""
    documents: List[Dict[str, Any]]
    total_found: int
    filter_applied: str  # Description of what filter was applied
    companies_found: List[str]
    years_found: List[int]

class DocumentFilter:

    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.logger = logging.getLogger(__name__)

    def filter_by_intent(self, intent: ExtractedIntent) -> 'FilterResult':

        try:
            # Build metadata filters for ChromaDB
            where_conditions = {}

            if intent.companies:
                # Handle multiple companies (OR condition)
                if len(intent.companies) == 1:
                    where_conditions["company"] = intent.companies[0]
                else:
                    where_conditions["company"] = {"$in": intent.companies}

            if intent.years:
                # Handle multiple years (OR condition)
                years_list = list(intent.years)
                if len(years_list) == 1:
                    where_conditions["year"] = years_list[0]
                else:
                    where_conditions["year"] = {"$in": years_list}

            # Query vector store with metadata filters
            documents = self.vector_store.get_documents_with_filters(
                where=where_conditions,
            )

            # Build filter description
            filter_parts = []
            if intent.companies:
                filter_parts.append(f"Companies: {', '.join(intent.companies)}")
            if intent.years:
                years_str = ', '.join(map(str, sorted(intent.years)))
                filter_parts.append(f"Years: {years_str}")

            filter_description = " | ".join(filter_parts) if filter_parts else "Intent-based"

            result = FilterResult(
                documents=documents,
                total_found=len(documents),
                filter_applied=filter_description,
                companies_found=intent.companies or [],
                years_found=sorted(list(intent.years)) if intent.years else []
            )

            self.logger.info(f"Filtered by intent: {len(documents)} documents found")
            return result

        except Exception as e:
            self.logger.error(f"Error filtering by intent: {str(e)}")
            # Fallback to recent documents
            return self._get_recent_documents(intent)

    def _get_recent_documents(self, intent: ExtractedIntent) -> 'FilterResult':
        """Fallback to get recent documents if filtering fails"""
        self.logger.warning("Filtering by intent failed, falling back to recent documents")

        # Get recent documents from vector store
        recent_docs = self.vector_store.get_recent_documents(limit=10)

        return FilterResult(
            documents=recent_docs,
            total_found=len(recent_docs),
            filter_applied="Recent documents fallback",
            companies_found=intent.companies or [],
            years_found=intent.years or []
        )
