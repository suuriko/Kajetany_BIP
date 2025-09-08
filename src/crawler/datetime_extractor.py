import re
from datetime import datetime
from typing import Optional

DATETIME_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b(\d{2}\.\d{2}\.\d{4})\b"), "%d.%m.%Y"),
    (re.compile(r"\b(\d{4}-\d{2}-\d{2})\b"), "%Y-%m-%d"),
    (re.compile(r"\b(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\b"), "%Y-%m-%d %H:%M"),
]


def extract_datetime(text: Optional[str]) -> Optional[datetime]:
    """Extract a datetime object from text using known patterns."""
    if not text:
        return None
    for pattern, date_format in DATETIME_PATTERNS:
        match = pattern.search(text)
        if match:
            try:
                return datetime.strptime(match.group(1), date_format)
            except ValueError:
                return None
    return None
