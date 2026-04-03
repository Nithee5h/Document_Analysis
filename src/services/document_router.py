from pathlib import Path
from src.services.extractor_pdf import PDFExtractor
from src.services.extractor_docx import DOCXExtractor
from src.services.extractor_image import ImageExtractor


class DocumentRouter:
    def __init__(self) -> None:
        self.pdf_extractor = PDFExtractor()
        self.docx_extractor = DOCXExtractor()
        self.image_extractor = ImageExtractor()

    def extract_text(self, file_path: Path, file_type: str) -> tuple[str, bool, str | None]:
        if file_type == "pdf":
            text, used = self.pdf_extractor.extract(file_path)
            return text, used, None  # PDFs don't use OCR methods
        if file_type == "docx":
            text, used = self.docx_extractor.extract(file_path)
            return text, used, None  # DOCX doesn't use OCR methods
        if file_type == "image":
            return self.image_extractor.extract(file_path)
        raise ValueError(f"Unsupported file type: {file_type}")