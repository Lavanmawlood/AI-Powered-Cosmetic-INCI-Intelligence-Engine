import sys
from pathlib import Path

PROJECT_ROOT = Path("/content/drive/MyDrive/lav-lab")
sys.path.insert(0, "/content")  # local copy fixes Drive import issues

import pytest
from app.ai.formula_engine import FormulaEngine
from app.ai.skin_consultant import SkinConsultant
from app.ai.skin_knowledge import SKIN_CONCERNS, get_concern_list, get_concern_ingredients, get_concern_explanation

DATA_PATH = PROJECT_ROOT / "data" / "processed" / "products_clean.json"


@pytest.fixture(scope="module")
def engine():
    return FormulaEngine(data_path=DATA_PATH)


@pytest.fixture(scope="module")
def consultant():
    return SkinConsultant(data_path=DATA_PATH)


# ------------------------------------------------------------------
# FormulaEngine tests
# ------------------------------------------------------------------
def test_engine_loads_products(engine):
    assert len(engine.products) > 0


def test_find_similar_returns_results(engine):
    first_product = engine.products[0]
    slug = first_product["url"].split("/")[-1]
    result = engine.find_similar(slug, top_n=5)
    assert "similar_products" in result
    assert len(result["similar_products"]) <= 5


def test_find_similar_excludes_self(engine):
    first_product = engine.products[0]
    slug = first_product["url"].split("/")[-1]
    result = engine.find_similar(slug, top_n=5)
    names = [p["name"] for p in result["similar_products"]]
    assert first_product["name"] not in names


def test_find_similar_unknown_slug_returns_error(engine):
    result = engine.find_similar("nonexistent-slug-12345", top_n=5)
    assert "error" in result


def test_check_conflicts_returns_valid_structure(engine):
    first_product = engine.products[0]
    slug = first_product["url"].split("/")[-1]
    result = engine.check_conflicts(slug)
    assert "conflicts_found" in result
    assert "conflicts" in result
    assert "disclaimer" in result


def test_conflict_rules_are_bidirectional_safe(engine):
    # Every conflict rule pair should have exactly 2 distinct ingredients
    for rule in engine.CONFLICT_RULES:
        assert len(rule["pair"]) == 2
        assert rule["pair"][0] != rule["pair"][1]
        assert "reason" in rule


# ------------------------------------------------------------------
# Skin Knowledge Base tests
# ------------------------------------------------------------------
def test_all_concerns_have_bilingual_labels():
    for key, data in SKIN_CONCERNS.items():
        assert "label_en" in data
        assert "label_ckb" in data
        assert len(data["label_en"]) > 0
        assert len(data["label_ckb"]) > 0


def test_all_concerns_have_ingredients():
    for key, data in SKIN_CONCERNS.items():
        assert len(data["key_ingredients"]) > 0


def test_get_concern_list_returns_all_concerns():
    en_list = get_concern_list("en")
    assert len(en_list) == len(SKIN_CONCERNS)


def test_get_concern_ingredients_unknown_key_returns_empty():
    result = get_concern_ingredients("nonexistent_concern")
    assert result == []


# ------------------------------------------------------------------
# SkinConsultant tests
# ------------------------------------------------------------------
def test_consultant_finds_products_for_known_concern(consultant):
    result = consultant.find_products_for_concern("acne", lang="en", top_n=10)
    assert result["total_matches"] > 0
    assert len(result["matching_products"]) <= 10


def test_consultant_unknown_concern_returns_error(consultant):
    result = consultant.find_products_for_concern("nonexistent_concern", lang="en")
    assert "error" in result


def test_consultant_suggest_formula_has_no_duplicate_ingredients(consultant):
    formula = consultant.suggest_formula("dryness", lang="en")
    ingredients = formula["proposed_formula"]
    assert len(ingredients) == len(set(ingredients))


def test_consultant_suggest_formula_includes_safety_check(consultant):
    formula = consultant.suggest_formula("acne", lang="en")
    assert "safety_check" in formula
    assert "conflicts_found" in formula["safety_check"]


def test_consultant_suggest_formula_all_concerns():
    consultant_local = SkinConsultant(data_path=DATA_PATH)
    for concern_key in SKIN_CONCERNS.keys():
        formula = consultant_local.suggest_formula(concern_key, lang="en")
        assert "error" not in formula
        assert len(formula["proposed_formula"]) > 0
