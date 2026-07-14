# Customer Development System PRD

## 1. Product Goal

Build an online customer development platform that starts from one or more product, industry, or buyer-identity keywords and turns them into a traceable lead research workflow.

The system helps users:

- Expand initial keywords into product categories, related products, industry/application terms, buyer identity terms, company self-description terms, and search-derived terms.
- Discover relevant trade shows and capture the most recent available exhibitor lists.
- Discover magazines, directories, buyer guides, and Issuu publications with seller/company information.
- Normalize, deduplicate, edit, tag, search, and export company leads with source evidence.

## 2. Target Users

- B2B export sales teams
- Sourcing and market research teams
- Founder-led sales teams validating international market demand
- Agencies performing lead research for clients

## 3. Core Workflow

1. User creates a research project.
2. User enters seed keywords, such as:
   - Product term: `LED display`
   - Industry term: `retail signage`
   - Customer identity term: `commercial integrator`
3. System creates an async research task.
4. Task expands keywords from configured sources:
   - Search result titles and snippets
   - Public customer website product/category pages
   - About Us self-description wording
   - Common related products and applications inferred from search content
   - LinkedIn-style company descriptions only from compliant sources: search snippets, user import, or allowed third-party datasets
5. System searches for relevant trade shows and exhibitor lists.
6. System extracts exhibitor company data where available:
   - Company name
   - Website
   - Country
   - Address
   - Phone
   - Email
   - Source event
   - Source URL
7. System searches for relevant magazine, directory, buyer guide, and Issuu sources.
8. System stores seller/company information and links to original sources.
9. User reviews results, edits records, assigns status tags, filters, searches, deduplicates, and exports CSV/XLSX.

## 4. Functional Requirements

### 4.1 Project Management

- Create, list, view, update, and archive projects.
- Each project contains seed keywords, expanded keywords, discovered sources, companies, and tasks.

### 4.2 Keyword Expansion

The keyword expansion engine must support:

- Product category extraction from page titles, headings, navigation text, and snippets.
- Related product suggestions using co-occurring terms.
- Industry/application terms such as `retail`, `commercial`, `hospitality`, `industrial`, `education`, and `healthcare`.
- Company self-description terms from public About Us content.
- LinkedIn company description terms only when provided by:
  - Search engine snippets
  - User-uploaded/imported content
  - API/data providers with permission

Every generated keyword must keep:

- Keyword text
- Category
- Confidence score
- Source type
- Source URL or source note

### 4.3 Trade Show Discovery

The system must search for:

- `<keyword> trade show exhibitors`
- `<keyword> exhibition exhibitor list`
- `<keyword> expo exhibitor directory`
- `<industry> fair exhibitors`
- Recent year variants, prioritizing the most recent year available

The crawler should capture exhibitor list links when publicly accessible. If pages are blocked by login, CAPTCHA, paywall, or robots restrictions, the system must store the blocked status and source URL rather than bypassing controls.

### 4.4 Magazine / Directory / Buyer Guide / Issuu Discovery

The system must search for:

- Industry magazines
- Supplier directories
- Buyer guides
- Vendor guides
- Issuu publications

For Issuu and magazine sources, store:

- Source title
- Source type
- URL
- Publication year if detectable
- Recognized company/seller names
- Recognized website/email/phone if available

### 4.5 Company Lead Management

The system must support:

- Deduplication by normalized website, normalized company name, and email domain.
- Manual editing.
- Status tags:
  - `new`
  - `reviewing`
  - `qualified`
  - `contacted`
  - `not_fit`
  - `blocked_source`
- Search and filtering by keyword, country, source type, event, status, and confidence.
- Source traceability for every company.
- CSV and XLSX export.

### 4.6 Async Task Management

- Research runs as background jobs.
- Tasks expose status:
  - `queued`
  - `running`
  - `succeeded`
  - `failed`
  - `partial`
- Task logs are saved for user inspection.
- Failed network operations retry with exponential backoff.
- Each task records counts for keywords, sources, and companies created.

## 5. Compliance And Safety Requirements

- Respect `robots.txt`.
- Apply per-domain rate limits.
- Use clear user-agent identification.
- Do not bypass CAPTCHA, login walls, paywalls, or technical access controls.
- Do not directly scrape LinkedIn pages in violation of terms. Use search snippets, user imports, or approved data providers instead.
- Store source URLs and crawl decisions for auditability.
- Allow users to delete projects and related data.

## 6. Non-Functional Requirements

- Deployable to Render using:
  - Next.js frontend
  - FastAPI backend
  - PostgreSQL database
  - Redis-backed worker using RQ
- Environment variables documented in `.env.example`.
- Database migrations managed by Alembic.
- GitHub Actions run lint/build checks.
- README includes local setup and Render deployment.

## 7. MVP Scope

The generated repository implements a functional MVP with:

- API CRUD for projects, keywords, companies, sources, and tasks.
- Background research task scaffold with compliant crawler services.
- Deterministic demo search provider for local development.
- Optional real search provider interface for production integration.
- Frontend dashboard for project creation, task launch, review, editing, filtering, and export.
- CSV/XLSX export endpoints.
- Example seed data.

## 8. Future Enhancements

- Add authenticated search provider integrations.
- Add browser-based user-assisted scraping for pages requiring manual login.
- Add import pipelines for LinkedIn exports and trade show CSV/PDF files.
- Add AI-assisted keyword clustering and lead scoring.
- Add email outreach integration.
- Add multi-user accounts and role permissions.
