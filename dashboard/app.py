import streamlit as st
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path("/content/drive/MyDrive/lav-lab")
sys.path.insert(0, str(PROJECT_ROOT))

from app.ai.formula_engine import FormulaEngine

st.set_page_config(page_title="LAV LAB", page_icon="🧪", layout="wide")

DATA_PATH = PROJECT_ROOT / "data" / "processed" / "products_clean.json"


@st.cache_resource
def load_engine():
    return FormulaEngine(data_path=DATA_PATH)


@st.cache_data
def load_products():
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


engine = load_engine()
products = load_products()

st.title("🧪 LAV LAB")
st.caption("AI-Powered Cosmetic & INCI Intelligence Engine")

tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔍 Similar Products", "⚠️ Conflict Checker"])

# ------------------------------------------------------------------
# TAB 1: OVERVIEW
# ------------------------------------------------------------------
with tab1:
    col1, col2, col3 = st.columns(3)
    total_ingredients = sum(p.get("ingredient_count", 0) for p in products)
    col1.metric("Total Products", len(products))
    col2.metric("Total Ingredient Mentions", total_ingredients)
    col3.metric("Avg Ingredients / Product", round(total_ingredients / len(products), 1))

    st.subheader("All Products")
    search = st.text_input("Search by product name", "")
    filtered = [p for p in products if search.lower() in p.get("name", "").lower()] if search else products
    st.dataframe(
        [{"Name": p.get("name"), "Ingredients": p.get("ingredient_count"), "URL": p.get("url")} for p in filtered],
        use_container_width=True,
        height=400,
    )

# ------------------------------------------------------------------
# TAB 2: SIMILARITY ENGINE
# ------------------------------------------------------------------
with tab2:
    st.subheader("Find Ingredient-Similar Products")
    names = [p.get("name") for p in products]
    selected_name = st.selectbox("Choose a product", names)

    if selected_name:
        selected_product = next(p for p in products if p.get("name") == selected_name)
        slug = selected_product["url"].split("/")[-1]

        top_n = st.slider("Number of similar products", 3, 10, 5)
        result = engine.find_similar(slug, top_n=top_n)

        st.write(f"**Ingredients ({selected_product.get('ingredient_count')}):**")
        st.write(", ".join(ing.get("inci_name", "") for ing in selected_product.get("ingredients", [])))

        st.divider()
        st.write("**Most similar products:**")
        for item in result.get("similar_products", []):
            st.write(f"- **{item['name']}** — similarity: `{item['similarity_score']}`")
            st.caption(item["url"])

# ------------------------------------------------------------------
# TAB 3: CONFLICT CHECKER
# ------------------------------------------------------------------
with tab3:
    st.subheader("Check for Known Ingredient Conflicts")
    names2 = [p.get("name") for p in products]
    selected_name2 = st.selectbox("Choose a product to check", names2, key="conflict_select")

    if selected_name2:
        selected_product2 = next(p for p in products if p.get("name") == selected_name2)
        slug2 = selected_product2["url"].split("/")[-1]

        result2 = engine.check_conflicts(slug2)

        if result2.get("conflicts_found", 0) > 0:
            st.error(f"⚠️ {result2['conflicts_found']} potential conflict(s) found")
            for c in result2["conflicts"]:
                st.write(f"- **{c['ingredients'][0]} + {c['ingredients'][1]}**")
                st.caption(c["reason"])
        else:
            st.success("✅ No known conflicts detected")

        st.info(result2.get("disclaimer", ""))

st.divider()
st.caption("Built with FastAPI + scikit-learn + Streamlit | Educational/portfolio project")
