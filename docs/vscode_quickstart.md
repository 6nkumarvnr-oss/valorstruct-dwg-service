# VS Code Quickstart: Run the Exam Engine on your system

## 1) Open project in VS Code
1. Open VS Code.
2. `File -> Open Folder...` and choose this repository.
3. Create a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

## 2) Configure environment
1. Copy `.env.example` to `.env`.
2. Update `DATABASE_URL` and `OPENAI_API_KEY`.

## 3) Install dependencies
- Run task: **Install dependencies** from `Terminal -> Run Task...`.
- Or run manually:
  ```bash
  pip install -r requirements.txt
  ```

## 4) Run DB migrations
```bash
alembic upgrade head
```

## 5) Validate code
- Run task: **Compile check**.
- Or run:
  ```bash
  python -m py_compile tet_engine/app/main.py tet_engine/app/models.py tet_engine/app/services.py tet_engine/app/phase2/db.py tet_engine/app/phase2/pdf_ingestion.py tet_engine/app/phase2/prompt_chain.py tet_engine/app/phase2/exam_catalog.py
  ```

## 6) Start engine (debug mode)
Option A (recommended):
- Press `F5` and choose **Run TET Engine (Uvicorn)**.

Option B:
- Run task: **Run TET Engine**.

API docs:
- http://127.0.0.1:8001/docs

## 7) Basic first-use sequence
1. `POST /v2/hierarchy/bootstrap`
2. `POST /v2/admin/users`
3. `POST /v2/auth/login` (email + password)
4. `POST /v2/sources/pdf`
5. `POST /v2/questions/generate-grounded`
6. `POST /v1/questions/review`
7. `POST /v2/publish/report`

## 8) Use in your system
- Keep this engine as a backend service.
- Your app frontend (mobile/web) calls these APIs.
- Persist report files from `tet_engine_data/reports/` for audit.
