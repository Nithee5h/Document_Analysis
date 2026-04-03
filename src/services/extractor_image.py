from pathlib import Path
from src.services.ocr_service import OCRService
from src.utils.text_utils import normalize_whitespace


class ImageExtractor:
    def __init__(self) -> None:
        self.ocr = OCRService()

    def extract(self, file_path: Path) -> tuple[str, bool, str]:
        text, ocr_used, ocr_method = self.ocr.extract_text(file_path)
        return normalize_whitespace(text), ocr_used, ocr_method