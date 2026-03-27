# Step-by-step: Build and run your Question Bank Test Engine

This guide explains how to run your engine, generate question banks, and own your custom rules/workflow.

## 0) What you get
- Admin API for exam hierarchy.
- PDF ingestion and chunking.
- Grounded MCQ generation.
- Review and publish flow.
- Notepad/text publish report.

## 1) Install and run
```bash
cd /workspace/valorstruct-dwg-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL='postgresql+psycopg://postgres:postgres@localhost:5432/tet_engine'
export OPENAI_API_KEY='YOUR_KEY'
export OPENAI_MODEL='gpt-4.1-mini'
uvicorn tet_engine.app.main:app --reload --port 8001
```

Open:
- Swagger UI: `http://127.0.0.1:8001/docs`

## 2) Initialize your engine (one time)
### 2.1 Bootstrap exam families
```bash
curl -X POST http://127.0.0.1:8001/v2/hierarchy/bootstrap
```

### 2.2 Create Super Admin
```bash
curl -X POST http://127.0.0.1:8001/v2/admin/users \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@yourapp.com","name":"Owner","role":"super_admin","password":"strongpass123"}'
```

## 3) Build one test pipeline (repeat per exam)
### 3.1 Create your own hierarchy
- Create exam/course/paper/subject/topic from v1 endpoints.
- Use your own naming and rules.

### 3.2 Upload syllabus/books/PYQ PDF
```bash
curl -X POST http://127.0.0.1:8001/v2/sources/pdf \
  -F exam_code=TNTET \
  -F source_name='TNTET Paper 1 Source' \
  -F source_type=book \
  -F file=@/path/to/file.pdf
```

### 3.3 Generate grounded questions
```bash
curl -X POST http://127.0.0.1:8001/v2/questions/generate-grounded \
  -H "Content-Type: application/json" \
  -d '{
    "exam_code":"TNTET",
    "paper_name":"Paper 1",
    "subject_name":"Child Development and Pedagogy",
    "topic_name":"Learning and Pedagogical Issues",
    "count":20,
    "difficulty":"medium",
    "language":"en",
    "top_k_chunks":5
  }'
```

### 3.4 Review + approve
- Use your reviewer/admin flow.
- Edit option/explanation when required.

### 3.5 Publish + report
```bash
curl -X POST http://127.0.0.1:8001/v2/publish/report \
  -H "Content-Type: application/json" \
  -d '{
    "exam_code":"TNTET",
    "paper_name":"Paper 1",
    "subject_name":"Child Development and Pedagogy",
    "topic_name":"Learning and Pedagogical Issues",
    "question_ids":["q_xxx","q_yyy"],
    "reviewer":"owner@yourapp.com"
  }'
```

Report path returned in response under `report_path`.

## 4) Create different question banks continuously
Use this cycle repeatedly:
1. Add new topic/source docs.
2. Generate questions by topic + difficulty.
3. Review quality.
4. Publish.
5. Analyze student performance.
6. Regenerate weak-topic sets.

This supports unlimited banks per exam, language, and difficulty.

## 5) Credits / ownership / "my rules"
### Can you use your own rules?
Yes. You can define your own:
- prompt policies,
- validation rules,
- approval workflow,
- scoring/report structure,
- UI/UX flow.

### Will credits go to others?
- **Your app logic/workflow/custom rules**: yours.
- **Third-party model/service usage** (OpenAI/cloud/db/libs): governed by each provider license and terms.
- **Exam source PDFs/papers**: use only if legally permitted; exam bodies may restrict redistribution.

### Practical recommendation
- Keep a `SOURCE_ATTRIBUTION` table with URL + access date.
- Keep a `CONTENT_LICENSE` flag per source.
- Publish only legally safe and reviewed content.

## 6) Production best practice for your 44-domain app
- Keep engine as independent microservice.
- Connect all domains through queue/jobs.
- Use role-based approval before publish.
- Keep publish reports for auditing and rollback.
- Add automated quality checks before publish gate.
