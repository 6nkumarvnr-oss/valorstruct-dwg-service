# Beginner manual: Build and run this exam-question engine step by step

This is a beginner-friendly manual to run the project from zero.

## 0) What you are building
You are building a backend service that can:
- store exam hierarchy (exam/course/paper/subject/topic)
- ingest source PDFs
- generate grounded MCQs
- allow review + publish
- create publish reports

## 1) Install software on your system
Install these first:
1. Python 3.10+
2. Git
3. PostgreSQL 14+
4. VS Code

Optional but useful:
- pgAdmin (to inspect database)
- Postman (to test APIs)

## 2) Download project code
```bash
git clone <your-repo-url>
cd valorstruct-dwg-service
```

## 3) Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

(Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 4) Install dependencies
```bash
pip install -r requirements.txt
```

## 5) Configure environment variables
1. Copy `.env.example` to `.env`
2. Update values:
- `DATABASE_URL`
- `OPENAI_API_KEY`
- `JWT_SECRET`

Example:
```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/tet_engine
OPENAI_API_KEY=your_real_key
OPENAI_MODEL=gpt-4.1-mini
JWT_SECRET=use_a_long_random_value
JWT_ALGORITHM=HS256
JWT_ACCESS_MINUTES=30
JWT_REFRESH_DAYS=7
```

## 6) Create database
In PostgreSQL create DB:
```sql
CREATE DATABASE tet_engine;
```

## 7) Run migrations (important)
```bash
alembic upgrade head
```

This creates required tables.

## 8) Start the API service
```bash
uvicorn tet_engine.app.main:app --reload --port 8001
```

Open API docs:
- http://127.0.0.1:8001/docs

## 9) First API workflow (beginner sequence)

### Step A: Bootstrap exam templates
`POST /v2/hierarchy/bootstrap`

### Step B: Create super admin
`POST /v2/admin/users`
```json
{
  "email": "owner@yourapp.com",
  "name": "Owner",
  "role": "super_admin",
  "password": "strongpass123"
}
```

### Step C: Login
`POST /v2/auth/login`
```json
{
  "email": "owner@yourapp.com",
  "password": "strongpass123"
}
```

### Step D: Upload source PDF
`POST /v2/sources/pdf` (multipart form)
- exam_code
- source_name
- source_type
- file

### Step E: Generate grounded questions
`POST /v2/questions/generate-grounded`

### Step F: Review questions
`POST /v1/questions/review`

### Step G: Publish report
`POST /v2/publish/report`

## 10) VS Code easy mode
Use built-in files:
- `.vscode/launch.json` (press F5 to run)
- `.vscode/tasks.json` (install, compile, run tasks)

## 11) Basic checks before deployment
Run these commands:
```bash
python -m py_compile tet_engine/app/main.py tet_engine/app/models.py tet_engine/app/services.py tet_engine/app/phase2/db.py tet_engine/app/phase2/pdf_ingestion.py tet_engine/app/phase2/prompt_chain.py tet_engine/app/phase2/exam_catalog.py tet_engine/app/phase2/auth.py
pytest -q
```

## 12) Deploy plan for beginners
1. Deploy backend first (Cloud Run / Render / Railway)
2. Connect managed Postgres
3. Test with Swagger/Postman
4. Build admin web panel
5. Integrate mobile app last

## 13) Common beginner mistakes
- Not running migrations.
- Wrong DB URL.
- Missing API key.
- Using weak JWT secret.
- Trying mobile integration before admin workflow is stable.

## 14) If you are stuck
Check in this order:
1. `.env` values
2. database running status
3. migration status
4. API health endpoint (`GET /health`)
5. terminal logs
