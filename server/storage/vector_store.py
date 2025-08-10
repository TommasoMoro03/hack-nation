import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional, Set
import logging
from core.config import settings

logger = logging.getLogger(__name__)

# Initialize the ChromaDB client.
# Using a persistent client to save data to disk.
client = chromadb.PersistentClient(path="./chroma_db")

# Use a pre-built embedding function from OpenAI
# OPENAI_API_KEY is defined in .env
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=settings.OPENAI_API_KEY,
    model_name="text-embedding-3-large"
)

# Create or get the collection.
# We pass the embedding function so ChromaDB knows how to handle documents.
collection = client.get_or_create_collection(
    name="financial_documents",
    embedding_function=openai_ef
)


class VectorStoreWrapper:
    """
    Wrapper class for ChromaDB operations.
    Provides the interface needed by the RAG services.
    """

    def __init__(self, collection):
        self.collection = collection
        self.logger = logging.getLogger(__name__)

    def similarity_search_with_filter(
            self,
            query: str,
            document_ids: Optional[List[str]] = None,
            n_results: int = 10,
            threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search with optional document filtering.

        Args:
            query: Search query
            document_ids: Optional list of document IDs to filter by
            n_results: Number of results to return
            threshold: Similarity threshold (not directly supported by ChromaDB)

        Returns:
            List of search results
        """
        try:
            where_filter = None

            # If document_ids provided, filter by them
            # Since we can't filter by document_id directly in ChromaDB,
            # we'll filter by filename (assuming document_ids are filenames)
            if document_ids:
                print(f"Document IDs provided for filtering: {document_ids}")  # Debugging line
                # Remove metadata_ prefix if present and extract filenames
                filenames = []
                for doc_id in document_ids:
                    if doc_id.startswith("metadata_"):
                        print("Enter also here")
                        filename = doc_id.replace("metadata_", "")
                        filenames.append(filename)
                    else:
                        filenames.append(doc_id)

                if len(filenames) == 1:
                    where_filter = {"filename": filenames[0]}
                else:
                    where_filter = {"filename": {"$in": filenames}}

            print("Final filenames filter:", filenames)  # Debugging line

            # DEBUG: Let's see what's actually in the database
            print("=== DEBUG: Checking database contents ===")
            all_results = self.collection.get()
            print(f"Total items in database: {len(all_results['ids'])}")
            
            # Show some sample chunks and their filenames
            chunk_count = 0
            for i, doc_id in enumerate(all_results['ids']):
                if not doc_id.startswith("metadata_"):
                    chunk_count += 1
                    if chunk_count <= 5:  # Show first 5 chunks
                        metadata = all_results['metadatas'][i] if all_results['metadatas'] else {}
                        filename = metadata.get('filename', 'NO_FILENAME')
                        print(f"Chunk {chunk_count}: ID={doc_id}, filename={filename}")
            
            print(f"Total chunks in database: {chunk_count}")
            print("=== END DEBUG ===")

            # Perform the search
            print(f"Performing search with filter: {where_filter}")
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter
            )
            
            print(f"Raw results from ChromaDB: {len(results.get('documents', [[]])[0]) if results and results.get('documents') else 0}")

            # If no results with filter, try without filter to debug
            if not results or not results.get('documents') or not results['documents'][0]:
                print("No results with filter, trying without filter for debugging...")
                results_no_filter = self.collection.query(
                    query_texts=[query],
                    n_results=n_results
                )
                print(f"Results without filter: {len(results_no_filter.get('documents', [[]])[0]) if results_no_filter and results_no_filter.get('documents') else 0}")
                
                # If we get results without filter, the issue is with the filter
                if results_no_filter and results_no_filter.get('documents') and results_no_filter['documents'][0]:
                    print("Found results without filter - the issue is with the filename filter")
                    # For now, use results without filter
                    results = results_no_filter

            # Convert to our expected format
            formatted_results = []
            if results and results['documents'] and results['documents'][0]:
                print(f"Processing {len(results['documents'][0])} results from ChromaDB")
                for i in range(len(results['documents'][0])):
                    doc_id = results['ids'][0][i]
                    print(f"Processing result {i}: ID={doc_id}")
                    
                    # Skip metadata documents in search results (but this shouldn't happen with filename filter)
                    if doc_id.startswith("metadata_"):
                        print(f"Skipping metadata document: {doc_id}")
                        continue

                    distance = results['distances'][0][i]
                    
                    # Robust similarity calculation based on distance type
                    # ChromaDB typically uses cosine distance or L2 distance
                    # For cosine distance: similarity = 1 - distance (distance is 0-2, similarity is -1 to 1)
                    # For L2 distance: similarity = 1 / (1 + distance) (distance is 0-inf, similarity is 0-1)
                    
                    # Try to determine if it's cosine distance (typically 0-2 range) or L2 distance
                    if distance <= 2.0:  # Likely cosine distance
                        similarity = 1.0 - distance
                        distance_type = "cosine"
                    else:  # Likely L2 distance
                        similarity = 1.0 / (1.0 + distance)
                        distance_type = "L2"
                    
                    # Ensure similarity is in reasonable range (0-1)
                    similarity = max(0.0, min(1.0, similarity))
                    
                    result = {
                        'id': results['ids'][0][i],
                        'document': results['documents'][0][i],
                        'content': results['documents'][0][i],  # Alias for compatibility
                        'similarity': similarity,
                        'distance': distance,
                        'distance_type': distance_type,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
                    }

                    print(f"Result {i}: distance={distance:.3f}, similarity={similarity:.3f} ({distance_type}), threshold={threshold}")

                    # Apply threshold filter
                    if result['similarity'] >= threshold:
                        formatted_results.append(result)
                        print(f"Added result {i} to formatted_results")
                    else:
                        print(f"Result {i} below threshold, skipping")

            self.logger.info(f"Similarity search returned {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            self.logger.error(f"Similarity search failed: {str(e)}")
            return []

    def get_documents_with_filters(
            self,
            where: Optional[Dict[str, Any]] = None,
            limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get documents with metadata filtering.

        Args:
            where: ChromaDB where clause for filtering
            limit: Maximum number of documents to return

        Returns:
            List of document metadata
        """
        try:
            # Get all documents with the filter
            results = self.collection.get(where=where)

            # Filter to only return metadata documents (file-level info)
            metadata_docs = []
            for i, doc_id in enumerate(results["ids"]):
                if doc_id.startswith("metadata_"):
                    doc_info = {
                        'id': doc_id,
                        'filename': results["metadatas"][i].get('filename', ''),
                        'company': results["metadatas"][i].get('company', ''),
                        'year': results["metadatas"][i].get('year', 0),
                        'metadata': results["metadatas"][i]
                    }
                    metadata_docs.append(doc_info)

            # Limit results
            limited_results = metadata_docs[:limit]

            self.logger.info(f"Retrieved {len(limited_results)} documents with filters")
            return limited_results

        except Exception as e:
            self.logger.error(f"Document filtering failed: {str(e)}")
            return []

    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Document info or None if not found
        """
        try:
            # Ensure it's a metadata document ID
            if not doc_id.startswith("metadata_"):
                doc_id = f"metadata_{doc_id}"

            results = self.collection.get(ids=[doc_id])

            if results and results['ids']:
                return {
                    'id': results['ids'][0],
                    'filename': results['metadatas'][0].get('filename', ''),
                    'company': results['metadatas'][0].get('company', ''),
                    'year': results['metadatas'][0].get('year', 0),
                    'metadata': results['metadatas'][0]
                }

            return None

        except Exception as e:
            self.logger.error(f"Get document by ID failed: {str(e)}")
            return None

    def get_all_companies(self) -> List[str]:
        """Get list of all unique companies in the database"""
        try:
            # Get all metadata documents
            results = self.collection.get()

            companies = set()
            for i, doc_id in enumerate(results["ids"]):
                if doc_id.startswith("metadata_"):
                    company = results["metadatas"][i].get('company', '')
                    if company:
                        companies.add(company)

            company_list = sorted(list(companies))
            self.logger.info(f"Found {len(company_list)} unique companies")
            return company_list

        except Exception as e:
            self.logger.error(f"Get all companies failed: {str(e)}")
            return []

    def get_all_years(self) -> List[int]:
        """Get list of all unique years in the database"""
        try:
            # Get all metadata documents
            results = self.collection.get()

            years = set()
            for i, doc_id in enumerate(results["ids"]):
                if doc_id.startswith("metadata_"):
                    year = results["metadatas"][i].get('year', 0)
                    if year and year > 1900:  # Valid year
                        years.add(year)

            year_list = sorted(list(years))
            self.logger.info(f"Found {len(year_list)} unique years")
            return year_list

        except Exception as e:
            self.logger.error(f"Get all years failed: {str(e)}")
            return []

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            all_results = self.collection.get()
            total_items = len(all_results['ids'])

            # Count metadata docs vs chunks
            metadata_count = sum(1 for doc_id in all_results['ids'] if doc_id.startswith("metadata_"))
            chunk_count = total_items - metadata_count

            return {
                'total_items': total_items,
                'file_count': metadata_count,
                'chunk_count': chunk_count,
                'companies': len(self.get_all_companies()),
                'years': len(self.get_all_years())
            }

        except Exception as e:
            self.logger.error(f"Get collection stats failed: {str(e)}")
            return {'error': str(e)}


# Create wrapper instance
vector_store = VectorStoreWrapper(collection)


# Keep your original functions for backward compatibility
def add_document_chunks(chunks: list, metadatas: list, ids: list, file_metadata: dict):
    """
    Adds document chunks and their metadata to the ChromaDB collection.
    Also stores file-level metadata as a special document.

    Args:
        chunks (list): The list of text chunks.
        metadatas (list): A list of dictionaries, each containing chunk-specific metadata.
        ids (list): A unique ID for each chunk.
        file_metadata (dict): File-level metadata (company, year, filename).
    """
    # Add chunks to the collection
    collection.add(
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )

    # Add file metadata as a special document (no text content, just metadata)
    collection.add(
        documents=["FILE_METADATA"],  # Dummy text for the document
        metadatas=[file_metadata],
        ids=[f"metadata_{file_metadata['filename']}"]
    )

    print(f"Successfully added {len(chunks)} chunks and file metadata to the collection.")


def get_files_by_company(company: str):
    """Get all files for a specific company."""
    results = collection.get(
        where={"company": company.lower()}
    )
    # Filter to only return metadata documents (not chunks)
    metadata_results = {
        "ids": [],
        "metadatas": [],
        "documents": []
    }
    for i, doc_id in enumerate(results["ids"]):
        if doc_id.startswith("metadata_"):
            metadata_results["ids"].append(results["ids"][i])
            metadata_results["metadatas"].append(results["metadatas"][i])
            metadata_results["documents"].append(results["documents"][i])
    return metadata_results


def get_files_by_year(year: int):
    """Get all files for a specific year."""
    results = collection.get(
        where={"year": year}
    )
    # Filter to only return metadata documents (not chunks)
    metadata_results = {
        "ids": [],
        "metadatas": [],
        "documents": []
    }
    for i, doc_id in enumerate(results["ids"]):
        if doc_id.startswith("metadata_"):
            metadata_results["ids"].append(results["ids"][i])
            metadata_results["metadatas"].append(results["metadatas"][i])
            metadata_results["documents"].append(results["documents"][i])
    return metadata_results


def get_all_files():
    """Get all file metadata."""
    results = collection.get()
    # Filter to only return metadata documents (not chunks)
    metadata_results = {
        "ids": [],
        "metadatas": [],
        "documents": []
    }
    for i, doc_id in enumerate(results["ids"]):
        if doc_id.startswith("metadata_"):
            metadata_results["ids"].append(results["ids"][i])
            metadata_results["metadatas"].append(results["metadatas"][i])
            metadata_results["documents"].append(results["documents"][i])
    return metadata_results


def get_vector_store() -> VectorStoreWrapper:
    """
    Get the vector store wrapper instance.
    This function provides compatibility with the RAG services.
    """
    return vector_store