# ============================================================
# LAV LAB — SKIN CONCERN KNOWLEDGE BASE (Bilingual: EN / CKB)
# ============================================================

SKIN_CONCERNS = {
    "acne": {
        "label_en": "Acne / Breakouts",
        "label_ckb": "دومەڵ / کیستە",
        "key_ingredients": [
            "Salicylic Acid", "Niacinamide", "Benzoyl Peroxide",
            "Zinc PCA", "Tea Tree Oil", "Sulfur",
        ],
        "explanation_en": "These ingredients help unclog pores, reduce excess oil, and calm inflammation associated with acne.",
        "explanation_ckb": "ئەم پێکهاتانە یارمەتی کردنەوەی خزنی پۆر، کەمکردنەوەی چەوری زیادە، و هێمنکردنەوەی هەوکردنی پێست دەدەن کە پەیوەستن بە دومەڵەوە.",
    },
    "dryness": {
        "label_en": "Dryness / Dehydration",
        "label_ckb": "وشکبوونی پێست",
        "key_ingredients": [
            "Hyaluronic Acid", "Glycerin", "Ceramides",
            "Squalane", "Panthenol", "Shea Butter",
        ],
        "explanation_en": "These ingredients attract and lock in moisture, restoring the skin's natural barrier.",
        "explanation_ckb": "ئەم پێکهاتانە شێ ڕادەکێشن و پاراستنی دەکەن لەناو پێستدا، بۆ گەڕاندنەوەی بەربەستی سروشتی پێست.",
    },
    "aging": {
        "label_en": "Aging / Fine Lines",
        "label_ckb": "پیربوون / هێڵی ورد",
        "key_ingredients": [
            "Retinol", "Peptides", "Vitamin C", "Ascorbic Acid",
            "Niacinamide", "Collagen", "Coenzyme Q10",
        ],
        "explanation_en": "These ingredients stimulate collagen production and protect against oxidative stress that accelerates visible aging.",
        "explanation_ckb": "ئەم پێکهاتانە هاندانی بەرهەمهێنانی کۆلاجین دەکەن و پاراستن لە زیانی ئۆکسیدەیشن کە کاریگەری هەیە لەسەر دەرکەوتنی نیشانەکانی پیربوون.",
    },
    "hyperpigmentation": {
        "label_en": "Dark Spots / Hyperpigmentation",
        "label_ckb": "لەکەی تاریک / گۆڕانی ڕەنگی پێست",
        "key_ingredients": [
            "Vitamin C", "Niacinamide", "Alpha Arbutin",
            "Kojic Acid", "Azelaic Acid", "Tranexamic Acid",
        ],
        "explanation_en": "These ingredients inhibit melanin production and help fade existing dark spots over time.",
        "explanation_ckb": "ئەم پێکهاتانە بەرهەمهێنانی مێلانین کەم دەکەنەوە و یارمەتی کەمبوونەوەی لەکەی تاریک دەدەن بە درێژایی کات.",
    },
    "sensitivity": {
        "label_en": "Sensitivity / Redness",
        "label_ckb": "هەستیاری / سووربوونەوە",
        "key_ingredients": [
            "Centella Asiatica", "Bisabolol", "Panthenol",
            "Allantoin", "Oat Extract", "Madecassoside",
        ],
        "explanation_en": "These ingredients are known for their soothing, anti-inflammatory properties that calm irritated skin.",
        "explanation_ckb": "ئەم پێکهاتانە بە تایبەتمەندی هێمنکردنەوە و دژە-هەوکردن ناسراون کە پێستی هەستیار ئارام دەکەنەوە.",
    },
    "oiliness": {
        "label_en": "Oily Skin / Excess Sebum",
        "label_ckb": "چەوری زیادەی پێست",
        "key_ingredients": [
            "Niacinamide", "Salicylic Acid", "Zinc PCA",
            "Clay", "Witch Hazel",
        ],
        "explanation_en": "These ingredients help regulate oil production and minimize the appearance of pores.",
        "explanation_ckb": "ئەم پێکهاتانە یارمەتی ڕێکخستنی بەرهەمهێنانی چەوری دەدەن و گەورەیی پۆرەکان کەم دەکەنەوە.",
    },
}


def get_concern_list(lang="en"):
    """Return a list of (key, label) pairs for UI dropdowns."""
    label_field = "label_ckb" if lang == "ckb" else "label_en"
    return [(key, data[label_field]) for key, data in SKIN_CONCERNS.items()]


def get_concern_ingredients(concern_key):
    """Return the ingredient list for a given concern key."""
    concern = SKIN_CONCERNS.get(concern_key)
    if not concern:
        return []
    return concern["key_ingredients"]


def get_concern_explanation(concern_key, lang="en"):
    concern = SKIN_CONCERNS.get(concern_key)
    if not concern:
        return ""
    field = "explanation_ckb" if lang == "ckb" else "explanation_en"
    return concern.get(field, "")


if __name__ == "__main__":
    print("Available concerns (EN):")
    for key, label in get_concern_list("en"):
        print(f"  {key}: {label}")

    print("\nAvailable concerns (CKB):")
    for key, label in get_concern_list("ckb"):
        print(f"  {key}: {label}")

    print("\nExample — acne ingredients:")
    print(get_concern_ingredients("acne"))
