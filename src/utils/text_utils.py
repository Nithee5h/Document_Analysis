from typing import Iterable


def normalize_whitespace(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def truncate_text(text: str, max_chars: int = 300) -> str:
    return text if len(text) <= max_chars else text[:max_chars] + "..."


def unique_preserve_order(items: Iterable[str]) -> list[str]:
    seen = set()
    output = []
    for item in items:
        cleaned = item.strip()
        if cleaned and cleaned.lower() not in seen:
            seen.add(cleaned.lower())
            output.append(cleaned)
    return output