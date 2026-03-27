# Beginner Manual Part-3: One-day real test-run checklist (first live demo)

This plan helps you run your **first live demo in one day**.

---

## Morning (Setup + baseline checks)

## 09:00 - 09:30 → Environment setup
- Activate virtual environment.
- Verify `.env` values.
- Confirm PostgreSQL is running.

Checklist:
- [ ] Python environment active
- [ ] `DATABASE_URL` correct
- [ ] `OPENAI_API_KEY` set
- [ ] `JWT_SECRET` set

## 09:30 - 10:00 → DB migration
Run:
```bash
alembic upgrade head
```

Checklist:
- [ ] Migration succeeded
- [ ] Tables created (`exams`, `source_documents`, `source_chunks`, `generated_questions`)

## 10:00 - 10:30 → Service startup
Run:
```bash
uvicorn tet_engine.app.main:app --reload --port 8001
```

Checklist:
- [ ] `GET /health` returns OK
- [ ] Swagger opens at `/docs`

## 10:30 - 11:30 → Pre-demo smoke validation
Run:
```bash
python -m py_compile tet_engine/app/main.py tet_engine/app/models.py tet_engine/app/services.py tet_engine/app/phase2/db.py tet_engine/app/phase2/pdf_ingestion.py tet_engine/app/phase2/prompt_chain.py tet_engine/app/phase2/exam_catalog.py tet_engine/app/phase2/auth.py
pytest -q
```

Checklist:
- [ ] Compile check passed
- [ ] Tests passed

---

## Afternoon (API validation + content generation)

## 12:00 - 12:30 → Bootstrap + admin creation
- `POST /v2/hierarchy/bootstrap`
- `POST /v2/admin/users`
- `POST /v2/auth/login`

Checklist:
- [ ] Exam templates loaded
- [ ] Super admin created
- [ ] Login tokens received

## 12:30 - 13:30 → Source ingestion
- Upload at least 1 syllabus PDF and 1 content PDF.
- Verify source listing with `GET /v2/sources`.

Checklist:
- [ ] PDFs uploaded
- [ ] `chunks_saved > 0`
- [ ] Sources listed correctly

## 14:30 - 16:00 → Grounded generation + review
- Generate 20 questions from one topic.
- Review and approve sample questions.

Checklist:
- [ ] Questions generated
- [ ] Answer keys manually sampled
- [ ] No obvious duplicates
- [ ] Review endpoint updates status

## 16:00 - 17:00 → Publish + report validation
- Publish approved sample set.
- Verify generated report file exists.

Checklist:
- [ ] Publish endpoint success
- [ ] `report_path` returned
- [ ] Report file readable in `tet_engine_data/reports/`

---

## Evening (Demo build + presentation flow)

## 17:30 - 18:30 → Build demo storyline
Prepare 6 demo steps:
1. Health check
2. Admin login
3. Upload source PDF
4. Generate grounded questions
5. Review/approve
6. Publish and show report

Checklist:
- [ ] All curl/Postman requests saved
- [ ] Example outputs ready
- [ ] Backup PDF source ready

## 18:30 - 19:30 → Dry run
- Run full demo twice.
- Record timing and fix slow/error points.

Checklist:
- [ ] End-to-end run < 15 minutes
- [ ] No blocking errors
- [ ] Fallback plan prepared

## 19:30 - 20:00 → Demo readiness sign-off
Go/No-go conditions:
- [ ] API stable for 30+ minutes
- [ ] At least 1 successful publish report
- [ ] Team can reproduce flow from docs

---

## Optional “Plan B” if API key/model fails
- Continue with fallback generation behavior.
- Demo ingestion, retrieval, review, and publishing workflow.
- Clearly mark model output as fallback sample.

---

## End-of-day deliverables
- Demo recording/video
- Postman collection or curl script
- One publish report file
- Issue list for Day-2 improvements
