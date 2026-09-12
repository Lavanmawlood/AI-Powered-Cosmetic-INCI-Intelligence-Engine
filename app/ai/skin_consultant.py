import json
import sys
from pathlib import Path

PROJECT_ROOT = Path("/content/drive/MyDrive/lav-lab")
sys.path.insert(0, str(PROJECT_ROOT))

from app.ai.skin_knowledge import SKIN_CONCERNS, get_concern_ingredients, get_concern_explanation
from app.ai.formula_engine import FormulaEngine

DATA_PATH = PROJECT_ROOT / "data" / "processed" / "products_clean.json"


class SkinConsultant:
    def __init__(self, data_path=DATA_PATH):
        self.products = json.loads(Path(data_path).read_text(encoding="utf-8"))
        self.formula_engine = FormulaEngine(data_path=data_path)

    def _product_ingredient_names(self, product):
        return {ing.get("inci_name", "") for ing in product.get("ingredients", [])}

    def find_products_for_concern(self, concern_key, lang="en", top_n=10):
        target_ingredients = set(get_concern_ingredients(concern_key))
        if not target_ingredients:
            return {"error": f"Unknown concern: {concern_key}"}

        matches = []
        for p in self.products:
            product_ings = self._product_ingredient_names(p)
            overlap = target_ingredients & product_ings
            if overlap:
                matches.append({
                    "name": p.get("name"),
                    "url": p.get("url"),
                    "matched_ingredients": sorted(overlap),
                    "match_count": len(overlap),
                })

        # Sort by match count, then diversify by shuffling ties deterministically by name
        matches.sort(key=lambda x: (-x["match_count"], x["name"]))

        return {
            "concern": concern_key,
            "explanation": get_concern_explanation(concern_key, lang),
            "recommended_ingredients": sorted(target_ingredients),
            "matching_products": matches[:top_n],
            "total_matches": len(matches),
        }

    def suggest_formula(self, concern_key, lang="en"):
        target_ingredients = get_concern_ingredients(concern_key)
        if not target_ingredients:
            return {"error": f"Unknown concern: {concern_key}"}

        base_ingredients = ["Water", "Glycerin"]
        supporting_ingredients = ["Phenoxyethanol"]

        # Pick actives, skipping anything already in the base/support lists
        actives = [ing for ing in target_ingredients if ing not in base_ingredients + supporting_ingredients][:3]

        # Deduplicate while preserving order
        seen = set()
        proposed_formula = []
        for ing in base_ingredients + actives + supporting_ingredients:
            if ing not in seen:
                seen.add(ing)
                proposed_formula.append(ing)

        conflicts_found = []
        rules = self.formula_engine.CONFLICT_RULES
        ingredient_set = set(proposed_formula)
        for rule in rules:
            a, b = rule["pair"]
            if a in ingredient_set and b in ingredient_set:
                conflicts_found.append({"ingredients": [a, b], "reason": rule["reason"]})

        return {
            "concern": concern_key,
            "explanation": get_concern_explanation(concern_key, lang),
            "proposed_formula": proposed_formula,
            "structure": {
                "base_solvent_humectant": base_ingredients,
                "active_ingredients": actives,
                "preservative": supporting_ingredients,
            },
            "safety_check": {
                "conflicts_found": len(conflicts_found),
                "conflicts": conflicts_found,
            },
            "disclaimer": (
                "This is an educational formulation suggestion based on commonly used "
                "cosmetic ingredient categories. It is NOT a tested, stability-verified, "
                "or dermatologically approved formula. Professional cosmetic chemists "
                "and stability/safety testing are required before any real-world use."
            ),
        }


if __name__ == "__main__":
    consultant = SkinConsultant()

    print("=== Products for 'acne' ===")
    result = consultant.find_products_for_concern("acne", lang="en", top_n=5)
    print(f"Total matches: {result['total_matches']}")
    for p in result["matching_products"]:
        print(f"  - {p['name']} (matched: {p['matched_ingredients']})")

    print("\n=== Suggested formula for 'dryness' ===")
    formula = consultant.suggest_formula("dryness", lang="en")
    print(json.dumps(formula, indent=2, ensure_ascii=False))
