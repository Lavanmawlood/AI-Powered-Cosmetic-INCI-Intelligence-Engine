"""HTML parsing and structured data extraction for LAV LAB."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class ParsedPage:
    """Structured representation of a parsed HTML page."""

    url: str
    title: Optional[str]
    description: Optional[str]
    canonical_url: Optional[str]
    brand: Optional[str]
    price: Optional[str]
    ingredients: Optional[str]


class HTMLParser:
    """Extract structured information from HTML documents."""

    def parse(
        self,
        html: bytes | str,
        url: str,
    ) -> ParsedPage:
        """Parse HTML and extract useful metadata."""

        soup = BeautifulSoup(html, "html.parser")

        title = self._extract_title(soup)
        description = self._extract_meta(
            soup,
            "description",
        )

        canonical_url = self._extract_canonical(
            soup,
            url,
        )

        brand = self._extract_brand(soup)
        price = self._extract_price(soup)
        ingredients = self._extract_ingredients(soup)

        return ParsedPage(
            url=url,
            title=title,
            description=description,
            canonical_url=canonical_url,
            brand=brand,
            price=price,
            ingredients=ingredients,
        )

    @staticmethod
    def _clean_text(value: Optional[str]) -> Optional[str]:
        if not value:
            return None

        value = re.sub(r"\s+", " ", value).strip()

        return value or None

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        if soup.title:
            return self._clean_text(soup.title.get_text())

        og_title = soup.find(
            "meta",
            attrs={"property": "og:title"},
        )

        if og_title:
            return self._clean_text(
                og_title.get("content")
            )

        return None

    def _extract_meta(
        self,
        soup: BeautifulSoup,
        name: str,
    ) -> Optional[str]:

        tag = soup.find(
            "meta",
            attrs={"name": name},
        )

        if not tag:
            tag = soup.find(
                "meta",
                attrs={"property": f"og:{name}"},
            )

        if tag:
            return self._clean_text(
                tag.get("content")
            )

        return None

    @staticmethod
    def _extract_canonical(
        soup: BeautifulSoup,
        base_url: str,
    ) -> Optional[str]:

        tag = soup.find(
            "link",
            rel="canonical",
        )

        if not tag or not tag.get("href"):
            return None

        return urljoin(
            base_url,
            tag["href"],
        )

    def _extract_brand(
        self,
        soup: BeautifulSoup,
    ) -> Optional[str]:

        selectors = [
            '[itemprop="brand"]',
            '[property="product:brand"]',
            '.brand',
            '.product-brand',
        ]

        for selector in selectors:
            element = soup.select_one(selector)

            if element:
                value = (
                    element.get("content")
                    or element.get_text()
                )

                value = self._clean_text(value)

                if value:
                    return value

        return None

    def _extract_price(
        self,
        soup: BeautifulSoup,
    ) -> Optional[str]:

        selectors = [
            '[itemprop="price"]',
            '[property="product:price:amount"]',
            '.price',
            '.product-price',
        ]

        for selector in selectors:
            element = soup.select_one(selector)

            if element:
                value = (
                    element.get("content")
                    or element.get_text()
                )

                value = self._clean_text(value)

                if value:
                    return value

        return None

    def _extract_ingredients(
        self,
        soup: BeautifulSoup,
    ) -> Optional[str]:

        keywords = (
            "ingredients",
            "ingredient",
            "inci",
        )

        for element in soup.find_all(
            ["div", "section", "p", "li", "span"]
        ):
            text = self._clean_text(
                element.get_text(" ", strip=True)
            )

            if not text:
                continue

            lower = text.lower()

            if any(
                keyword in lower
                for keyword in keywords
            ):
                return text

        return None
