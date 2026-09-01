
import re


class INCIParser:
    """
    Basic parser for cosmetic INCI lists.

    Responsibilities:
    - Validate input
    - Split ingredients
    - Remove unnecessary whitespace
    - Preserve ingredient order
    - Remove empty entries
    """

    def __init__(self):
        self.separator_pattern = re.compile(r"\s*,\s*")

    def parse(self, raw_inci: str) -> list[str]:

        if not isinstance(raw_inci, str):
            raise TypeError("INCI input must be a string.")

        raw_inci = raw_inci.strip()

        if not raw_inci:
            return []

        ingredients = self.separator_pattern.split(raw_inci)

        cleaned = []

        for ingredient in ingredients:

            ingredient = " ".join(
                ingredient.split()
            )

            if ingredient:
                cleaned.append(ingredient)

        return cleaned


class INCINormalizer:
    """
    Normalizes cosmetic ingredient strings
    without changing their scientific identity.
    """

    def normalize(self, ingredients: list[str]) -> list[str]:

        if not isinstance(ingredients, list):
            raise TypeError(
                "Ingredients must be provided as a list."
            )

        normalized = []

        for ingredient in ingredients:

            if not isinstance(ingredient, str):
                continue

            cleaned = " ".join(
                ingredient.strip().split()
            )

            if not cleaned:
                continue

            normalized.append(cleaned)

        return normalized
