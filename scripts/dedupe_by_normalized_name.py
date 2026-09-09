import json
import re
from pathlib import Path

PROJECT_ROOT = Path("/content/drive/MyDrive/lav-lab")
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "products_clean.json"


def normalize_name(name):
    """Normalize a product name for duplicate detection:
    lowercase, unify & / and, strip punctuation and extra spaces."""
    name = name.lower()
    name = name.replace("&", "and")
    name = re.sub(r"[^a-z0-9\s]", "", name)   # strip punctuation
    name = re.sub(r"\s+", " ", name).strip()   # collapse spaces
    return name


def main():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    print(f"Before dedup: {len(data)} products")

    seen = {}
    duplicates_found = []

    for p in data:
        key = normalize_name(p.get("name", ""))
        if key in seen:
            duplicates_found.append((p.get("name"), seen[key].get("name")))
            # Keep the one with more ingredients (likely more complete)
            existing = seen[key]
            if len(p.get("ingredients", [])) > len(existing.get("ingredients", [])):
                seen[key] = p
        else:
            seen[key] = p

    if duplicates_found:
        print(f"\nFound {len(duplicates_found)} duplicate(s):")
        for dup_name, kept_name in duplicates_found:
            print(f"  '{dup_name}'  ==  '{kept_name}'")
    else:
        print("\nNo duplicates found.")

    clean_data = list(seen.values())
    print(f"\nAfter dedup: {len(clean_data)} products")

    DATA_PATH.write_text(
        json.dumps(clean_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Saved to: {DATA_PATH}")


if __name__ == "__main__":
    main()
