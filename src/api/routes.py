import os
import base64
import tempfile
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from src.core.config import settings
from src.core.security import validate_api_key
from src.schemas.request import DocumentAnalyzeRequest
from src.schemas.response import DocumentAnalyzeResponse
from src.services.document_pipeline import DocumentPipeline


router = APIRouter()
pipeline = DocumentPipeline()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}


@router.post("/api/document-analyze", response_model=DocumentAnalyzeResponse)
def analyze_document(
    payload: DocumentAnalyzeRequest,
    _: str = Depends(validate_api_key),
) -> DocumentAnalyzeResponse:
    """
    Analyze a document file.
    Accepts JSON with base64-encoded file content.
    """
    temp_path = None
    try:
        # Decode base64 content
        file_content = base64.b64decode(payload.fileBase64)
        
        # Check file size
        file_size_mb = len(file_content) / (1024 * 1024)
        if file_size_mb > settings.max_file_size_mb:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds {settings.max_file_size_mb} MB limit",
            )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(
            suffix=f".{payload.fileType}",
            delete=False,
            dir=tempfile.gettempdir()
        ) as tmp:
            tmp.write(file_content)
            temp_path = Path(tmp.name)
        
        # Process the file
        return pipeline.process(temp_path, payload.fileName, payload.fileType)
    
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(exc)}"
        ) from exc
    finally:
        # Clean up temporary file
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass