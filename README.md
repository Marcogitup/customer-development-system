# Customer Development System

An online B2B customer development platform for keyword expansion, trade show exhibitor discovery, magazine/directory research, lead management, deduplication, source tracking, and CSV/XLSX export.

## What It Does

- Starts from product, industry, or buyer-identity keywords.
- Expands keywords using related products, industry/application terms, search snippets, About Us style terms, and compliant LinkedIn-derived snippets or user imports.
- Finds trade show, expo, exhibition, and exhibitor directory sources.
- Finds magazine, directory, buyer guide, vendor guide, and Issuu sources.
- Stores company leads with website, country, address, phone, email, source, event, status, and notes.
- Supports manual editing, filtering, status tags, deduplication, and export.

## Compliance Notes

The crawler layer is designed to respect `robots.txt`, limit requests per domain, record blocked sources, and avoid bypassing CAPTCHA, paywalls, login walls, or other access controls. LinkedIn is not directly scraped. LinkedIn-like descriptions must come from search snippets, user imports, or approved data providers.

## Tech Stack

- Frontend: Next.js, React, TypeScript
- Backend: FastAPI, SQLAlchemy, Alembic
- Database: PostgreSQL
- Queue: Redis + RQ worker
- Deployment: Render Blueprint

## Repository Structure

```text
backend/      FastAPI API, models, migrations, worker
frontend/     Next.js dashboard
docs/         PRD and technical design
sample_data/  Example inputs and company rows
render.yaml   Render Blueprint
```

## Local Setup

1. Copy environment variables:

```bash
cp .env.example backend/.env
cp .env.example frontend/.env.local
```

2. Start PostgreSQL and Redis locally.

3. Run the backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

4. Run the worker:

```bash
cd backend
source .venv/bin/activate
python -m app.worker
```

5. Run the frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

For local testing without Redis worker, use the UI's `Run now` button. Production should use `Queue`.

## Render Deployment

1. Push this repository to GitHub.
2. In Render, choose **New +** then **Blueprint**.
3. Connect the GitHub repository.
4. Render reads `render.yaml` and creates:
   - PostgreSQL database
   - Redis instance
   - FastAPI API service
   - RQ worker service
   - Next.js frontend service
5. Update these values after creation:
   - `CRAWL_USER_AGENT` with a real contact email
   - `SEARCH_PROVIDER` when replacing the demo provider
   - `FRONTEND_ORIGIN` if Render does not resolve it correctly during first deploy
   - `NEXT_PUBLIC_API_BASE_URL` to the API service URL if needed

## Search Provider Integration

The MVP uses `DemoSearchProvider` so the full workflow works without paid APIs. To connect real search:

1. Add provider credentials to environment variables.
2. Implement a provider in `backend/app/services/search_provider.py`.
3. Return `SearchResult(title, url, snippet)` values.
4. Set `SEARCH_PROVIDER` to the new provider name.

Recommended providers include Bing Web Search, Brave Search, Google Programmable Search, SerpAPI, or a licensed internal dataset.

## API Highlights

- `POST /api/projects`
- `GET /api/projects`
- `GET /api/projects/{project_id}`
- `POST /api/projects/{project_id}/research-tasks`
- `POST /api/projects/{project_id}/research-tasks/run-now`
- `GET /api/projects/{project_id}/companies`
- `PATCH /api/companies/{company_id}`
- `GET /api/projects/{project_id}/exports/companies.csv`
- `GET /api/projects/{project_id}/exports/companies.xlsx`

## Documents

- [PRD](docs/PRD.md)
- [Technical Design](docs/TECHNICAL_DESIGN.md)
