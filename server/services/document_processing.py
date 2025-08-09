import re
from pypdf import PdfReader
from storage import vector_store

def _parse_filename(filename: str) -> dict:
    """
    Parses the filename to extract company and year using regex.
    Example: "amazon_2023_report.pdf" -> {"company": "amazon", "year": 2023}
    """
    # Regex to find company name (letters) and year (4 digits)
    match = re.match(r"([a-zA-Z]+)_(\d{4})", filename)
    if match:
        company, year = match.groups()
        return {"company": company.lower(), "year": int(year)}
    # Return a default if the pattern doesn't match
    return {"company": "unknown", "year": 0}

def _extract_text_from_pdf(file_path: str) -> str:
    """Extracts text from a single PDF file."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def process_and_store(file_path: str, filename: str):
    """
    Main function to process a single PDF and store it in the vector DB.
    """
    print(f"Processing {filename}...")

    # 1. Parse filename for metadata
    metadata_base = _parse_filename(filename)
    if metadata_base["company"] == "unknown":
        print(f"Warning: Could not parse company and year from {filename}.")

    # 2. Extract text from PDF
    full_text = _extract_text_from_pdf(file_path)
    if not full_text:
        print(f"Warning: No text extracted from {filename}.")
        return

    # 3. Chunk the text (simple example: split by paragraph)
    chunks = full_text.split("\n\n")
    # Filter out empty or very short chunks
    chunks = [chunk for chunk in chunks if len(chunk.strip()) > 100]

    # 4. Prepare data for ChromaDB
    metadatas = []
    ids = []
    for i, chunk in enumerate(chunks):
        # Create metadata for each chunk
        chunk_metadata = metadata_base.copy()
        chunk_metadata["filename"] = filename
        chunk_metadata["chunk_number"] = i
        metadatas.append(chunk_metadata)

        # Create a unique ID for each chunk
        ids.append(f"{filename}_chunk_{i}")

    # 5. Add to vector store
    # Note: We pass the text 'chunks' as 'documents' to ChromaDB.
    # ChromaDB will automatically use the OpenAI function to create embeddings.
    vector_store.add_document_chunks(
        chunks=chunks,
        metadatas=metadatas,
        ids=ids
    )