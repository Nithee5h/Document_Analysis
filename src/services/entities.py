from __future__ import annotations
from dataclasses import dataclass
import re
import spacy
import logging
from src.core.config import settings
from src.schemas.response import EntityBlock
from src.utils.regex_patterns import DATE_PATTERNS, AMOUNT_PATTERNS, EMAIL_PATTERN, PHONE_PATTERN, WEBSITE_PATTERN, VAGUE_DATE_TERMS
from src.utils.text_utils import unique_preserve_order

logger = logging.getLogger(__name__)


@dataclass
class LoadedModels:
    nlp: object


class EntityExtractor:
    def __init__(self) -> None:
        try:
            self.models = LoadedModels(nlp=spacy.load(settings.spacy_model))
        except OSError:
            raise RuntimeError(f"Spacy model '{settings.spacy_model}' not found. Please run: python -m spacy download {settings.spacy_model}")

    def _is_temporal_phrase(self, date_text: str) -> bool:
        """Check if text is a temporal phrase we want to keep (e.g., 'the past few years')."""
        temporal_pattern = re.compile(
            r"(?:the\s+)?(?:past|recent|coming|future|next|last)\s+(?:few\s+)?(?:years?|decades?|months?|weeks?|centuries?|times?)",
            re.IGNORECASE
        )
        return bool(temporal_pattern.search(date_text))

    def _is_vague_date(self, date_text: str) -> bool:
        """Check if a date is vague (e.g., 'the past few years') and should be filtered."""
        date_lower = date_text.lower()
        for vague_term in VAGUE_DATE_TERMS:
            if vague_term in date_lower:
                return True
        return False

    def _filter_dates(self, dates: list[str]) -> list[str]:
        """Filter out vague dates, but keep temporal phrases like 'the past few years'."""
        filtered = []
        for date in dates:
            # Keep temporal phrases even if they contain vague terms
            if self._is_temporal_phrase(date):
                filtered.append(date)
                continue
            # Skip other vague dates
            if self._is_vague_date(date):
                continue
            # Skip if it's just a year
            if re.match(r'^\d{4}$', date.strip()):
                continue
            # Keep structured dates
            filtered.append(date)
        return filtered

    def _is_valid_name(self, name: str) -> bool:
        """Check if text is likely a real person name, not junk."""
        # Filter out single words that are common adjectives/articles
        single_word_filters = {
            "smart", "bright", "great", "ai", "the", "a", "an", "and", "or", "but",
            "is", "was", "are", "be", "been", "being"
        }
        
        if name.lower() in single_word_filters:
            return False
        
        # Names should have at least one capital letter (for proper nouns)
        if not any(c.isupper() for c in name):
            return False
            
        # Single letter names are likely errors
        if len(name.strip()) <= 1:
            return False
            
        return True

    def _is_document_title_or_headline(self, text: str) -> bool:
        """Check if text is likely a document title or headline."""
        # Skip if all caps (typical for titles)
        if text.isupper() and len(text) > 3:
            return True
        # Skip title-like phrases that start with capital and contain report/incident/analysis
        title_terms = {"report", "incident", "analysis", "summary", "overview", "guide", "manual"}
        words_lower = [w.lower().strip('.,;:!?') for w in text.split()]
        
        # If it's a capitalized phrase with 2+ words and contains title terms, likely a title
        if len(words_lower) >= 2 and text[0].isupper():
            # Check if any title term is present
            if any(term in words_lower for term in title_terms):
                return True
        
        return False

    def _extract_document_title(self, text: str) -> str:
        """Extract the potential document title (usually first line)."""
        lines = text.split('\n')
        for line in lines:
            clean = line.strip()
            if clean and len(clean) > 5:
                return clean
        return ""

    def _filter_organizations(self, organizations: list[str], doc_title: str = "") -> list[str]:
        """Filter out document titles and generic phrases from organizations."""
        filtered = []
        generic_terms = {
            "report", "incident", "data", "breach", "unauthorized", 
            "access", "security", "analysis", "document"
        }
        
        for org in organizations:
            # Skip if it's the document title
            if org.lower().strip() == doc_title.lower().strip():
                continue
            # Skip if it matches title pattern (all caps, short, etc.)
            if self._is_document_title_or_headline(org):
                continue
            # Skip if all words are generic terms
            words = [w.lower().strip('.,;:!?') for w in org.split()]
            if all(word in generic_terms for word in words if word):
                continue
            # Skip if mostly numbers or symbols
            if not any(c.isalpha() for c in org):
                continue
            # Skip if it's only punctuation or very short
            if len(org.strip()) < 2 or not org[0].isalpha():
                continue
            filtered.append(org)
        return filtered

    def extract(self, text: str, doc_type: str) -> EntityBlock:
        doc = self.models.nlp(text)
        names: list[str] = []
        dates: list[str] = []
        organizations: list[str] = []
        amounts: list[str] = []

        # Extract document title once for filtering
        doc_title = self._extract_document_title(text)

        # Extract entities from Spacy
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                names.append(ent.text)
            elif ent.label_ in {"ORG", "GPE", "LOC"}:
                organizations.append(ent.text)
            elif ent.label_ == "DATE":
                dates.append(ent.text)
            elif ent.label_ == "MONEY":
                amounts.append(ent.text)

        # Extract dates using regex patterns (improved with resume date ranges)
        for pattern in DATE_PATTERNS:
            matched = pattern.findall(text)
            if matched:
                dates.extend(matched if isinstance(matched[0], str) else [m[0] if isinstance(m, tuple) else m for m in matched])

        # Filter out vague dates
        dates = self._filter_dates(dates)

        # Extract amounts
        for pattern in AMOUNT_PATTERNS:
            amounts.extend(match[0] if isinstance(match, tuple) else match for match in pattern.findall(text))

        # Filter organizations to remove titles and generic terms
        organizations = self._filter_organizations(organizations, doc_title)

        # Filter names to remove junk entries
        names = [name for name in names if self._is_valid_name(name)]

        if doc_type == "resume":
            email_hits = EMAIL_PATTERN.findall(text)
            phone_hits = PHONE_PATTERN.findall(text)
            website_hits = WEBSITE_PATTERN.findall(text)
            # Don't add emails/phones/websites as organizations - they're contact info
            # organizations.extend(email_hits)  # Removed: emails aren't organizations
            # organizations.extend(phone_hits)  # Removed: phones aren't organizations
            # organizations.extend(website_hits)  # Removed: websites aren't organizations

            top_lines = text.splitlines()[:8]
            for line in top_lines:
                clean = line.strip()
                if clean and len(clean.split()) in {2, 3} and clean[0].isupper() and not re.search(r"@|\d", clean):
                    if self._is_valid_name(clean):  # Filter with validity check
                        names.append(clean)

        return EntityBlock(
            names=unique_preserve_order(names),
            dates=unique_preserve_order(dates),
            organizations=unique_preserve_order(organizations),
            amounts=unique_preserve_order(amounts),
        )