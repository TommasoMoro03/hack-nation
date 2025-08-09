import re
from pypdf import PdfReader
from storage import vector_store
from langchain.text_splitter import RecursiveCharacterTextSplitter


def _parse_filename(filename: str) -> dict:
    """
    Parses the filename to extract company and year using regex.
    """
    match = re.match(r"([A-Za-z0-9]+)_(\d{4})", filename)  # Updated regex for names like ADOBE
    if match:
        company, year = match.groups()
        return {"company": company.lower(), "year": int(year)}
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
    file_metadata = _parse_filename(filename)
    file_metadata["filename"] = filename  # Add filename to file metadata
    
    if file_metadata["company"] == "unknown":
        print(f"Warning: Could not parse company and year from {filename}.")

    # 2. Extract text from PDF
    full_text = _extract_text_from_pdf(file_path)
    if not full_text:
        print(f"Warning: No text extracted from {filename}.")
        return

    # 3. Chunk the text using LangChain's RecursiveCharacterTextSplitter
    # This splitter is token-aware and will try to split on logical separators
    # first (like paragraphs) before forcing a split by character count.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # The target size for each chunk in characters
        chunk_overlap=200,  # The number of characters to overlap between chunks
        length_function=len,
        is_separator_regex=False,
    )

    chunks = text_splitter.split_text(full_text)

    # 4. Prepare data for ChromaDB
    # Include file metadata in chunks for querying, but keep it minimal
    metadatas = []
    ids = []
    for i, chunk in enumerate(chunks):
        chunk_metadata = {
            "filename": filename,  # Reference to the file
            "chunk_number": i,
            "total_chunks": len(chunks),
            "company": file_metadata["company"],  # For querying
            "year": file_metadata["year"]  # For querying
        }
        metadatas.append(chunk_metadata)
        ids.append(f"{filename}_chunk_{i}")

    # 5. Add to vector store with separate file metadata
    vector_store.add_document_chunks(
        chunks=chunks,
        metadatas=metadatas,
        ids=ids,
        file_metadata=file_metadata
    )
