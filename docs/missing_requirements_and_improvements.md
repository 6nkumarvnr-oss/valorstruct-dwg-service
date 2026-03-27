# Missing requirements and recommended improvements

This is a practical gap analysis for the current exam-question-bank engine.

## 1) Important missing requirements (high priority)

## A. Authentication and authorization (must-have)
- Current auth is in-memory token stub.
- Missing JWT validation middleware and token expiry.
- Missing role permission checks per endpoint (super_admin/content_admin/reviewer).

**Recommendation**
1. Add JWT access + refresh tokens with expiry.
2. Add dependency-based role guard in FastAPI.
3. Store sessions/revoked tokens in DB or Redis.

## B. Database migrations (must-have)
- Current schema is create-all style and static SQL file.
- Missing versioned migration workflow.

**Recommendation**
1. Add Alembic migration setup.
2. Enforce migration on deploy.
3. Add rollback-tested migration scripts.

## C. Test coverage (must-have)
- Current checks are compile-only.
- Missing unit/integration/API tests.

**Recommendation**
1. Add pytest + httpx test client.
2. Cover ingestion, generation, review, publish, auth flows.
3. Add CI pass criteria: tests + coverage threshold.

## D. Input validation and error handling (must-have)
- API currently returns some error strings in success models.
- Missing standardized error schema and status codes.

**Recommendation**
1. Raise proper `HTTPException` with status codes.
2. Add global exception handler.
3. Add typed error response model.

## E. Security hardening (must-have)
- Missing rate limiting, request size controls, CORS policy, and strict file validation.

**Recommendation**
1. Add upload size and file type validation.
2. Add rate limiting (Redis-based).
3. Add strict CORS allowlist and secure headers.

---

## 2) Product-quality improvements (should-have)

## A. Retrieval quality
- Current retrieval is keyword overlap only.

**Recommendation**
- Add embeddings + pgvector hybrid retrieval (semantic + keyword).
- Add reranker for source chunk relevance.

## B. Question quality
- Add automatic quality scorers for ambiguity, duplication, and curriculum fit.
- Add answer-key cross-validation step before publish.

## C. Observability
- Add structured logs, correlation IDs, metrics, traces.
- Add dashboards for generation latency, failure rates, publish counts.

## D. Async job processing
- Move PDF parsing and large generation to queue workers.
- Add retry policy and dead-letter queue.

---

## 3) Scale and reliability (should-have)
- Multi-tenant isolation (if multiple institutes/use-cases).
- Object storage abstraction (S3/GCS/Azure).
- Backup and disaster recovery plan.
- API versioning policy and deprecation strategy.

---

## 4) Compliance and content governance (must-have for exams)
- Source licensing metadata per document.
- Source attribution trace in generated output.
- Human-review gate for all high-stakes exam sets.
- Plagiarism and similarity checks before publishing.

---

## 5) Suggested implementation order
1. JWT auth + role guards.
2. Alembic migrations.
3. pytest suite + CI test stage.
4. standardized error handling.
5. upload/rate-limit security hardening.
6. vector retrieval + quality scorers.
7. async workers + observability stack.
