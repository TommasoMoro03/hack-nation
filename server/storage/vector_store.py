import chromadb
from chromadb.utils import embedding_functions
from core.config import settings

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