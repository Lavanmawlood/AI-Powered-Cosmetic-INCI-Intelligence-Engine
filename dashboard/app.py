import streamlit as st
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path("/content/drive/MyDrive/lav-lab")
sys.path.insert(0, str(PROJECT_ROOT))

from app.ai.formula_engine import FormulaEngine
from app.ai.skin_consultant import SkinConsultant
from app.ai.skin_knowledge import get_concern_list

st.set_page_config(page_title="LAV LAB", page_icon="🧪", layout="wide")

DATA_PATH = PROJECT_ROOT / "data" / "processed" / "products_clean.json"


@st.cache_resource
def load_engine():
    return FormulaEngine(data_path=DATA_PATH)


@st.cache_resource
def load_consultant():
    return SkinConsultant(data_path=DATA_PATH)


@st.cache_data
def load_products():
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


engine = load_engine()
consultant = load_consultant()
products = load_products()

# ------------------------------------------------------------------
# LANGUAGE TOGGLE
# ------------------------------------------------------------------
lang_choice = st.sidebar.radio("🌐 Language / زمان", ["English", "کوردی"])
lang = "en" if lang_choice == "English" else "ckb"

st.title("🧪 LAV LAB")
st.caption("AI-Powered Cosmetic & INCI Intelligence Engine")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview", "🔍 Similar Products", "⚠️ Conflict Checker", "🩺 Skin Consultant"
])

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
    selected_name = st.selectbox("Choose a product", names, key="sim_select")

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

# ------------------------------------------------------------------
# TAB 4: SKIN CONSULTANT (NEW)
# ------------------------------------------------------------------
with tab4:
    header = "🩺 Virtual Skin Consultant" if lang == "en" else "🩺 ڕاوێژکاری ڤیرچوالی پێست"
    st.subheader(header)

    concern_options = get_concern_list(lang)
    concern_labels = [label for key, label in concern_options]
    concern_keys = [key for key, label in concern_options]

    prompt = "What is your skin concern?" if lang == "en" else "نیگەرانیت لەسەر پێستت چییە؟"
    selected_label = st.selectbox(prompt, concern_labels, key="concern_select")
    selected_concern = concern_keys[concern_labels.index(selected_label)]

    sub_tab1, sub_tab2 = st.tabs([
        "🔍 Matching Products" if lang == "en" else "🔍 بەرهەمی گونجاو",
        "🧪 New Formula Suggestion" if lang == "en" else "🧪 پێشنیاری فۆرمیولای نوێ",
    ])

    with sub_tab1:
        result = consultant.find_products_for_concern(selected_concern, lang=lang, top_n=10)
        st.info(result["explanation"])

        ing_label = "Recommended ingredients:" if lang == "en" else "پێکهاتەی پێشنیارکراو:"
        st.write(f"**{ing_label}** {', '.join(result['recommended_ingredients'])}")

        st.divider()
        total_label = f"Found {result['total_matches']} matching product(s)" if lang == "en" \
            else f"{result['total_matches']} بەرهەمی گونجاو دۆزرایەوە"
        st.write(f"**{total_label}**")

        for p in result["matching_products"]:
            st.write(f"- **{p['name']}**")
            st.caption(f"{', '.join(p['matched_ingredients'])} | {p['url']}")

    with sub_tab2:
        formula = consultant.suggest_formula(selected_concern, lang=lang)
        st.info(formula["explanation"])

        st.write("**Proposed Formula:**" if lang == "en" else "**فۆرمیولای پێشنیارکراو:**")
        for category, ingredients in formula["structure"].items():
            label = category.replace("_", " ").title()
            st.write(f"- **{label}:** {', '.join(ingredients)}")

        st.divider()
        safety = formula["safety_check"]
        if safety["conflicts_found"] > 0:
            st.error(f"⚠️ {safety['conflicts_found']} conflict(s) found")
            for c in safety["conflicts"]:
                st.write(f"- **{c['ingredients'][0]} + {c['ingredients'][1]}**: {c['reason']}")
        else:
            safe_msg = "✅ No conflicts detected in this formula" if lang == "en" \
                else "✅ هیچ تێکەڵبوونی نائاسایی نەدۆزرایەوە لەم فۆرمیولایەدا"
            st.success(safe_msg)

        st.warning(formula["disclaimer"])

st.divider()
st.caption("Built with FastAPI + scikit-learn + Streamlit | Educational/portfolio project")
