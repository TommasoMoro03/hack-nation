import re
from pypdf import PdfReader
from storage import vector_store
from langchain.text_splitter import RecursiveCharacterTextSplitter
from docling.document_converter import DocumentConverter  # New import for Docling


def _parse_filename(filename: str) -> dict:
    """
    Parses the filename to extract company and year using regex.
    """
    match = re.match(r"([A-Za-z0-9]+)_(\d{4})", filename)  # Updated regex for names like ADOBE
    if match:
        company, year = match.groups()
        return {"company": company.lower(), "year": int(year)}
    return {"company": "unknown", "year": 0}


"""
def _extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text
"""


def _extract_text_from_pdf(file_path: str) -> str:
    """Extracts text from a single PDF file using Docling's DocumentConverter.
    Converts PDF to Markdown first, then extracts text from the Markdown content.

    Args:
        file_path: Path to the PDF file

    Returns:
        Extracted text as a single string
    """
    try:
        from docling import DocumentConverter
        import tempfile
        import os

        # Create a temporary directory for conversion
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize DocumentConverter
            converter = DocumentConverter()

            # Convert PDF to Markdown in the temp directory
            md_file_path = os.path.join(temp_dir, "converted.md")
            converter.convert(
                input_path=file_path,
                output_path=md_file_path,
                input_format="pdf",
                output_format="markdown",
                options={
                    "tables": True,  # Extract tables
                    "formatting": True,  # Preserve formatting
                    "footnotes": True,  # Include footnotes
                    "comments": False  # Exclude comments for cleaner text
                }
            )

            # Read the converted Markdown file
            with open(md_file_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            # Remove excessive Markdown formatting if needed
            # This keeps the text clean while preserving structure
            clean_text = re.sub(r'#{1,6}\s*', '', markdown_content)  # Remove headers
            clean_text = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', clean_text)  # Remove bold/italic
            clean_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', clean_text)  # Remove links
            clean_text = re.sub(r'`{3}.*?`{3}', '', clean_text, flags=re.DOTALL)  # Remove code blocks

            return clean_text.strip()

    except Exception as e:
        print(f"Error converting PDF with Docling: {e}")
        # Fallback to PyPDF if Docling fails
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as fallback_e:
            print(f"Fallback extraction also failed: {fallback_e}")
            return ""



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
