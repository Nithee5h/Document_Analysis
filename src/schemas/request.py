from pydantic import BaseModel, Field


class DocumentAnalyzeRequest(BaseModel):
    fileName: str = Field(..., min_length=1)
    fileType: str = Field(..., pattern="^(pdf|docx|image)$")
    fileBase64: str = Field(..., min_length=10)