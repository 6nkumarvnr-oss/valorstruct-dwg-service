# Software requirements and usage opinion

## A) Software requirements to build/run this engine

## 1) Core runtime
- Python 3.10+
- pip + virtualenv
- FastAPI + Uvicorn
- SQLAlchemy
- psycopg (PostgreSQL driver)
- pypdf
- OpenAI SDK

## 2) Database
- PostgreSQL 14+ (recommended)
- Optional: pgAdmin / DBeaver for inspection

## 3) Infra / deployment
- Linux VM or Docker host
- Nginx (optional reverse proxy)
- Process manager (systemd / supervisor / container orchestrator)
- Object storage (local path now, cloud bucket for production)

## 4) Security and secrets
- `.env` or secret manager for `OPENAI_API_KEY`, `DATABASE_URL`
- Role-based access for admin/reviewer
- HTTPS in production

## 5) Optional production add-ons
- Redis (job queue / caching)
- Celery or RQ for background ingestion/generation
- pgvector for semantic retrieval
- Monitoring: Prometheus + Grafana / OpenTelemetry
- Error tracking: Sentry

---

## B) Can this engine be used as a digital book printer/writer?

Short answer: **Yes, as an AI writing assistant pipeline** — but do it responsibly.

## Good use cases
- Drafting educational notes and study books
- Creating structured thesis outlines
- Summarizing literature reviews
- Creating question banks and practice explanations
- Drafting journal-ready structure templates

## High-risk areas (must control)
- Directly auto-writing full thesis/journal papers without human verification
- Plagiarism/copyright risk from source text reuse
- Fabricated citations or non-existent references
- Authorship ethics violations for academic publishing

## Recommended policy
- Human-in-the-loop editing is mandatory.
- Use plagiarism checks before release.
- Keep citation traceability for every generated section.
- Separate modes:
  1. `exam_mode` for MCQs and answer keys
  2. `author_mode` for books/thesis drafts with strict citation workflow

---

## C) My opinion for your product direction

Best approach for your app:
1. Keep this engine primary for exam question banks.
2. Add a separate "Author Studio" module for books/thesis/journal drafting.
3. Enforce review workflows and plagiarism/citation checks in Author Studio.
4. Never auto-publish academic content without expert review.

This gives you scale, safety, and legal clarity.
