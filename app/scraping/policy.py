"""Compliance policy layer for LAV LAB scraping."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from urllib.parse import urlparse

from .robots import RobotsChecker

logger = logging.getLogger(__name__)


class PolicyViolationError(Exception):
    """Raised when a URL violates the scraping policy."""


@dataclass(frozen=True)
class ScrapingPolicy:
    """Rules controlling whether a URL may be fetched."""

    require_http_https: bool = True
    respect_robots_txt: bool = True

    def validate_url(self, url: str) -> None:
        """Validate basic URL policy."""

        parsed = urlparse(url)

        if self.require_http_https and parsed.scheme not in {
            "http",
            "https",
        }:
            raise PolicyViolationError(
                f"Unsupported URL scheme: {parsed.scheme!r}"
            )

        if not parsed.netloc:
            raise PolicyViolationError(
                f"Invalid URL: {url!r}"
            )


class ComplianceChecker:
    """Apply URL and robots.txt compliance rules."""

    def __init__(
        self,
        user_agent: str,
        policy: ScrapingPolicy | None = None,
    ) -> None:
        self.policy = policy or ScrapingPolicy()
        self.robots = RobotsChecker(user_agent=user_agent)

    def check(self, url: str) -> None:
        """Raise PolicyViolationError if fetching is not permitted."""

        self.policy.validate_url(url)

        if (
            self.policy.respect_robots_txt
            and not self.robots.can_fetch(url)
        ):
            raise PolicyViolationError(
                f"Fetching disallowed by robots.txt: {url}"
            )
