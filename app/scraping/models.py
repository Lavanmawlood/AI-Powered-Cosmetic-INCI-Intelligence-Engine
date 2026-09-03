"""Data models for the scraping engine."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class FetchResult:
    """Normalized HTTP fetch result."""

    url: str
    status_code: int
    content: bytes
    content_type: Optional[str]
    elapsed_seconds: float
