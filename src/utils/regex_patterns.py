import re

# Enhanced date patterns including resume date ranges (e.g., "June 2020 – Present")
# IMPORTANT: These patterns match both STRUCTURED dates and common VAGUE date phrases
DATE_PATTERNS = [
    # Resume date range: "June 2020 – Present" or "June 2020 - May 2021"
    re.compile(r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\s+[–—-]\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Present)(?:\s+\d{4})?", re.IGNORECASE),
    # Month Year format: "June 2020", "Jan 2021"
    re.compile(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b", re.IGNORECASE),
    # Day Month Year: "15 June 2020", "1 January 2024"
    re.compile(r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b", re.IGNORECASE),
    # DD/MM/YYYY or DD-MM-YYYY
    re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
    # YYYY-MM-DD format
    re.compile(r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b"),
    # Abbreviated format: Jan 2020, Mar 2021 (with optional period)
    re.compile(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{4}\b", re.IGNORECASE),
    # Vague date phrases: "past few years", "coming decade", "recent times"
    re.compile(r"(?:the\s+)?(?:past|recent|coming|future|next|last)\s+(?:few\s+)?(?:years?|decades?|months?|weeks?|centuries?|times?)", re.IGNORECASE),
]

# Vague date phrases that should be FILTERED OUT
VAGUE_DATE_TERMS = {
    "the past", "the coming", "recent", "future", "current", "today", "yesterday", 
    "last year", "next year", "few years", "decade", "century", "era", "period"
}

AMOUNT_PATTERNS = [
    re.compile(r"(?:₹|\$|€|£)\s?\d+(?:,\d{3})*(?:\.\d{2})?"),
    re.compile(r"\b(?:Rs\.?|Rs)\s?\d+(?:,\d{3})*(?:\.\d{2})?\b", re.IGNORECASE),
    re.compile(r"\b(?:USD|INR|EUR|GBP)\s?\d+(?:,\d{3})*(?:\.\d{2})?\b", re.IGNORECASE),
    re.compile(r"\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:₹|Rs\.?|Rs|dollars|euros|pounds)\b", re.IGNORECASE),
]

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)?\d{3}[\s-]?\d{4}")
WEBSITE_PATTERN = re.compile(r"\b(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}\b")