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
                model_name="text-embedding-3-small"
            )

# Create or get the collection.
# We pass the embedding function so ChromaDB knows how to handle documents.
collection = client.get_or_create_collection(
    name="financial_documents",
    embedding_function=openai_ef
)

def add_document_chunks(chunks: list, metadatas: list, ids: list):
    """
    Adds document chunks and their metadata to the ChromaDB collection.

    Args:
        chunks (list): The list of text chunks.
        metadatas (list): A list of dictionaries, each containing metadata for a chunk.
        ids (list): A unique ID for each chunk.
    """
    # ChromaDB's add function takes documents, metadatas, and ids.
    # 'documents' here refers to the text chunks you want to embed.
    collection.add(
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Successfully added {len(chunks)} chunks to the collection.")