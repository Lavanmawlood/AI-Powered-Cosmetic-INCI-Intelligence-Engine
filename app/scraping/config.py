"""Scraper configuration."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class ScraperConfig:
    """Runtime configuration for HTTP fetching."""

    timeout: float = 30.0
    max_retries: int = 3
    backoff_factor: float = 1.0
    rate_limit_seconds: float = 1.0

    user_agent: str = (
        "LAV-LAB/0.1 "
        "(+https://github.com/Lavanmawlood/"
        "AI-Powered-Cosmetic-INCI-Intelligence-Engine)"
    )

    @classmethod
    def from_environment(cls) -> "ScraperConfig":
        """Load configuration from environment variables."""

        return cls(
            timeout=float(os.getenv("SCRAPER_TIMEOUT", "30")),
            max_retries=int(
                os.getenv("SCRAPER_MAX_RETRIES", "3")
            ),
            backoff_factor=float(
                os.getenv("SCRAPER_BACKOFF_FACTOR", "1")
            ),
            rate_limit_seconds=float(
                os.getenv("SCRAPER_RATE_LIMIT", "1")
            ),
            user_agent=os.getenv(
                "SCRAPER_USER_AGENT",
                cls.user_agent,
            ),
        )
