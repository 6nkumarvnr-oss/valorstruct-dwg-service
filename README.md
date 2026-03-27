# valorstruct-dwg-service

This repository contains a TET/CTET-ready exam engine in `tet_engine/app`.

## Phase-2 delivered in this update
- PostgreSQL schema + ORM models.
- Alembic migrations for versioned DB changes.
- PDF ingestion and text chunking.
- Grounded MCQ prompt chain (OpenAI Responses API).
- New API endpoints for exam catalog, PDF ingestion, grounded generation, and JWT auth login/refresh.
- Alembic migration scaffolding and pytest smoke tests.

## Architecture (exam-first, course-expandable)
- Exam → Course → Paper → Subject → Topic.
- Source documents (PDF/books/notes) are chunked and stored.
- Retrieval selects grounded chunks for the requested topic.
- LLM generates MCQs using only retrieved chunks.
- Questions are stored for admin review and publishing.

## Files added for Phase-2
- `tet_engine/app/phase2/schema.sql` (PostgreSQL DDL)
- `tet_engine/app/phase2/db.py` (SQLAlchemy models/session/init)
- `tet_engine/app/phase2/pdf_ingestion.py` (PDF extraction/chunking/retrieval)
- `tet_engine/app/phase2/prompt_chain.py` (grounded LLM prompt chain)
- `tet_engine/app/phase2/exam_catalog.py` (official multi-exam source registry)
- `docs/exam_content_collection.md` (collection SOP + answer key policy)

## API endpoints
### Existing (v1)
- `POST /v1/exams`
- `POST /v1/courses`
- `POST /v1/papers`
- `POST /v1/subjects`
- `POST /v1/topics`
- `POST /v1/sources`
- `POST /v1/questions/generate` (template fallback flow)

### New (v2)
- `GET /v2/catalog/exams` (TNTET, TNPSC, GATE, NCEES FE/PE, PMP source registry)
- `POST /v2/admin/users` (create Admin/Super Admin/Reviewer)
- `GET /v2/admin/users` (list admins)
- `POST /v2/auth/login` (admin login token)
- `POST /v2/auth/refresh` (refresh token)
- `POST /v2/hierarchy/bootstrap` (seed PMP, TNTET, NCEES FE/PE, GATE, TNPSC)
- `GET /v2/sources` (list manual + PDF sources)
- `DELETE /v2/sources/{source_id}` (delete source)
- `POST /v2/sources/pdf` (multipart upload)
- `POST /v2/questions/generate-grounded` (retrieval + LLM grounded generation)
- `POST /v2/publish/report` (publish and generate notepad/text report)

---


## Migration commands
```bash
alembic upgrade head
```

To create a new migration:
```bash
alembic revision --autogenerate -m "describe change"
```

## Run tests
```bash
pytest
```

## Hands-on tutorial (VS Code)

### 1) Setup
```bash
cd /workspace/valorstruct-dwg-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) PostgreSQL setup (local)
```bash
export DATABASE_URL='postgresql+psycopg://postgres:postgres@localhost:5432/tet_engine'
```

Optional manual schema apply:
```bash
psql postgresql://postgres:postgres@localhost:5432/tet_engine -f tet_engine/app/phase2/schema.sql
```

`init_db()` also auto-creates tables on app startup.

### 3) OpenAI setup
```bash
export OPENAI_API_KEY='your_key_here'
export OPENAI_MODEL='gpt-4.1-mini'
```

If API key is missing, the system returns a safe fallback sample question.

### 4) Run service
```bash
uvicorn tet_engine.app.main:app --reload --port 8001
```

Swagger docs:
- http://127.0.0.1:8001/docs

---

## End-to-end flow

### A. Create exam
```bash
curl -X POST http://127.0.0.1:8001/v1/exams \
  -H "Content-Type: application/json" \
  -d '{"code":"TET","name":"Teacher Eligibility Test"}'
```

### B. List supported exam-source catalog
```bash
curl http://127.0.0.1:8001/v2/catalog/exams
```

### C. Upload PDF source (Phase-2)
```bash
curl -X POST http://127.0.0.1:8001/v2/sources/pdf \
  -F exam_code=TET \
  -F source_name='TET CDP Book' \
  -F source_type=book \
  -F file=@/absolute/path/to/tet_cdp.pdf
