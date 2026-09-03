"""Scraping pipeline that combines fetcher and parser."""

import logging
from typing import Optional

from app.scraping.fetcher import HTTPFetcher
from app.scraping.parser import HTMLParser, ParsedPage

logger = logging.getLogger(__name__)


class ScrapingPipeline:
    """Combine fetcher and parser into a single pipeline."""

    def __init__(self):
        self.fetcher = HTTPFetcher()
        self.parser = HTMLParser()

    def scrape(self, url: str) -> Optional[ParsedPage]:
        """
        Fetch and parse a single URL.

        Args:
            url: The URL to scrape

        Returns:
            ParsedPage if successful, None otherwise
        """
        logger.info(f"Scraping: {url}")

        result = self.fetcher.fetch(url)

        if not result or not result.content:
            logger.warning(f"No HTML returned for: {url}")
            return None

        try:
            parsed = self.parser.parse(result.content, url)
            logger.info(f"Successfully parsed: {url}")
            return parsed

        except Exception as e:
            logger.error(f"Parser error for {url}: {e}")
            return None
