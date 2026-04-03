from pathlib import Path
import fitz
import pdfplumber
from PIL import Image
from src.services.ocr_service import OCRService
from src.utils.text_utils import normalize_whitespace


class PDFExtractor:
    def __init__(self) -> None:
        self.ocr = OCRService()

    def extract(self, file_path: Path) -> tuple[str, bool]:
        text_blocks = []
        ocr_used = False

        with fitz.open(file_path) as doc:
            for page in doc:
                blocks = page.get_text("blocks")
                blocks_sorted = sorted(blocks, key=lambda b: (b[1], b[0]))
                page_text = "\n".join(block[4] for block in blocks_sorted if len(block) > 4 and block[4].strip())
                if page_text.strip():
                    text_blocks.append(page_text)

        text = normalize_whitespace("\n\n".join(text_blocks))

        if len(text) > 80:
            return text, ocr_used

        with fitz.open(file_path) as doc:
            for index, page in enumerate(doc):
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_path = file_path.with_name(f"page_{index}.png")
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img.save(img_path)
                page_text, _ = self.ocr.extract_text(img_path)
        return text, ocr_used