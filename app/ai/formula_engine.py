import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_ROOT = Path("/content/drive/MyDrive/lav-lab")
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "products_clean.json"


class FormulaEngine:
    CONFLICT_RULES = [
        {"pair": ("Retinol", "Glycolic Acid"),
         "reason": "Layering retinol with AHAs can increase skin irritation and sensitivity."},
        {"pair": ("Retinol", "Salicylic Acid"),
         "reason": "Combining retinol with BHA may over-exfoliate and irritate the skin barrier."},
        {"pair": ("Ascorbic Acid", "Niacinamide"),
         "reason": "Historically thought to reduce efficacy when combined, though modern formulations mostly resolve this. Still commonly flagged."},
        {"pair": ("Benzoyl Peroxide", "Ascorbic Acid"),
         "reason": "Benzoyl peroxide can oxidize and destabilize Vitamin C, reducing its effectiveness."},
        {"pair": ("Retinol", "Benzoyl Peroxide"),
         "reason": "Benzoyl peroxide can degrade retinol, reducing its potency."},
    ]

    def __init__(self, data_path=DATA_PATH):
        self.products = self._load_products(data_path)
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = None
        self._build_index()

    def _load_products(self, path):
        if not path.exists():
            raise FileNotFoundError(f"Could not find {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        return data

    def _ingredient_text(self, product):
        names = [ing.get("inci_name", "").replace(" ", "_") for ing in product.get("ingredients", [])]
        return " ".join(names)

    def _build_index(self):
        corpus = [self._ingredient_text(p) for p in self.products]
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def find_similar(self, slug, top_n=5):
        idx = None
        for i, p in enumerate(self.products):
            if slug in p.get("url", "") or slug in p.get("source_url", ""):
                idx = i
                break
        if idx is None:
            return {"error": "Product with slug " + slug + " not found."}

        sims = cosine_similarity(self.tfidf_matrix[idx], self.tfidf_matrix).flatten()
        ranked = sorted([(i, score) for i, score in enumerate(sims) if i != idx],
                         key=lambda x: x[1], reverse=True)[:top_n]

        results = []
        for i, score in ranked:
            results.append({
                "name": self.products[i].get("name"),
                "url": self.products[i].get("url"),
                "similarity_score": round(float(score), 4),
            })

        return {"source_product": self.products[idx].get("name"), "similar_products": results}

    def check_conflicts(self, slug):
        product = None
        for p in self.products:
            if slug in p.get("url", "") or slug in p.get("source_url", ""):
                product = p
                break
        if product is None:
            return {"error": "Product with slug " + slug + " not found."}

        ingredient_names = set(ing.get("inci_name", "") for ing in product.get("ingredients", []))
        conflicts_found = []
        for rule in self.CONFLICT_RULES:
            a, b = rule["pair"]
            if a in ingredient_names and b in ingredient_names:
                conflicts_found.append({"ingredients": [a, b], "reason": rule["reason"]})

        return {
            "product": product.get("name"),
            "conflicts_found": len(conflicts_found),
            "conflicts": conflicts_found,
            "disclaimer": "This is general educational information based on commonly cited ingredient interactions, not professional or medical skincare advice.",
        }


if __name__ == "__main__":
    engine = FormulaEngine()
    print("Loaded " + str(len(engine.products)) + " products into engine.")
