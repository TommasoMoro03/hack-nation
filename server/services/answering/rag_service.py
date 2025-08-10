import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from core.config import settings
from storage.vector_store import get_vector_store
from utils.prompts import INTENT_EXTRACTION_PROMPT


@dataclass
class RAGResult:
    """Result of RAG processing"""
    answer: str
    sent_analysis: Optional[str]
    chunks_used: int
    processing_time: float
    filter_applied: str


class RAGService:
    """
    Clean RAG service that handles the complete pipeline:
    1. Document filtering (user selection or intent-based)
    2. Chunk retrieval
    3. Answer generation
    """
    
    def __init__(self):
        self.vector_store = get_vector_store()
        self.logger = logging.getLogger(__name__)
    
    def process_query(
        self, 
        question: str, 
        selected_documents: Optional[List[str]] = None
    ) -> RAGResult:
        """
        Process a question through the complete RAG pipeline
        """
        start_time = time.time()
        
        try:
            # Step 1: Filter documents
            documents, filter_applied = self._filter_documents(question, selected_documents)
            
            if not documents:
                return RAGResult(
                    answer="I couldn't find any relevant documents for your question.",
                    sent_analysis=None,
                    chunks_used=0,
                    processing_time=time.time() - start_time,
                    filter_applied=filter_applied
                )
            
            # Step 2: Retrieve chunks
            chunks = self._retrieve_chunks(question, documents)
            
            # Step 3: Generate answer
            answer = self._generate_answer(question, chunks)

            # Step 4: Generate sentiment analysis
            sent_analysis = self._analyze_sentiment(chunks)
            
            processing_time = time.time() - start_time
            
            return RAGResult(
                answer=answer,
                sent_analysis=sent_analysis,
                chunks_used=len(chunks),
                processing_time=processing_time,
                filter_applied=filter_applied
            )
            
        except Exception as e:
            self.logger.error(f"RAG processing failed: {str(e)}")
            return RAGResult(
                answer="I encountered an error while processing your question. Please try again.",
                sent_analysis=None,
                chunks_used=0,
                processing_time=time.time() - start_time,
                filter_applied="Error"
            )
    
    def _filter_documents(
        self, 
        question: str, 
        selected_documents: Optional[List[str]] = None
    ) -> tuple[List[Dict], str]:
        """Filter documents based on user selection or extracted intent"""
        
        if selected_documents:
            print("Here I should not enter")
            # User specified documents - filter by those
            documents = []
            for doc_id in selected_documents:
                doc = self.vector_store.get_document_by_id(doc_id)
                if doc:
                    documents.append(doc)
            return documents, f"User-selected documents ({len(selected_documents)} selected)"
        
        else:
            print("Here I should enter")
            # Extract intent and filter by that
            intent = self._extract_intent(question)
            documents, filter_desc = self._filter_by_intent(intent)
            return documents, filter_desc
    
    def _extract_intent(self, question: str) -> Dict[str, Any]:
        """Extract intent from question using LLM"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            available_companies = self.vector_store.get_all_companies()
            available_years = self.vector_store.get_all_years()
            
            prompt = f"""
Extract company names and years from this question. Available companies: {available_companies}. Available years: {available_years}.

Question: {question}

{INTENT_EXTRACTION_PROMPT}
"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            import json
            raw_content = response.choices[0].message.content.strip()
            print("=== RAW RESPONSE ===")
            print(raw_content)
            print("====================")
            result = json.loads(raw_content)
            print(f"Extracted intent with openai: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Intent extraction failed: {str(e)}")
            return {"companies": [], "years": []}
    
    def _filter_by_intent(self, intent: Dict[str, Any]) -> tuple[List[Dict], str]:
        """Filter documents based on extracted intent"""
        companies = intent.get('companies', [])
        years = intent.get('years', [])
        
        where_conditions = {}
        
        if companies:
            if len(companies) == 1:
                where_conditions["company"] = companies[0]
            else:
                where_conditions["company"] = {"$in": companies}
        
        if years:
            if len(years) == 1:
                where_conditions["year"] = years[0]
            else:
                where_conditions["year"] = {"$in": years}
        
        if where_conditions:
            documents = self.vector_store.get_documents_with_filters(
                where=where_conditions, 
                limit=50
            )
            filter_desc = f"Intent-based: companies={companies}, years={years}"
        else:
            # No intent - get recent documents
            documents = self.vector_store.get_documents_with_filters(
                where={"year": {"$in": [2024, 2023, 2022]}}, 
                limit=50
            )
            filter_desc = "Recent documents (last 3 years)"
        
        return documents, filter_desc
    
    def _retrieve_chunks(self, question: str, documents: List[Dict], top_k: int = 10) -> List[Dict]:
        """Retrieve relevant chunks from filtered documents"""
        if not documents:
            return []
        
        # Get document IDs for filtering
        doc_ids = [doc.get('id') for doc in documents if doc.get('id')]
        
        # Perform semantic search
        chunks = self.vector_store.similarity_search_with_filter(
            query=question,
            document_ids=doc_ids,
            n_results=top_k,
            threshold=0.1
        )
        
        return chunks
    
    def _generate_answer(self, question: str, chunks: List[Dict]) -> str:
        """Generate answer using LLM based on retrieved chunks"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Prepare context from chunks
            if not chunks:
                return "I couldn't find any relevant information to answer your question."
            
            context_parts = []
            for i, chunk in enumerate(chunks[:5]):  # Use top 5 chunks
                content = chunk.get('content', '')
                company = chunk.get('company', 'Unknown')
                year = chunk.get('year', 'Unknown')
                
                if content.strip():
                    context_parts.append(f"Document {i+1} ({company}, {year}):\n{content}\n")
            
            context = "\n".join(context_parts)
            
            # Create prompt
            prompt = f"""
Based on the following document context, please answer the user's question.

Context:
{context}

Question: {question}

Please provide a clear, accurate answer based on the information in the documents. If the information is not available in the provided context, say so clearly.
"""
            
            # Generate answer
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful financial document analyst. Answer questions based on the provided document context. Be accurate and concise."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Error generating answer: {str(e)}")
            return "I apologize, but I encountered an error while generating the answer. Please try again."

    def _analyze_sentiment(self, chunks: List[Dict]) -> Optional[str]:
        """Perform sentiment analysiss using LLM on the retrieved chunks"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            if not chunks:
                return None

            # Prepare context for sentiment analysis
            context_parts = []
            for i, chunk in enumerate(chunks[:5]):  # Use top 5 chunks
                content = chunk.get('content', '')
                company = chunk.get('company', 'Unknown')
                year = chunk.get('year', 'Unknown')

                if content.strip():
                    context_parts.append(f"Document {i+1} ({company}, {year}):\n{content}\n")

            context = "\n".join(context_parts)

            # Create prompt for sentiment analysis
            prompt = f"""
Analyze the sentiment of the following document context. Provide a summary of the overall sentiment and any notable positive or negative aspects.
Context:
{context}
Please provide a clear sentiment analysis based on the information in the documents.
"""

            # Generate sentiment analysis
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial document sentiment analyst. Analyze the sentiment of the provided document context."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"Error performing sentiment analysis: {str(e)}")
            return None
