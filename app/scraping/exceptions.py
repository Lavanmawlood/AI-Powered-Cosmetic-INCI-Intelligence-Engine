"""Exceptions for the LAV LAB scraping engine."""


class ScrapingError(Exception):
    """Base scraping exception."""


class FetchError(ScrapingError):
    """HTTP fetching failed."""


class FetchTimeoutError(FetchError):
    """HTTP request timed out."""


class HTTPStatusError(FetchError):
    """HTTP response returned an unsuccessful status."""


class InvalidResponseError(FetchError):
    """HTTP response was invalid or empty."""
