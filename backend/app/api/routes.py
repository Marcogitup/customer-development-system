import csv
from io import BytesIO, StringIO

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from redis import Redis
from rq import Queue
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.core.database import get_db
from app.models.company import Company
from app.models.keyword import Keyword
from app.models.project import Project
from app.models.research_task import ResearchTask
from app.models.source import Source
from app.schemas.common import (
    CompanyOut,
    CompanyUpdate,
    KeywordOut,
    ProjectCreate,
    ProjectDetail,
    ProjectOut,
    ProjectUpdate,
    ResearchTaskOut,
    SourceOut,
)
from app.services.research import run_research_task

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/projects", response_model=ProjectOut)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> Project:
    project = Project(
        name=payload.name,
        description=payload.description,
        seed_keywords=", ".join(payload.seed_keywords),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)) -> list[Project]:
    return db.query(Project).order_by(Project.created_at.desc()).all()


@router.get("/projects/{project_id}", response_model=ProjectDetail)
def get_project(project_id: int, db: Session = Depends(get_db)) -> Project:
    project = (
        db.query(Project)
        .options(
            selectinload(Project.keywords),
            selectinload(Project.sources),
            selectinload(Project.companies),
            selectinload(Project.tasks),
        )
        .filter(Project.id == project_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/projects/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)) -> Project:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


@router.post("/projects/{project_id}/research-tasks", response_model=ResearchTaskOut)
def create_research_task(project_id: int, db: Session = Depends(get_db)) -> ResearchTask:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    task = ResearchTask(project_id=project_id, status="queued")
    db.add(task)
    db.commit()
    db.refresh(task)

    settings = get_settings()
    queue = Queue("research", connection=Redis.from_url(settings.redis_url))
    job = queue.enqueue(run_research_task, task.id, job_timeout=900)
    task.queue_job_id = job.id
    db.commit()
    db.refresh(task)
    return task


@router.post("/projects/{project_id}/research-tasks/run-now", response_model=ResearchTaskOut)
def run_research_now(project_id: int, db: Session = Depends(get_db)) -> ResearchTask:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    task = ResearchTask(project_id=project_id, status="queued")
    db.add(task)
    db.commit()
    db.refresh(task)
    run_research_task(task.id)
    db.refresh(task)
    return task


@router.get("/projects/{project_id}/keywords", response_model=list[KeywordOut])
def list_keywords(project_id: int, db: Session = Depends(get_db)) -> list[Keyword]:
    return db.query(Keyword).filter(Keyword.project_id == project_id).order_by(Keyword.confidence.desc()).all()


@router.get("/projects/{project_id}/sources", response_model=list[SourceOut])
def list_sources(project_id: int, db: Session = Depends(get_db)) -> list[Source]:
    return db.query(Source).filter(Source.project_id == project_id).order_by(Source.created_at.desc()).all()


@router.get("/projects/{project_id}/companies", response_model=list[CompanyOut])
def list_companies(
    project_id: int,
    q: str | None = None,
    status: str | None = None,
    source_type: str | None = None,
    db: Session = Depends(get_db),
) -> list[Company]:
    query = db.query(Company).filter(Company.project_id == project_id)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Company.name.ilike(like), Company.website.ilike(like), Company.country.ilike(like)))
    if status:
        query = query.filter(Company.status == status)
    if source_type:
        query = query.filter(Company.source_type == source_type)
    return query.order_by(Company.created_at.desc()).all()


@router.patch("/companies/{company_id}", response_model=CompanyOut)
def update_company(company_id: int, payload: CompanyUpdate, db: Session = Depends(get_db)) -> Company:
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    db.commit()
    db.refresh(company)
    return company


def company_rows(project_id: int, db: Session) -> list[Company]:
    return db.query(Company).filter(Company.project_id == project_id).order_by(Company.name.asc()).all()


@router.get("/projects/{project_id}/exports/companies.csv")
def export_companies_csv(project_id: int, db: Session = Depends(get_db)) -> StreamingResponse:
    output = StringIO()
    writer = csv.writer(output)
    headers = ["Company Name", "Website", "Country", "Address", "Phone", "Email", "Status", "Source Type", "Source Title", "Source URL", "Event"]
    writer.writerow(headers)
    for company in company_rows(project_id, db):
        writer.writerow([
            company.name,
            company.website,
            company.country,
            company.address,
            company.phone,
            company.email,
            company.status,
            company.source_type,
            company.source_title,
            company.source_url,
            company.event_name,
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=project-{project_id}-companies.csv"},
    )


@router.get("/projects/{project_id}/exports/companies.xlsx")
def export_companies_xlsx(project_id: int, db: Session = Depends(get_db)) -> StreamingResponse:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Companies"
    sheet.append(["Company Name", "Website", "Country", "Address", "Phone", "Email", "Status", "Source Type", "Source Title", "Source URL", "Event"])
    for company in company_rows(project_id, db):
        sheet.append([
            company.name,
            company.website,
            company.country,
            company.address,
            company.phone,
            company.email,
            company.status,
            company.source_type,
            company.source_title,
            company.source_url,
            company.event_name,
        ])
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=project-{project_id}-companies.xlsx"},
    )
