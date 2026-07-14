from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    seed_keywords: list[str] = Field(min_length=1)


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None


class ProjectOut(OrmModel):
    id: int
    name: str
    description: str | None
    seed_keywords: str
    status: str
    created_at: datetime
    updated_at: datetime


class KeywordOut(OrmModel):
    id: int
    project_id: int
    text: str
    category: str
    confidence: float
    source_type: str
    source_url: str | None


class SourceOut(OrmModel):
    id: int
    project_id: int
    source_type: str
    title: str
    url: str
    event_name: str | None
    publication_year: int | None
    access_status: str
    notes: str | None


class CompanyUpdate(BaseModel):
    name: str | None = None
    website: str | None = None
    country: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    status: str | None = None
    notes: str | None = None


class CompanyOut(OrmModel):
    id: int
    project_id: int
    name: str
    website: str | None
    country: str | None
    address: str | None
    phone: str | None
    email: str | None
    status: str
    confidence: float
    source_type: str | None
    source_title: str | None
    source_url: str | None
    event_name: str | None
    notes: str | None


class ResearchTaskOut(OrmModel):
    id: int
    project_id: int
    queue_job_id: str | None
    status: str
    log: str | None
    keywords_created: int
    sources_created: int
    companies_created: int
    error: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class ProjectDetail(ProjectOut):
    keywords: list[KeywordOut] = []
    sources: list[SourceOut] = []
    companies: list[CompanyOut] = []
    tasks: list[ResearchTaskOut] = []
