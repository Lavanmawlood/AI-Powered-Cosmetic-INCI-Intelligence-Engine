# LAV LAB
## AI-Powered Cosmetic & INCI Intelligence Engine

LAV LAB is a production-oriented data and AI platform for cosmetic
ingredient intelligence, INCI analysis, formula screening, and
evidence-aware cosmetic formulation recommendations.

## Project Vision

The goal of LAV LAB is to build a structured intelligence system that
can transform cosmetic product and ingredient data into useful,
auditable insights.

## Core Architecture

1. Scraper & Normalizer
2. Database
3. INCI Knowledge Engine
4. Formula Recommendation Engine
5. AI Layer
6. Streamlit Dashboard

## 🧠 Formula Engine & AI Layer

This is the intelligence core of LAV LAB — a data-driven system built
on the 146 cleaned products in the dataset. It combines classical
machine learning (TF-IDF + cosine similarity) with a rule-based
knowledge layer, exposed through a live FastAPI backend.

### 1. Ingredient Similarity Engine
Each product's ingredient list is vectorized with **TF-IDF**
(Term Frequency–Inverse Document Frequency), treating each product as
a "document" and each ingredient as a "term". Rare, distinctive
ingredients are weighted more heavily than common ones (e.g. Water,
Glycerin), so similarity is driven by what actually differentiates a
formula. **Cosine similarity** is then used to rank the most
ingredient-similar products to any given item.

Example — products most similar to *Aquaphor Baby Wash & Shampoo*:

| Product | Similarity |
|---|---|
| Cetaphil Daily Facial Cleanser Fragrance Free | 0.337 |
| Olay Gentle Foaming Face Wash (Birch Water) | 0.291 |
| Cetaphil Gentle Foaming Cleanser | 0.263 |
| Cetaphil Hydrating Cream-to-Foam Cleanser | 0.219 |
| Wellwell Gentle Face Wash | 0.171 |

### 2. Rule-Based Ingredient Conflict Checker
A curated set of commonly cited ingredient interactions
(e.g. Retinol + AHA/BHA, Vitamin C + Benzoyl Peroxide) is checked
against each product's ingredient list to flag potential formulation
conflicts.

> **Disclaimer:** This is general educational information based on
> commonly cited ingredient interactions in the skincare community —
> not professional, medical, or dermatological advice.

### 3. Live API Endpoints
| Endpoint | Description |
|---|---|
| `GET /products` | List all products (paginated) |
| `GET /products/{slug}` | Get full details for one product |
| `GET /products/{slug}/similar` | Top N most ingredient-similar products |
| `GET /products/{slug}/conflicts` | Check a product against known conflict rules |
| `GET /search?ingredient=X` | Find all products containing ingredient X |
| `GET /stats` | Dataset-wide statistics |

**Tech:** Python, scikit-learn (TfidfVectorizer, cosine_similarity), FastAPI

## Project Structure

```text
lav-lab/
├── app/
│   ├── api/
│   ├── core/
│   ├── database/
│   ├── scraper/
│   ├── normalization/
│   ├── knowledge/
│   ├── formulation/
│   ├── ai/
│   └── analytics/
├── dashboard/
├── data/
│   ├── raw/
│   ├── processed/
│   └── reference/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── api/
│   └── fixtures/
├── migrations/
├── scripts/
├── notebooks/
├── docs/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md

