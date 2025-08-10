import logging
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class RetrievalResult:
    """Result of semantic retrieval"""
    chunks: List[Dict[str, Any]]
    total_chunks: int
    avg_similarity: float
    query_used: str


class Retriever:
    """
    Semantic retrieval service for RAG.

    Performs semantic search on filtered document sets and returns
    the most relevant chunks for answer generation.
    """

    def __init__(self, vector_store, logger):
        self.vector_store = vector_store
        self.logger = logger

    def retrieve(
            self,
            question: str,
            selected_documents: List[Dict[str, Any]],
            top_k: int = 10,
            similarity_threshold: float = 0.1  # Lowered threshold for testing
    ) -> RetrievalResult:
        """
        Perform semantic retrieval on filtered documents.

        Args:
            question: User's question for semantic search
            top_k: Number of top chunks to retrieve
            similarity_threshold: Minimum similarity score

        Returns:
            RetrievalResult with relevant chunks
        """
        if not selected_documents:
            return RetrievalResult(
                chunks=[],
                total_chunks=0,
                avg_similarity=0.0,
                query_used=question
            )

        try:
            # Extract document IDs for filtering
            doc_ids = [doc.get('id') for doc in selected_documents if doc.get('id')]

            print(f"Selected document IDs: {doc_ids}")  # Debugging line

            if not doc_ids:
                self.logger.warning("No valid document IDs found")
                return self._empty_result(question)

            # Perform semantic search with document filtering
            chunks = self._semantic_search(
                query=question,
                document_ids=doc_ids,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )

            # Process and enrich results
            processed_chunks = self._process_chunks(chunks)
            avg_similarity = self._calculate_avg_similarity(processed_chunks)

            result = RetrievalResult(
                chunks=processed_chunks,
                total_chunks=len(processed_chunks),
                avg_similarity=avg_similarity,
                query_used=question
            )

            print(f"Retrieved {len(processed_chunks)} chunks with avg similarity {avg_similarity:.3f}")  # Debugging line

            self.logger.info(
                f"Retrieved {len(processed_chunks)} chunks with avg similarity {avg_similarity:.3f}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Retrieval failed: {str(e)}")
            return self._empty_result(question)

    def _semantic_search(
            self,
            query: str,
            document_ids: List[str],
            top_k: int,
            similarity_threshold: float
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search using ChromaDB.

        This method assumes your vector_store has a method to search
        with document ID filtering.
        """
        try:
            # Query ChromaDB with document filtering
            results = self.vector_store.similarity_search_with_filter(
                query=query,
                document_ids=document_ids,
                n_results=top_k,
                threshold=similarity_threshold
            )

            return results

        except Exception as e:
            self.logger.error(f"Semantic search failed: {str(e)}")
            raise

    def _process_chunks(self, raw_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and enrich retrieved chunks"""
        processed = []

        for chunk in raw_chunks:
            try:
                # Standardize chunk format
                processed_chunk = {
                    'content': chunk.get('document', chunk.get('content', '')),
                    'similarity_score': chunk.get('similarity', chunk.get('distance', 0.0)),
                    'metadata': chunk.get('metadata', {}),
                    'chunk_id': chunk.get('id', ''),
                    'document_id': chunk.get('metadata', {}).get('document_id', ''),
                    'company': chunk.get('metadata', {}).get('company', ''),
                    'year': chunk.get('metadata', {}).get('year', ''),
                    'page': chunk.get('metadata', {}).get('page', ''),
                    'chunk_index': chunk.get('metadata', {}).get('chunk_index', 0)
                }

                # Only add if content is meaningful
                if processed_chunk['content'].strip():
                    processed.append(processed_chunk)

            except Exception as e:
                self.logger.warning(f"Error processing chunk: {str(e)}")
                continue

        # Sort by similarity score (descending)
        processed.sort(key=lambda x: x['similarity_score'], reverse=True)

        return processed

    def _extract_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract unique sources from chunks"""
        sources = {}

        for chunk in chunks:
            company = chunk.get('company', 'Unknown')
            year = chunk.get('year', 'Unknown')
            doc_id = chunk.get('document_id', '')
            page = chunk.get('page', '')

            source_key = f"{company}_{year}_{doc_id}"

            if source_key not in sources:
                sources[source_key] = {
                    'company': company,
                    'year': str(year),
                    'document_id': doc_id,
                    'pages': set()
                }

            if page:
                sources[source_key]['pages'].add(str(page))

        # Convert to list and format pages
        source_list = []
        for source in sources.values():
            pages_list = sorted(list(source['pages'])) if source['pages'] else []
            source_dict = {
                'company': source['company'],
                'year': source['year'],
                'document_id': source['document_id'],
                'pages': ', '.join(pages_list) if pages_list else 'Unknown'
            }
            source_list.append(source_dict)

        return source_list

    def _calculate_avg_similarity(self, chunks: List[Dict[str, Any]]) -> float:
        """Calculate average similarity score"""
        if not chunks:
            return 0.0

        scores = [chunk.get('similarity_score', 0.0) for chunk in chunks]
        return sum(scores) / len(scores)

    def _empty_result(self, question: str) -> RetrievalResult:
        """Return empty result"""
        return RetrievalResult(
            chunks=[],
            total_chunks=0,
            avg_similarity=0.0,
            query_used=question
        )
