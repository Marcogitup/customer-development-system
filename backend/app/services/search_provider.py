from dataclasses import dataclass


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    snippet: str


class SearchProvider:
    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        raise NotImplementedError


class DemoSearchProvider(SearchProvider):
    """Deterministic local search provider for demos and CI."""

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        normalized = query.lower()
        stem = query.split()[0].strip("\"'") if query.split() else "industry"
        results = [
            SearchResult(
                title=f"{stem.title()} Expo 2026 Exhibitor Directory",
                url=f"https://example.com/events/{stem.lower()}-expo-2026/exhibitors",
                snippet=f"Find exhibitors, suppliers, manufacturers and commercial partners for {query}.",
            ),
            SearchResult(
                title=f"International {stem.title()} Buyer Guide",
                url=f"https://example.com/guides/{stem.lower()}-buyer-guide",
                snippet=f"Directory of vendors, distributors, OEM suppliers, retail and commercial solution providers.",
            ),
            SearchResult(
                title=f"{stem.title()} Industry Magazine on Issuu",
                url=f"https://issuu.com/example/docs/{stem.lower()}_supplier_directory_2026",
                snippet=f"Supplier profiles, product categories, company websites, emails and phone contacts.",
            ),
            SearchResult(
                title=f"About leading {stem} manufacturers",
                url=f"https://example-manufacturer.com/about-us",
                snippet=f"We are a manufacturer of {stem}, accessories, replacement parts and commercial applications.",
            ),
        ]
        if "linkedin" in normalized:
            results.append(
                SearchResult(
                    title=f"{stem.title()} companies overview",
                    url="https://www.linkedin.com/company/example",
                    snippet="Search snippet only: supplier of commercial systems, retail solutions and custom manufacturing.",
                )
            )
        return results[:limit]


def get_search_provider(name: str) -> SearchProvider:
    return DemoSearchProvider()
