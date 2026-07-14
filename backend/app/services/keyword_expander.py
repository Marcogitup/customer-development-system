import re
from collections import Counter

from app.services.search_provider import SearchResult


STOPWORDS = {
    "and",
    "for",
    "with",
    "the",
    "from",
    "this",
    "that",
    "find",
    "company",
    "companies",
    "supplier",
    "suppliers",
    "manufacturer",
    "manufacturers",
}

INDUSTRY_TERMS = [
    "retail",
    "commercial",
    "hospitality",
    "industrial",
    "education",
    "healthcare",
    "distribution",
    "oem",
    "wholesale",
]

RELATED_PATTERNS = [
    "{seed} accessories",
    "{seed} parts",
    "{seed} systems",
    "{seed} solutions",
    "{seed} supplier",
    "{seed} manufacturer",
    "{seed} distributor",
]


def tokenize(text: str) -> list[str]:
    return [word for word in re.findall(r"[a-zA-Z][a-zA-Z0-9-]{2,}", text.lower()) if word not in STOPWORDS]


def expand_keywords(seed_keywords: list[str], search_results: list[SearchResult]) -> list[dict]:
    expanded: list[dict] = []
    seen: set[str] = set()

    def add(text: str, category: str, confidence: float, source_type: str, source_url: str | None = None) -> None:
        clean = " ".join(text.lower().split())
        if len(clean) < 3 or clean in seen:
            return
        seen.add(clean)
        expanded.append(
            {
                "text": clean,
                "category": category,
                "confidence": confidence,
                "source_type": source_type,
                "source_url": source_url,
            }
        )

    for seed in seed_keywords:
        add(seed, "seed", 1.0, "user")
        for pattern in RELATED_PATTERNS:
            add(pattern.format(seed=seed), "related_product", 0.72, "system")
        for term in INDUSTRY_TERMS:
            add(f"{term} {seed}", "industry_application", 0.66, "system")

    counter: Counter[str] = Counter()
    source_by_word: dict[str, str] = {}
    for result in search_results:
        for token in tokenize(f"{result.title} {result.snippet}"):
            counter[token] += 1
            source_by_word.setdefault(token, result.url)

    for token, count in counter.most_common(30):
        category = "about_us_definition" if token in {"custom", "commercial", "solutions"} else "search_common_term"
        add(token, category, min(0.9, 0.45 + count * 0.08), "search_snippet", source_by_word.get(token))

    return expanded
