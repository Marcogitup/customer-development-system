"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-14
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("seed_keywords", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_projects_id"), "projects", ["id"], unique=False)
    op.create_index(op.f("ix_projects_status"), "projects", ["status"], unique=False)

    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("website", sa.String(length=1200), nullable=True),
        sa.Column("country", sa.String(length=120), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("phone", sa.String(length=120), nullable=True),
        sa.Column("email", sa.String(length=240), nullable=True),
        sa.Column("status", sa.String(length=60), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("source_type", sa.String(length=80), nullable=True),
        sa.Column("source_title", sa.String(length=500), nullable=True),
        sa.Column("source_url", sa.String(length=1200), nullable=True),
        sa.Column("event_name", sa.String(length=300), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_companies_email"), "companies", ["email"], unique=False)
    op.create_index(op.f("ix_companies_id"), "companies", ["id"], unique=False)
    op.create_index(op.f("ix_companies_name"), "companies", ["name"], unique=False)
    op.create_index(op.f("ix_companies_project_id"), "companies", ["project_id"], unique=False)
    op.create_index(op.f("ix_companies_status"), "companies", ["status"], unique=False)
    op.create_index(op.f("ix_companies_website"), "companies", ["website"], unique=False)

    op.create_table(
        "keywords",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.String(length=240), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("source_type", sa.String(length=80), nullable=False),
        sa.Column("source_url", sa.String(length=1200), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_keywords_project_id"), "keywords", ["project_id"], unique=False)
    op.create_index(op.f("ix_keywords_text"), "keywords", ["text"], unique=False)

    op.create_table(
        "research_tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("queue_job_id", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("log", sa.Text(), nullable=True),
        sa.Column("keywords_created", sa.Integer(), nullable=False),
        sa.Column("sources_created", sa.Integer(), nullable=False),
        sa.Column("companies_created", sa.Integer(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_research_tasks_id"), "research_tasks", ["id"], unique=False)
    op.create_index(op.f("ix_research_tasks_project_id"), "research_tasks", ["project_id"], unique=False)
    op.create_index(op.f("ix_research_tasks_queue_job_id"), "research_tasks", ["queue_job_id"], unique=False)
    op.create_index(op.f("ix_research_tasks_status"), "research_tasks", ["status"], unique=False)

    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("url", sa.String(length=1200), nullable=False),
        sa.Column("event_name", sa.String(length=300), nullable=True),
        sa.Column("publication_year", sa.Integer(), nullable=True),
        sa.Column("access_status", sa.String(length=80), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sources_id"), "sources", ["id"], unique=False)
    op.create_index(op.f("ix_sources_project_id"), "sources", ["project_id"], unique=False)
    op.create_index(op.f("ix_sources_source_type"), "sources", ["source_type"], unique=False)
    op.create_index(op.f("ix_sources_url"), "sources", ["url"], unique=False)


def downgrade() -> None:
    op.drop_table("sources")
    op.drop_table("research_tasks")
    op.drop_table("keywords")
    op.drop_table("companies")
    op.drop_table("projects")
