# ============================================================
# LAV LAB — FULL REBUILD PIPELINE
# Discover -> Sample -> Scrape -> Normalize -> Dedup
# ============================================================

import json
import re
import time
import random
from pathlib import Path
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

PROJECT_ROOT = Path("/content/drive/MyDrive/lav-lab")
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

URLS_PATH = RAW_DIR / "product_urls.txt"
PRODUCTS_PATH = PROCESSED_DIR / "products.json"
CLEAN_PATH = PROCESSED_DIR / "products_clean.json"

ALLOWED_DOMAINS = ["inkeedecoder.com", "incidecoder.com"]
BASE_URL = "https://inkeedecoder.com"
HEADERS = {"User-Agent": "LAVLabBot/1.0 (Educational portfolio project; contact: student project)"}

BRANDS = [
    "cerave", "the-ordinary", "la-roche-posay", "cetaphil",
    "paulas-choice", "vanicream", "wellwell", "aquaphor",
    "the-inkey-list", "neutrogena", "olay", "eucerin",
]

TARGET_SAMPLE = 150
MAX_PER_BRAND_PAGES = 30  # safety cap on pagination


# ------------------------------------------------------------------
# STEP 1: Robots.txt check
# ------------------------------------------------------------------
def can_fetch(url: str) -> bool:
    rp = RobotFileParser()
    rp.set_url(urljoin(BASE_URL, "/robots.txt"))
    try:
        rp.read()
        return rp.can_fetch(HEADERS["User-Agent"], url)
    except Exception:
        return True  # if robots.txt unreadable, proceed cautiously


# ------------------------------------------------------------------
# STEP 2: Discover product URLs from brand listing pages
# ------------------------------------------------------------------
def discover_urls():
    print("=" * 60)
    print("STEP 1/5: Discovering product URLs by brand")
    print("=" * 60)

    all_urls = set()
    for brand in BRANDS:
        brand_urls = set()
        offset = 0
        for page in range(MAX_PER_BRAND_PAGES):
            url = f"{BASE_URL}/brands/{brand}"
            if offset > 0:
                url += f"?offset={offset}"

            if not can_fetch(url):
                break

            try:
                resp = requests.get(url, headers=HEADERS, timeout=10)
                if resp.status_code == 404:
                    break
                resp.raise_for_status()
            except Exception:
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.find_all("a", href=re.compile(r"/products/"))
            found_this_page = set()
            for link in links:
                href = link.get("href", "")
                full_url = urljoin(BASE_URL, href)
                found_this_page.add(full_url)

            if not found_this_page or found_this_page.issubset(brand_urls):
                break

            brand_urls.update(found_this_page)
            offset += 1
            time.sleep(1.0)

        print(f"  {brand}: {len(brand_urls)} URLs")
        all_urls.update(brand_urls)

    print(f"\nTotal discovered: {len(all_urls)} URLs")
    URLS_PATH.write_text("\n".join(sorted(all_urls)), encoding="utf-8")
    return list(all_urls)


# ------------------------------------------------------------------
# STEP 3: Sample down to a brand-diverse subset
# ------------------------------------------------------------------
def sample_urls(all_urls, target=TARGET_SAMPLE):
    print("\n" + "=" * 60)
    print("STEP 2/5: Sampling URLs")
    print("=" * 60)

    by_brand = {}
    for url in all_urls:
        slug = url.rstrip("/").split("/")[-1]
        guess = slug.split("-")[0]
        by_brand.setdefault(guess, []).append(url)

    random.seed(42)
    for group in by_brand.values():
        random.shuffle(group)

    sampled = []
    idx = 0
    groups = list(by_brand.values())
    while len(sampled) < target and any(idx < len(g) for g in groups):
        for g in groups:
            if idx < len(g):
                sampled.append(g[idx])
            if len(sampled) >= target:
                break
        idx += 1

    print(f"Sampled {len(sampled)} URLs from {len(by_brand)} brand groups")
    URLS_PATH.write_text("\n".join(sorted(sampled)), encoding="utf-8")
    return sampled


# ------------------------------------------------------------------
# STEP 4: Scrape products (with incremental save, retry, dedup by slug)
# ------------------------------------------------------------------
def normalize_url(url: str) -> str:
    return url.rstrip("/")


