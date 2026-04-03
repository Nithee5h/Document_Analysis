from typing import List, Dict, Optional
from pydantic import BaseModel


class EntityBlock(BaseModel):
    names: List[str] = []
    dates: List[str] = []
    organizations: List[str] = []
    amounts: List[str] = []


class ConfidenceBlock(BaseModel):
    summary: float
    entities: float
    sentiment: float


class ProcessingMeta(BaseModel):
    docType: str
    ocrUsed: bool
    ocrMethod: Optional[str] = None  # "vision_api" or "tesseract" or None
    textLength: int
    language: str = "en"
    processingTimeMs: int = 0


class DocumentAnalyzeResponse(BaseModel):
    status: str
    fileName: str
    summary: str
    entities: EntityBlock
    sentiment: str
    confidence: Optional[ConfidenceBlock] = None
    processingMeta: Optional[ProcessingMeta] = None
    extractedTextPreview: Optional[str] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str