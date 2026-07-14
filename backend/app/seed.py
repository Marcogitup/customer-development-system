from app.core.database import Base, SessionLocal, engine
from app.models.company import Company
from app.models.project import Project
from app.models.source import Source


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Project).first():
            return
        project = Project(
            name="LED Display Market Research",
            description="Sample project for testing keyword expansion and exhibitor discovery.",
            seed_keywords="LED display, retail signage, commercial integrator",
        )
        db.add(project)
        db.flush()
        db.add(
            Source(
                project_id=project.id,
                source_type="trade_show",
                title="Digital Signage Expo 2026 Exhibitor Directory",
                url="https://example.com/digital-signage-expo/exhibitors",
                event_name="Digital Signage Expo 2026",
                publication_year=2026,
                access_status="sample",
                notes="Sample source.",
            )
        )
        db.add(
            Company(
                project_id=project.id,
                name="BrightView Display Systems",
                website="https://brightview.example",
                country="United States",
                address="100 Market Street, Chicago, IL",
                phone="+1 312 555 0100",
                email="sales@brightview.example",
                status="new",
                confidence=0.82,
                source_type="trade_show",
                source_title="Digital Signage Expo 2026 Exhibitor Directory",
                source_url="https://example.com/digital-signage-expo/exhibitors",
                event_name="Digital Signage Expo 2026",
            )
        )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