def get_slug(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def fetch_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 404:
                return None, "404"
            resp.raise_for_status()
            return resp, None
        except requests.exceptions.HTTPError as e:
            if resp.status_code >= 500:
                time.sleep(2 ** attempt)
                continue
            return None, str(e)
        except Exception as e:
            time.sleep(2 ** attempt)
            if attempt == max_retries - 1:
                return None, str(e)
    return None, "max_retries_exceeded"


def parse_product(url, html):
    soup = BeautifulSoup(html, "html.parser")

    name_tag = soup.find("h1")
    name = name_tag.get_text(strip=True) if name_tag else url.split("/")[-1]

    ingredients = []
    seen_names = set()
    # Primary ingredient list (first occurrence block, avoids repeated sections)
    ingredient_links = soup.select(".ingred-link") or soup.select(".ingredient-list .ingredient-name")
    for tag in ingredient_links:
        ing_name = tag.get_text(strip=True)
        if ing_name and ing_name not in seen_names:
            seen_names.add(ing_name)
            ingredients.append({"inci_name": ing_name, "raw_name": ing_name})

    return {
        "name": name,
        "url": url,
        "ingredients": ingredients,
        "ingredient_count": len(ingredients),
        "source_url": url,
        "final_url": url,
        "scraped_at": time.time(),
    }


def collect_products():
    print("\n" + "=" * 60)
    print("STEP 3/5: Scraping products")
    print("=" * 60)

    urls = [u.strip() for u in URLS_PATH.read_text(encoding="utf-8").splitlines() if u.strip()]
    urls = [u for u in urls if any(d in u for d in ALLOWED_DOMAINS)]
    print(f"Loaded {len(urls)} URLs")

    existing = []
    if PRODUCTS_PATH.exists():
        try:
            existing = json.loads(PRODUCTS_PATH.read_text(encoding="utf-8"))
        except Exception:
            existing = []

    done_slugs = {get_slug(p["url"]) for p in existing}
    remaining = [u for u in urls if get_slug(u) not in done_slugs]
    print(f"{len(existing)} already collected, {len(remaining)} remaining")

    products = existing[:]
    for i, url in enumerate(remaining, 1):
        if not can_fetch(url):
            print(f"  [{i}/{len(remaining)}] skipped (robots.txt): {url}")
            continue

        resp, err = fetch_with_retry(url)
        if resp is None:
            print(f"  [{i}/{len(remaining)}] FAILED ({err}): {url}")
            time.sleep(1.5)
            continue

        product = parse_product(url, resp.text)
        products.append(product)
        print(f"  [{i}/{len(remaining)}] OK: {product['name']}")

        if len(products) % 10 == 0:
            PRODUCTS_PATH.write_text(json.dumps(products, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"    -- saved checkpoint ({len(products)} products) --")

        time.sleep(1.5 + random.random())

    PRODUCTS_PATH.write_text(json.dumps(products, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDone. {len(products)} total products saved to {PRODUCTS_PATH}")
    return products


# ------------------------------------------------------------------
# STEP 5: Normalize + dedup by URL slug (within-product duplicate ingredients)
# ------------------------------------------------------------------
SYNONYMS = {
    "aqua": "water",
    "water (aqua)": "water",
    "tocopheryl acetate": "tocopherol acetate",
}


def normalize_ingredient_name(name):
    key = name.strip().lower()
    return SYNONYMS.get(key, name.strip())


def normalize_products(products):
    print("\n" + "=" * 60)
    print("STEP 4/5: Normalizing ingredients")
    print("=" * 60)

    cleaned = []
    for p in products:
        seen = set()
        clean_ingredients = []
        for ing in p.get("ingredients", []):
            norm_name = normalize_ingredient_name(ing.get("inci_name", ""))
            if norm_name and norm_name not in seen:
                seen.add(norm_name)
                clean_ingredients.append({"inci_name": norm_name, "raw_name": ing.get("raw_name", norm_name)})
        p2 = dict(p)
        p2["ingredients"] = clean_ingredients
        p2["ingredient_count"] = len(clean_ingredients)
        cleaned.append(p2)

    print(f"Normalized {len(cleaned)} products")
    return cleaned


# ------------------------------------------------------------------
# STEP 6: Dedup across products by normalized product name
# ------------------------------------------------------------------
def normalize_product_name(name):
    name = name.lower()
    name = name.replace("&", "and")
    name = re.sub(r"[^a-z0-9\s]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def dedup_products(products):
    print("\n" + "=" * 60)
    print("STEP 5/5: Deduplicating by normalized name")
    print("=" * 60)

    seen = {}
    for p in products:
        key = normalize_product_name(p.get("name", ""))
        if key in seen:
            existing = seen[key]
            if len(p.get("ingredients", [])) > len(existing.get("ingredients", [])):
                seen[key] = p
        else:
            seen[key] = p

    final = list(seen.values())
    print(f"Before: {len(products)}  ->  After: {len(final)}")
    return final


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
def main():
    all_urls = discover_urls()
    sampled = sample_urls(all_urls, target=TARGET_SAMPLE)
    products = collect_products()
    normalized = normalize_products(products)
    final = dedup_products(normalized)

    CLEAN_PATH.write_text(json.dumps(final, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n{'=' * 60}")
    print(f"PIPELINE COMPLETE: {len(final)} clean products saved to {CLEAN_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
