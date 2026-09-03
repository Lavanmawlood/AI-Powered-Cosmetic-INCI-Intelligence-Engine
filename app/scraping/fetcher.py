"""HTTP fetching layer for LAV LAB."""

import logging
import time
from typing import Optional

import requests

from .config import ScraperConfig
from .exceptions import (
    FetchError,
    FetchTimeoutError,
    HTTPStatusError,
    InvalidResponseError,
)
from .models import FetchResult
from .policy import (
    ComplianceChecker,
    PolicyViolationError,
)

logger = logging.getLogger(__name__)


class HTTPFetcher:
    """Safe HTTP fetcher with compliance, retry and rate limiting."""

    RETRYABLE_STATUS_CODES = {
        408, 425, 429, 500, 502, 503, 504
    }

    def __init__(
        self,
        config: Optional[ScraperConfig] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.config = config or ScraperConfig.from_environment()
        self.session = session or requests.Session()

        self.session.headers.update({
            "User-Agent": self.config.user_agent,
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
        })

        self.compliance = ComplianceChecker(
            user_agent=self.config.user_agent
        )

        self._last_request_time = 0.0

    def _rate_limit(self) -> None:
        """Respect the configured delay between requests."""

        elapsed = time.monotonic() - self._last_request_time
        remaining = self.config.rate_limit_seconds - elapsed

        if remaining > 0:
            time.sleep(remaining)

    def fetch(self, url: str) -> FetchResult:
        """Fetch a URL after compliance validation."""

        try:
            self.compliance.check(url)
        except PolicyViolationError as exc:
            logger.warning(
                "Request blocked by scraping policy: %s",
                url,
            )
            raise FetchError(
                f"Scraping policy blocked URL: {url}"
            ) from exc

        last_error = None

        for attempt in range(
            1,
            self.config.max_retries + 1
        ):
            self._rate_limit()
            started = time.monotonic()

            try:
                logger.info(
                    "Fetching %s (attempt %s/%s)",
                    url,
                    attempt,
                    self.config.max_retries,
                )

                response = self.session.get(
                    url,
                    timeout=self.config.timeout,
                    allow_redirects=True,
                )

                elapsed = time.monotonic() - started
                self._last_request_time = time.monotonic()

                if response.status_code >= 400:
                    if (
                        response.status_code
                        in self.RETRYABLE_STATUS_CODES
                        and attempt < self.config.max_retries
                    ):
                        delay = (
                            self.config.backoff_factor
                            * (2 ** (attempt - 1))
                        )

                        logger.warning(
                            "Retryable HTTP status %s. "
                            "Retrying in %.2fs.",
                            response.status_code,
                            delay,
                        )

                        time.sleep(delay)
                        continue

                    raise HTTPStatusError(
                        f"HTTP {response.status_code}: {url}"
                    )

                if not response.content:
                    raise InvalidResponseError(
                        f"Empty response: {url}"
                    )

                logger.info(
                    "Fetch successful: %s in %.3fs",
                    response.status_code,
                    elapsed,
                )

                return FetchResult(
                    url=response.url,
                    status_code=response.status_code,
                    content=response.content,
                    content_type=response.headers.get(
                        "Content-Type"
                    ),
                    elapsed_seconds=elapsed,
                )

            except requests.Timeout as exc:
                last_error = exc

                if attempt < self.config.max_retries:
                    delay = (
                        self.config.backoff_factor
                        * (2 ** (attempt - 1))
                    )

                    logger.warning(
                        "Timeout. Retrying in %.2fs.",
                        delay,
                    )

                    time.sleep(delay)
                    continue

                raise FetchTimeoutError(
                    f"Request timed out: {url}"
                ) from exc

            except requests.RequestException as exc:
                last_error = exc

                if attempt < self.config.max_retries:
                    delay = (
                        self.config.backoff_factor
                        * (2 ** (attempt - 1))
                    )

                    logger.warning(
                        "Request error. Retrying in %.2fs.",
                        delay,
                    )

                    time.sleep(delay)
                    continue

                raise FetchError(
                    f"Failed to fetch {url}: {exc}"
                ) from exc

        raise FetchError(
            f"Failed to fetch {url}: {last_error}"
        )


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
