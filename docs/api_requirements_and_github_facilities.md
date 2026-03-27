# Engine verification: required APIs and GitHub facilities

This document verifies the current codebase and lists the APIs/facilities required for an exam-focused question bank engine.

## 1) Current codebase verification (what exists)

### API service modules
- FastAPI entrypoint: `tet_engine/app/main.py`
- API schemas: `tet_engine/app/models.py`
- Service orchestration: `tet_engine/app/services.py`
- DB models: `tet_engine/app/phase2/db.py`
- PDF ingestion: `tet_engine/app/phase2/pdf_ingestion.py`
- LLM chain: `tet_engine/app/phase2/prompt_chain.py`
- Exam catalog: `tet_engine/app/phase2/exam_catalog.py`

### Core capabilities already present
- Exam hierarchy CRUD endpoints
- PDF upload + chunking
- Grounded question generation endpoint
- Admin user endpoints
- Publish endpoint with text report output

## 2) Required APIs (minimum production set)

## A. Auth & admin APIs
1. `POST /v2/admin/users`
2. `GET /v2/admin/users`
3. `POST /v2/auth/login`
4. `POST /v2/auth/refresh`

## B. Exam hierarchy APIs
1. `POST /v1/exams`
2. `POST /v1/courses`
3. `POST /v1/papers`
4. `POST /v1/subjects`
5. `POST /v1/topics`
6. `POST /v2/hierarchy/bootstrap`

## C. Content source APIs
1. `POST /v1/sources` (manual text)
2. `POST /v2/sources/pdf`
3. `GET /v2/catalog/exams`
4. `GET /v2/sources`
5. `DELETE /v2/sources/{id}`

## D. Generation & review APIs
1. `POST /v1/questions/generate` (template fallback)
2. `POST /v2/questions/generate-grounded`
3. `POST /v1/questions/validate`
4. `POST /v1/questions/review`
5. `GET /v1/questions`

## E. Publish/report APIs
1. `POST /v2/publish/report`
2. `GET /v2/publish/reports` *(recommended next)*
3. `GET /v2/publish/reports/{filename}` *(recommended next)*

## F. Student delivery APIs (recommended next)
1. `GET /v2/tests/topic/{topic_id}`
2. `POST /v2/tests/submit`
3. `GET /v2/analytics/weak-topics/{student_id}`

## 3) GitHub facilities you should enable

## Repository setup
- README + architecture docs
- LICENSE
- CODEOWNERS
- CONTRIBUTING.md
- SECURITY.md

## Quality gates
- Branch protection rules
- Required PR reviews
- Required status checks
- Signed commits (optional but recommended)

## CI/CD via GitHub Actions
- Lint + format checks
- Unit tests + integration tests
- Build container image
- Deploy to staging/production

## Project management
- Issues templates (bug/feature)
- PR template
- Labels + milestones
- GitHub Projects board for roadmap

## Security/compliance
- Dependabot alerts + updates
- Code scanning (CodeQL)
- Secret scanning
- Environments with protected deployment approvals

## Release management
- Semantic version tags
- Release notes per version
- Changelog automation

## 4) Recommended immediate next tasks in this repo
1. Add auth endpoints and JWT middleware.
2. Add source-list and report-download endpoints.
3. Add automated test suite and GitHub Actions workflow.
4. Add branch protection + CODEOWNERS.
5. Add analytics endpoints for weak-topic targeting.
