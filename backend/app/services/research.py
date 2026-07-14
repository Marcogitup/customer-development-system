from datetime import datetime
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.company import Company
from app.models.keyword import Keyword
from app.models.project import Project
from app.models.research_task import ResearchTask
from app.models.source import Source
from app.services.dedup import is_duplicate
from app.services.keyword_expander import expand_keywords
from app.services.search_provider import SearchResult, get_search_provider


def parse_seed_keywords(seed_keywords: str) -> list[str]:
    return [item.strip() for item in seed_keywords.replace("\n", ",").split(",") if item.strip()]


def classify_source(result: SearchResult) -> str:
    value = f"{result.title} {result.url} {result.snippet}".lower()
    if "issuu.com" in value:
        return "issuu"
    if any(word in value for word in ["exhibitor", "expo", "trade show", "exhibition", "fair"]):
        return "trade_show"
    if any(word in value for word in ["magazine", "buyer guide", "directory", "vendor guide"]):
        return "magazine_directory"
    if "linkedin.com/company" in value:
        return "linkedin_search_snippet"
    return "web"


def infer_year(text: str) -> int | None:
    for year in range(datetime.utcnow().year + 1, datetime.utcnow().year - 6, -1):
        if str(year) in text:
            return year
    return None


def company_from_result(project_id: int, result: SearchResult, source_type: str) -> dict | None:
    if source_type not in {"trade_show", "magazine_directory", "issuu"}:
        return None
    host = urlparse(result.url).netloc.replace("www.", "")
    name_seed = result.title.split("|")[0].replace("Exhibitor Directory", "").replace("Buyer Guide", "").strip()
    if not name_seed:
        name_seed = host or "Unknown company"
    return {
        "project_id": project_id,
        "name": name_seed[:300],
        "website": f"https://{host}" if host else result.url,
        "country": None,
        "address": None,
        "phone": None,
        "email": None,
        "status": "new",
        "confidence": 0.58,
        "source_type": source_type,
        "source_title": result.title,
        "source_url": result.url,
        "event_name": result.title if source_type == "trade_show" else None,
        "notes": result.snippet,
    }


def run_research_task(task_id: int) -> None:
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        run_research_task_with_session(db, task_id)
    finally:
        db.close()


def run_research_task_with_session(db: Session, task_id: int) -> ResearchTask:
    settings = get_settings()
    task = db.get(ResearchTask, task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")
    project = db.get(Project, task.project_id)
    if not project:
        raise ValueError(f"Project {task.project_id} not found")

    task.status = "running"
    task.started_at = datetime.utcnow()
    task.log = "Research started\n"
    db.commit()

    try:
        provider = get_search_provider(settings.search_provider)
        seeds = parse_seed_keywords(project.seed_keywords)
        all_results: list[SearchResult] = []
        query_templates = [
            "{keyword} products categories applications about us",
            "{keyword} trade show exhibitors exhibitor list",
            "{keyword} expo exhibitor directory 2026",
            "{keyword} magazine directory buyer guide suppliers",
            "{keyword} site:issuu.com supplier directory",
            "{keyword} linkedin company description supplier",
        ]
        for seed in seeds:
            for template in query_templates:
                query = template.format(keyword=seed)
                all_results.extend(provider.search(query, limit=4))

        keywords_created = 0
        for item in expand_keywords(seeds, all_results):
            exists = (
                db.query(Keyword)
                .filter(Keyword.project_id == project.id, Keyword.text == item["text"], Keyword.category == item["category"])
                .first()
            )
            if not exists:
                db.add(Keyword(project_id=project.id, **item))
                keywords_created += 1

        sources_created = 0
        companies_created = 0
        existing_companies = list(db.query(Company).filter(Company.project_id == project.id).all())
        seen_urls: set[str] = {url for (url,) in db.query(Source.url).filter(Source.project_id == project.id).all()}

        for result in all_results:
            source_type = classify_source(result)
            if result.url not in seen_urls:
                db.add(
                    Source(
                        project_id=project.id,
                        source_type=source_type,
                        title=result.title,
                        url=result.url,
                        event_name=result.title if source_type == "trade_show" else None,
                        publication_year=infer_year(f"{result.title} {result.snippet}"),
                        access_status="discovered",
                        notes=result.snippet,
                    )
                )
                sources_created += 1
                seen_urls.add(result.url)

            company_candidate = company_from_result(project.id, result, source_type)
            if company_candidate and not is_duplicate(company_candidate, existing_companies):
                company = Company(**company_candidate)
                db.add(company)
                db.flush()
                existing_companies.append(company)
                companies_created += 1

        task.status = "succeeded"
        task.finished_at = datetime.utcnow()
        task.keywords_created = keywords_created
        task.sources_created = sources_created
        task.companies_created = companies_created
        task.log = (task.log or "") + (
            f"Created {keywords_created} keywords, {sources_created} sources, "
            f"{companies_created} companies.\n"
        )
        db.commit()
        db.refresh(task)
        return task
    except Exception as exc:
        task.status = "failed"
        task.error = str(exc)
        task.finished_at = datetime.utcnow()
        task.log = (task.log or "") + f"Failed: {exc}\n"
        db.commit()
        raise
