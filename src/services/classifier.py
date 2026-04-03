import re
import logging

logger = logging.getLogger(__name__)


class DocumentClassifier:
    def _extract_title(self, text: str) -> str:
        """Extract the first line as potential title."""
        lines = text.split('\n')
        for line in lines:
            clean = line.strip()
            if clean and len(clean) > 5:
                return clean
        return ""

    def _get_content_section(self, text: str) -> str:
        """Get the main body text, excluding first few lines (potential title)."""
        lines = text.split('\n')
        # Skip first line and get next few lines for content analysis
        content = ' '.join(lines[1:10]) if len(lines) > 1 else text
        return content.lower()

    def classify(self, text: str) -> str:
        """Classify document based on PRIMARY purpose and content analysis."""
        title = self._extract_title(text)
        content = self._get_content_section(text)
        lower = text.lower()  # Full text for comprehensive analysis
        
        # Count keyword frequencies in FULL TEXT (not just excerpt)
        resume_keywords = ["experience", "skills", "education", "portfolio", "professional", "employment"]
        incident_keywords = ["incident", "breach", "unauthorized", "fraudulent", "compromise", "attack"]
        invoice_keywords = ["invoice", "bill to", "amount due", "subtotal", "total payable"]
        article_keywords = ["analysis", "research", "findings", "conclusion", "introduction"]
        
        # Check in both title and full content
        resume_count = sum(1 for kw in resume_keywords if kw in lower)
        incident_count = sum(1 for kw in incident_keywords if kw in lower)
        invoice_count = sum(1 for kw in invoice_keywords if kw in lower)
        article_count = sum(1 for kw in article_keywords if kw in lower)
        
        # Title-based classification (analyze title separately) with heavier weight
        title_lower = title.lower()
        if any(kw in title_lower for kw in ["resume", "cv", "curriculum", "vitae"]):
            resume_count += 5
        if any(kw in title_lower for kw in ["incident", "breach", "security attack"]):
            incident_count += 5
        if any(kw in title_lower for kw in ["invoice", "bill", "receipt"]):
            invoice_count += 5
        if any(kw in title_lower for kw in ["analysis", "research", "study", "report"]):
            article_count += 5
        
        # Classify based on highest score with tie-breaking rules
        scores = {
            "resume": resume_count,
            "incident_report": incident_count,
            "invoice": invoice_count,
            "article": article_count
        }
        
        # Default classification based on document structure
        if len(re.findall(r"\n", text)) > 5 and len(text.split()) > 150:
            scores["article"] += 2
        
        # Tie-breaking: prefer article/incident for longer documents
        max_score = max(scores.values())
        if max_score == 0:
            return "general_document"
        
        # Get the document type with highest score
        best_type = max(scores, key=scores.get)
        return best_type