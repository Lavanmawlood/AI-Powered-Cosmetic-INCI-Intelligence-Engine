"""Robots.txt compliance layer for LAV LAB."""

from __future__ import annotations

import logging
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

logger = logging.getLogger(__name__)


class RobotsChecker:
    """Check whether a URL may be fetched according to robots.txt."""

    def __init__(
        self,
        user_agent: str,
        timeout: float = 10.0,
    ) -> None:
        self.user_agent = user_agent
        self.timeout = timeout
        self._cache: dict[str, RobotFileParser] = {}

    def _robots_url(self, url: str) -> str:
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            raise ValueError(f"Unsupported URL scheme: {parsed.scheme}")

        return f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    def _load(self, url: str) -> RobotFileParser:
        robots_url = self._robots_url(url)
        origin = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

        if origin in self._cache:
            return self._cache[origin]

        parser = RobotFileParser()
        parser.set_url(robots_url)

        try:
            response = requests.get(
                robots_url,
                headers={"User-Agent": self.user_agent},
                timeout=self.timeout,
            )

            if response.status_code == 404:
                logger.info(
                    "No robots.txt found for %s. "
                    "Continuing with normal HTTP policy.",
                    origin,
                )
                parser.parse([])
            elif response.status_code >= 400:
                logger.warning(
                    "Could not reliably read robots.txt for %s "
                    "(HTTP %s). Access will be denied.",
                    origin,
                    response.status_code,
                )
                parser.parse(["User-agent: *", "Disallow: /"])
            else:
                parser.parse(response.text.splitlines())

        except requests.RequestException as exc:
            logger.warning(
                "Failed to retrieve robots.txt from %s: %s. "
                "Access will be denied.",
                robots_url,
                exc,
            )
            parser.parse(["User-agent: *", "Disallow: /"])

        self._cache[origin] = parser
        return parser

    def can_fetch(self, url: str) -> bool:
        """Return True when robots.txt permits the configured user-agent."""

        parser = self._load(url)

        allowed = parser.can_fetch(
            self.user_agent,
            url,
        )

        if not allowed:
            logger.warning(
                "Robots.txt disallows fetching: %s",
                url,
            )

        return allowed
