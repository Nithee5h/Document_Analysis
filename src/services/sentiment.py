class SentimentService:
    def __init__(self) -> None:
        self.model = None

    def _load_model(self):
        if self.model is None:
            from transformers import pipeline as nlp_pipeline
            self.model = nlp_pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    def analyze(self, text: str, doc_type: str) -> tuple[str, float]:
        if doc_type in {"resume", "invoice", "general_document"}:
            return "Neutral", 0.95
        if doc_type == "incident_report":
            return "Negative", 0.98
        if doc_type == "article":
            lower = text.lower()
            if any(word in lower for word in ["growth", "innovation", "benefits", "improve", "opportunities"]):
                return "Positive", 0.92

        self._load_model()
        short_text = text[:1200]
        result = self.model(short_text)[0]
        label = result["label"].capitalize()
        score = float(result["score"])
        if label not in {"Positive", "Negative"}:
            label = "Neutral"
        return label, score