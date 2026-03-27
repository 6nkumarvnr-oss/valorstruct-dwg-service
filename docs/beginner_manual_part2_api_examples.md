# Beginner Manual Part-2: API command/output examples (copy-paste ready)

This guide gives terminal-style examples for each important API call.

> Base URL: `http://127.0.0.1:8001`

---

## 0) Start server
```bash
uvicorn tet_engine.app.main:app --reload --port 8001
```

Expected terminal output (example):
```text
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
```

---

## 1) Health check
```bash
curl -s http://127.0.0.1:8001/health | jq
```

Expected output:
```json
{
  "ok": true,
  "service": "tet-agentic-engine"
}
```

---

## 2) Bootstrap exam hierarchy
```bash
curl -s -X POST http://127.0.0.1:8001/v2/hierarchy/bootstrap | jq
```

Expected output (trimmed):
```json
[
  {"code":"PMP","name":"Project Management Professional"},
  {"code":"TNTET","name":"Tamil Nadu Teacher Eligibility Test"},
  {"code":"NCEES_FE_PE","name":"NCEES FE and PE Exams"},
  {"code":"GATE","name":"Graduate Aptitude Test in Engineering"},
  {"code":"TNPSC","name":"Tamil Nadu Public Service Commission Exams"}
]
```

---

## 3) Create Super Admin user
```bash
curl -s -X POST http://127.0.0.1:8001/v2/admin/users \
  -H "Content-Type: application/json" \
  -d '{
    "email":"owner@yourapp.com",
    "name":"Owner",
    "role":"super_admin",
    "password":"strongpass123"
  }' | jq
```

Expected output:
```json
{
  "id": "admin_xxxxxxxx",
  "email": "owner@yourapp.com",
  "name": "Owner",
  "role": "super_admin",
  "password_hash": "..."
}
```

---

## 4) Login and capture tokens
```bash
LOGIN_JSON=$(curl -s -X POST http://127.0.0.1:8001/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@yourapp.com","password":"strongpass123"}')

echo "$LOGIN_JSON" | jq
ACCESS_TOKEN=$(echo "$LOGIN_JSON" | jq -r '.access_token')
REFRESH_TOKEN=$(echo "$LOGIN_JSON" | jq -r '.refresh_token')
```

Expected output:
```json
{
  "access_token": "<long_token>",
  "refresh_token": "<long_token>",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## 5) Refresh token
```bash
curl -s -X POST http://127.0.0.1:8001/v2/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\":\"$REFRESH_TOKEN\"}" | jq
```

Expected output:
```json
{
  "access_token": "<new_access_token>",
  "refresh_token": "<same_or_new_refresh_token>",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## 6) Upload PDF source
```bash
curl -s -X POST http://127.0.0.1:8001/v2/sources/pdf \
  -F exam_code=TNTET \
  -F source_name='TNTET Paper 1 Source' \
  -F source_type=book \
  -F file=@/absolute/path/to/source.pdf | jq
```

Expected output:
```json
{
  "exam_code": "TNTET",
  "source_name": "TNTET Paper 1 Source",
  "storage_path": "tet_engine_data/uploads/<file>.pdf",
  "chunks_saved": 42
}
```

---

## 7) List sources
```bash
curl -s "http://127.0.0.1:8001/v2/sources?exam_code=TNTET" | jq
```

Expected output (example):
```json
[
  {
    "id": "1",
    "exam_code": "TNTET",
    "name": "TNTET Paper 1 Source",
    "type": "book",
    "origin": "pdf",
    "storage_path": "tet_engine_data/uploads/...pdf"
  }
]
```

---

## 8) Generate grounded questions
```bash
curl -s -X POST http://127.0.0.1:8001/v2/questions/generate-grounded \
  -H "Content-Type: application/json" \
  -d '{
    "exam_code":"TNTET",
    "paper_name":"Paper 1",
    "subject_name":"Child Development and Pedagogy",
    "topic_name":"Learning and Pedagogical Issues",
    "count":3,
    "difficulty":"medium",
    "language":"en",
    "top_k_chunks":5
  }' | jq
```

Expected output (trimmed):
```json
{
  "questions": [
    {
      "question_text": "...",
      "options": [{"label":"A","text":"..."}],
      "correct_option": "A",
      "explanation": "...",
      "source_chunk_ids": [1,2]
    }
  ],
  "retrieved_chunks": [
    {"id":1,"content":"...","chunk_index":0}
  ]
}
```

---

## 9) Review questions
```bash
curl -s -X POST http://127.0.0.1:8001/v1/questions/review \
  -H "Content-Type: application/json" \
  -d '{
    "question_ids":["q_example_1"],
    "approved":true,
    "reviewer":"owner@yourapp.com"
  }' | jq
```

Expected output:
```json
{
  "updated": ["q_example_1"],
  "status": "approved",
  "reviewer": "owner@yourapp.com"
}
```

---

## 10) Publish + report
```bash
curl -s -X POST http://127.0.0.1:8001/v2/publish/report \
  -H "Content-Type: application/json" \
  -d '{
    "exam_code":"TNTET",
    "paper_name":"Paper 1",
    "subject_name":"Child Development and Pedagogy",
    "topic_name":"Learning and Pedagogical Issues",
    "question_ids":["q_example_1"],
    "reviewer":"owner@yourapp.com"
  }' | jq
```

Expected output:
```json
{
  "report_path": "tet_engine_data/reports/publish_tntet_YYYYMMDD_HHMMSS.txt",
  "published_count": 1,
  "status": "published"
}
```

---

## 11) Delete source
```bash
curl -s -X DELETE http://127.0.0.1:8001/v2/sources/1 | jq
```

Expected output:
```json
{
  "deleted": true,
  "source_id": "1",
  "origin": "pdf",
  "exam_code": "TNTET"
}
```

---

## 12) Quick troubleshooting
If command fails:
1. Check server is running.
2. Check `.env` values.
3. Check DB and migrations.
4. Re-run login token command.
5. Check terminal logs for traceback.
