
import sys
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.normalization.inci_parser import (
    INCIParser,
    INCINormalizer
)


def test_parse_basic_inci():

    parser = INCIParser()

    raw = "Water, Glycerin, Niacinamide"

    result = parser.parse(raw)

    assert result == [
        "Water",
        "Glycerin",
        "Niacinamide"
    ]


def test_parse_extra_spaces():

    parser = INCIParser()

    raw = "Water,   Glycerin  ,  Niacinamide"

    result = parser.parse(raw)

    assert result == [
        "Water",
        "Glycerin",
        "Niacinamide"
    ]


def test_preserve_order():

    parser = INCIParser()

    raw = "Water, Glycerin, Panthenol"

    result = parser.parse(raw)

    assert result[0] == "Water"
    assert result[1] == "Glycerin"
    assert result[2] == "Panthenol"


def test_empty_inci():

    parser = INCIParser()

    assert parser.parse("") == []


def test_whitespace_only():

    parser = INCIParser()

    assert parser.parse("     ") == []


def test_invalid_input():

    parser = INCIParser()

    try:
        parser.parse(None)
        assert False
    except TypeError:
        assert True


def test_normalizer():

    normalizer = INCINormalizer()

    ingredients = [
        " Water ",
        "Glycerin  ",
        "  Niacinamide"
    ]

    result = normalizer.normalize(ingredients)

    assert result == [
        "Water",
        "Glycerin",
        "Niacinamide"
    ]


def test_normalizer_empty_values():

    normalizer = INCINormalizer()

    ingredients = [
        "Water",
        "",
        "   ",
        "Glycerin"
    ]

    result = normalizer.normalize(ingredients)

    assert result == [
        "Water",
        "Glycerin"
    ]
