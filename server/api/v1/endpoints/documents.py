import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
from services.documents import document_processing
from storage import vector_store

router = APIRouter()

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Receives PDF files, saves them temporarily, processes them,
    and stores their embeddings in the vector database.
    """
    # Temporary directory to store uploaded files
    temp_dir = "../pdfs"

    processed_files = []
    failed_files = []

    for file in files:
        if file.content_type != "application/pdf":
            failed_files.append({"filename": file.filename, "error": "Invalid file type"})
            continue

        try:
            # Save the file temporarily
            temp_file_path = f"{temp_dir}/{file.filename}"
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Trigger the main processing service
            document_processing.process_and_store(file_path=temp_file_path, filename=file.filename)
            processed_files.append(file.filename)

        except Exception as e:
            failed_files.append({"filename": file.filename, "error": str(e)})
        finally:
            # Always close the file
            file.file.close()

    if failed_files:
        # If some files failed, return a partial success message
        return {"processed_files": processed_files, "failed_files": failed_files}

    return {"message": "All files processed and stored successfully.", "processed_files": processed_files}

@router.get("/files")
async def get_all_files():
    """
    Get metadata for all processed files.
    """
    try:
        results = vector_store.get_all_files()
        return {"files": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/company/{company}")
async def get_files_by_company(company: str):
    """
    Get all files for a specific company.
    """
    try:
        results = vector_store.get_files_by_company(company)
        return {"files": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/year/{year}")
async def get_files_by_year(year: int):
    """
    Get all files for a specific year.
    """
    try:
        results = vector_store.get_files_by_year(year)
        return {"files": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))