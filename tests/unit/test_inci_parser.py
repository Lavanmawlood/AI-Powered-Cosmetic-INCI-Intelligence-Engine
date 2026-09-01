
import sys
from pathlib import Path

# Make project root importable
PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.normalization.inci_parser import INCIParser
from app.normalization.inci_parser import INCINormalizer


def test_parse_basic_inci():

    parser = INCIParser()

    raw = "Water, Glycerin, Niacinamide"

    result = parser.parse(raw)

    assert result == [
        "Water",
        "Glycerin",
        "Niacinamide"
    ]


def test_parse_removes_extra_spaces():

    parser = INCIParser()

    raw = "Water,   Glycerin  ,  Niacinamide"

    result = parser.parse(raw)

    assert result == [
        "Water",
        "Glycerin",
        "Niacinamide"
    ]


def test_parse_preserves_order():

    parser = INCIParser()

    raw = "Water, Glycerin, Panthenol"

    result = parser.parse(raw)

    assert result[0] == "Water"
    assert result[1] == "Glycerin"
    assert result[2] == "Panthenol"


def test_empty_inci_returns_empty_list():

    parser = INCIParser()

    result = parser.parse("")

    assert result == []


def test_whitespace_only_returns_empty_list():

    parser = INCIParser()

    result = parser.parse("     ")

    assert result == []


def test_invalid_input_raises_error():

    parser = INCIParser()

    try:
        parser.parse(None)
        assert False, "Expected TypeError"
    except TypeError:
        assert True


def test_normalizer_removes_extra_whitespace():

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


def test_normalizer_ignores_empty_values():

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
