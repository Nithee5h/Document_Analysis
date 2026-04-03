from pathlib import Path
import time
from src.schemas.response import ConfidenceBlock, DocumentAnalyzeResponse, ProcessingMeta
from src.services.document_router import DocumentRouter
from src.services.classifier import DocumentClassifier
from src.services.entities import EntityExtractor
from src.services.sentiment import SentimentService
from src.services.summarizer import Summarizer
from src.utils.text_utils import truncate_text


class DocumentPipeline:
    def __init__(self) -> None:
        self.router = DocumentRouter()
        self.classifier = DocumentClassifier()
        self.entities = EntityExtractor()
        self.sentiment = SentimentService()
        self.summarizer = Summarizer()

    def process(self, file_path: Path, file_name: str, file_type: str) -> DocumentAnalyzeResponse:
        start_time = time.time()
        text, ocr_used, ocr_method = self.router.extract_text(file_path, file_type)
        doc_type = self.classifier.classify(text)
        entity_block = self.entities.extract(text, doc_type)
        summary, summary_score = self.summarizer.summarize(text, entity_block, doc_type)
        sentiment, sentiment_score = self.sentiment.analyze(text, doc_type)

        entity_quality_count = sum(
            len(getattr(entity_block, field)) for field in ["names", "dates", "organizations", "amounts"]
        )
        entity_score = 0.75 if entity_quality_count == 0 else min(0.99, 0.70 + (entity_quality_count * 0.03))

        return DocumentAnalyzeResponse(
            status="success",
            fileName=file_name,
            summary=summary,
            entities=entity_block,
            sentiment=sentiment,
            confidence=ConfidenceBlock(
                summary=round(summary_score, 2),
                entities=round(entity_score, 2),
                sentiment=round(sentiment_score, 2),
            ),
            processingMeta=ProcessingMeta(
                docType=doc_type,
                ocrUsed=ocr_used,
                ocrMethod=ocr_method,
                textLength=len(text),
                language="en",
                processingTimeMs=int((time.time() - start_time) * 1000),
            ),
            extractedTextPreview=truncate_text(text, 300),
        )
