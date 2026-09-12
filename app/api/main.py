import sys
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException

PROJECT_ROOT = Path("/content/drive/MyDrive/lav-lab")
sys.path.insert(0, str(PROJECT_ROOT))

from app.ai.formula_engine import FormulaEngine
from app.ai.skin_consultant import SkinConsultant
from app.ai.skin_knowledge import get_concern_list

DATA_PATH = PROJECT_ROOT / "data" / "processed" / "products_clean.json"

app = FastAPI(
    title="LAV LAB API",
    description="Cosmetic & INCI Intelligence Engine",
    version="1.1.0",
)

with open(DATA_PATH, encoding="utf-8") as f:
    PRODUCTS = json.load(f)

engine = FormulaEngine(data_path=DATA_PATH)
consultant = SkinConsultant(data_path=DATA_PATH)


def find_product_by_slug(slug: str):
    for p in PRODUCTS:
        if slug in p.get("url", "") or slug in p.get("source_url", ""):
            return p
    return None


@app.get("/")
def root():
    return {"message": "LAV LAB API is running", "total_products": len(PRODUCTS)}


@app.get("/products")
def list_products(limit: int = 20, offset: int = 0):
    return {
        "total": len(PRODUCTS),
        "limit": limit,
        "offset": offset,
        "products": [
            {"name": p.get("name"), "url": p.get("url"), "ingredient_count": p.get("ingredient_count")}
            for p in PRODUCTS[offset: offset + limit]
        ],
    }


@app.get("/products/{slug}")
def get_product(slug: str):
    product = find_product_by_slug(slug)
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product '{slug}' not found")
    return product


@app.get("/products/{slug}/similar")
def get_similar_products(slug: str, top_n: int = 5):
    product = find_product_by_slug(slug)
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product '{slug}' not found")
    return engine.find_similar(slug, top_n=top_n)


@app.get("/products/{slug}/conflicts")
def get_product_conflicts(slug: str):
    product = find_product_by_slug(slug)
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product '{slug}' not found")
    return engine.check_conflicts(slug)


@app.get("/search")
def search_by_ingredient(ingredient: str):
    matches = []
    for p in PRODUCTS:
        names = [ing.get("inci_name", "") for ing in p.get("ingredients", [])]
        if any(ingredient.lower() in n.lower() for n in names):
            matches.append({"name": p.get("name"), "url": p.get("url")})
    return {"query": ingredient, "match_count": len(matches), "matches": matches}


@app.get("/stats")
def get_stats():
    total_ingredients = sum(p.get("ingredient_count", 0) for p in PRODUCTS)
    return {
        "total_products": len(PRODUCTS),
        "total_ingredient_mentions": total_ingredients,
        "average_ingredients_per_product": round(total_ingredients / len(PRODUCTS), 1) if PRODUCTS else 0,
    }


# ------------------------------------------------------------------
# NEW: Virtual Skin Consultant endpoints
# ------------------------------------------------------------------
@app.get("/concerns")
def list_concerns(lang: str = "en"):
    """List all supported skin concerns in the requested language."""
    return {"concerns": [{"key": key, "label": label} for key, label in get_concern_list(lang)]}


@app.get("/consult")
def consult(concern: str, lang: str = "en", top_n: int = 10):
    """Given a skin concern, return matching products and an explanation."""
    result = consultant.find_products_for_concern(concern, lang=lang, top_n=top_n)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.get("/consult/formula")
def consult_formula(concern: str, lang: str = "en"):
    """Given a skin concern, suggest a new formula with a safety check."""
    result = consultant.suggest_formula(concern, lang=lang)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
