from urllib.parse import urlparse

from app.models.company import Company


def normalize_company_name(name: str | None) -> str:
    if not name:
        return ""
    noise = [" ltd", " limited", " inc", " llc", " co.", " company", " corp", " corporation", " gmbh", " srl"]
    value = " ".join(name.lower().replace("&", "and").split())
    for suffix in noise:
        if value.endswith(suffix):
            value = value[: -len(suffix)]
    return value.strip(" .,")


def normalize_host(url: str | None) -> str:
    if not url:
        return ""
    value = url if "://" in url else f"https://{url}"
    host = urlparse(value).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def email_domain(email: str | None) -> str:
    if not email or "@" not in email:
        return ""
    return email.rsplit("@", 1)[-1].lower()


def is_duplicate(candidate: dict, existing: list[Company]) -> bool:
    candidate_host = normalize_host(candidate.get("website"))
    candidate_domain = email_domain(candidate.get("email"))
    candidate_name = normalize_company_name(candidate.get("name"))

    for company in existing:
        if candidate_host and candidate_host == normalize_host(company.website):
            return True
        if candidate_domain and candidate_domain == email_domain(company.email):
            return True
        if candidate_name and candidate_name == normalize_company_name(company.name):
            return True
    return False