```

### D. Generate grounded MCQs (Phase-2)
```bash
curl -X POST http://127.0.0.1:8001/v2/questions/generate-grounded \
  -H "Content-Type: application/json" \
  -d '{
    "exam_code":"TET",
    "paper_name":"Paper 1",
    "subject_name":"Child Development and Pedagogy",
    "topic_name":"Learning and Pedagogical Issues",
    "count":5,
    "difficulty":"medium",
    "language":"en",
    "top_k_chunks":5
  }'
```

---



### E. Bootstrap exam hierarchy templates
```bash
curl -X POST http://127.0.0.1:8001/v2/hierarchy/bootstrap
```

### F. Create Admin / Super Admin / Reviewer
```bash
curl -X POST http://127.0.0.1:8001/v2/admin/users \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@yourapp.com","name":"Main Admin","role":"super_admin","password":"strongpass123"}'
```

### G. Publish approved questions + notepad report
```bash
curl -X POST http://127.0.0.1:8001/v2/publish/report \
  -H "Content-Type: application/json" \
  -d '{
    "exam_code":"TNTET",
    "paper_name":"Paper 1",
    "subject_name":"Child Development and Pedagogy",
    "topic_name":"Learning and Pedagogical Issues",
    "question_ids":["<q_id_1>","<q_id_2>"],
    "reviewer":"superadmin@yourapp.com"
  }'
```
This generates a text report under `tet_engine_data/reports/`.

## Best way for your existing 44-domain exam app
1. Keep this engine as a separate backend service.
2. Use Admin/Super Admin roles for approval control.
3. Use bootstrap hierarchy for PMP/TNTET/NCEES/GATE/TNPSC first.
4. Force publish only through `publish/report` to keep auditable records.
5. Store report files per batch for compliance and rollback.
6. Add student analytics feedback loop to trigger new generation batches.

## Quick complete guide
- `docs/step_by_step_setup.md` (full build/run/procedure + ownership/credits notes)
- `docs/software_requirements_and_use_cases.md` (software stack + book/thesis/journal usage policy)
- `docs/api_requirements_and_github_facilities.md` (API checklist + GitHub features to enable)
- `docs/vscode_quickstart.md` (run in VS Code on your own system)
- `docs/missing_requirements_and_improvements.md` (gap analysis + prioritized improvements)
- `docs/similar_engine_evaluation_framework.md` (benchmark framework to compare with similar engines)
- `docs/github_and_platform_recommendations.md` (GitHub checks + live deployment platform plan)
- `docs/beginner_step_by_step_manual.md` (beginner-friendly complete procedure)
- `docs/beginner_manual_part2_api_examples.md` (copy/paste API calls with expected output)
- `docs/beginner_manual_part3_one_day_demo_plan.md` (one-day real test-run checklist for first demo)

## How to operate the Question Bank Engine (daily runbook)

1. **Check exam catalog** using `GET /v2/catalog/exams`.
2. **Create hierarchy** (`exam -> course -> paper -> subject -> topic`) using v1 endpoints.
3. **Upload syllabus/books/PYQ PDFs** via `POST /v2/sources/pdf`.
4. **Generate grounded MCQs** via `POST /v2/questions/generate-grounded`.
5. **Review draft questions** in admin panel (must validate key/explanation).
6. **Approve/reject** question sets.
7. **Publish approved sets** to student app test bank.
8. **Track weak topics** from analytics and generate additional targeted sets.

## UI mandatory requirements

See the full checklist here:
- `docs/ui_mandatory_requirements.md`

This file defines the minimum modules for:
- admin + reviewer roles,
- ingestion/generation/review/publish workflow,
- answer-key quality gates,
- student practice screens,
- operational monitoring.

## Production next steps
- Replace keyword retrieval with vector DB (`pgvector`) + embeddings.
- Add answer-key verifier and duplicate detector.
- Add admin review dashboard + publish workflow.
- Add bilingual generation templates (EN + HI).
- Add student analytics and weak-topic adaptive generation.


## GitHub facilities enabled in this repo
- `CODEOWNERS`: `.github/CODEOWNERS`
- Contribution guide: `CONTRIBUTING.md`
- Security policy: `SECURITY.md`
- PR template: `.github/pull_request_template.md`
- Issue templates: `.github/ISSUE_TEMPLATE/*`
- CI workflow: `.github/workflows/ci.yml`
- CodeQL workflow: `.github/workflows/codeql.yml`
- Dependabot config: `.github/dependabot.yml`
- Release policy: `RELEASE.md`
- Changelog: `CHANGELOG.md`
