from __future__ import annotations

from typing import List, Optional

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile

from .models import (
    AdminUserCreate,
    AuthLoginRequest,
    AuthRefreshRequest,
    AuthTokenResponse,
    CourseCreate,
    ExamCreate,
    GenerateQuestionsRequest,
    GroundedGenerateRequest,
    GroundedQuestionResponse,
    PaperCreate,
    PublishReportRequest,
    PublishReportResponse,
    QuestionEditRequest,
    Question,
    ReviewActionRequest,
    ReviewQuestionRecord,
    ReviewDecision,
    ReviewStatus,
    SourceUpload,
    SubjectCreate,
    TopicCreate,
    ValidationIssue,
)
from .phase2.db import init_db
from .services import (
    authenticate_admin_access_token,
    bootstrap_exam_hierarchy,
    delete_source,
    create_admin_user,
    create_course,
    create_exam,
    create_paper,
    create_subject,
    create_topic,
    generate_grounded_questions,
    generate_questions,
    ingest_pdf_source,
    ingest_source,
    edit_question,
    list_admin_users,
    list_review_questions,
    list_sources,
    list_exam_catalog,
    list_questions,
    publish_questions_with_report,
    login_admin,
    refresh_access_token,
    reject_question,
    review_questions,
    require_user_role,
    approve_question,
    validate_questions,
)

app = FastAPI(title="TET Agentic Question Engine", version="0.2.0")


def require_admin_auth(authorization: str | None = Header(default=None)) -> dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="missing authorization header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="invalid authorization header")

    try:
        return authenticate_admin_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="invalid or expired access token")


def require_reviewer_auth(authorization: str | None = Header(default=None)) -> dict:
    user = require_admin_auth(authorization)
    try:
        require_user_role(user, {"super_admin", "content_admin", "reviewer"})
    except Exception:
        raise HTTPException(status_code=403, detail="insufficient role permissions")
    return user


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "tet-agentic-engine"}


@app.post("/v1/exams")
def create_exam_endpoint(payload: ExamCreate) -> dict:
    return create_exam(payload)


@app.post("/v1/courses")
def create_course_endpoint(payload: CourseCreate) -> dict:
    return create_course(payload)


@app.post("/v1/papers")
def create_paper_endpoint(payload: PaperCreate) -> dict:
    return create_paper(payload)


@app.post("/v1/subjects")
def create_subject_endpoint(payload: SubjectCreate) -> dict:
    return create_subject(payload)


@app.post("/v1/topics")
def create_topic_endpoint(payload: TopicCreate) -> dict:
    return create_topic(payload)


@app.post("/v1/sources")
def source_ingestion_endpoint(payload: SourceUpload) -> dict:
    return ingest_source(payload)




@app.get("/v2/catalog/exams")
def list_exam_catalog_endpoint() -> list[dict]:
    return list_exam_catalog()




@app.post("/v2/admin/users")
def create_admin_user_endpoint(payload: AdminUserCreate, _: dict = Depends(require_admin_auth)) -> dict:
    return create_admin_user(payload)


@app.get("/v2/admin/users")
def list_admin_users_endpoint(_: dict = Depends(require_admin_auth)) -> list[dict]:
    return list_admin_users()


@app.post("/v2/hierarchy/bootstrap")
def bootstrap_exam_hierarchy_endpoint() -> list[dict]:
    return bootstrap_exam_hierarchy()




@app.post("/v2/auth/login", response_model=AuthTokenResponse)
def auth_login_endpoint(payload: AuthLoginRequest) -> AuthTokenResponse:
    result = login_admin(payload)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return AuthTokenResponse(**result)


@app.post("/v2/auth/refresh", response_model=AuthTokenResponse)
def auth_refresh_endpoint(payload: AuthRefreshRequest) -> AuthTokenResponse:
    result = refresh_access_token(payload)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return AuthTokenResponse(**result)


@app.get("/v2/sources")
def list_sources_endpoint(exam_code: Optional[str] = None) -> list[dict]:
    return list_sources(exam_code=exam_code)


@app.delete("/v2/sources/{source_id}")
def delete_source_endpoint(source_id: str) -> dict:
    return delete_source(source_id)


@app.post("/v2/sources/pdf")
async def source_pdf_ingestion_endpoint(
    exam_code: str = Form(...),
    source_name: str = Form(...),
    source_type: str = Form("book"),
    file: UploadFile = File(...),
) -> dict:
    file_bytes = await file.read()
    return ingest_pdf_source(
        exam_code=exam_code,
        source_name=source_name,
        source_type=source_type,
        filename=file.filename or "source.pdf",
        content=file_bytes,
    )


@app.post("/v1/questions/generate", response_model=List[Question])
def generate_questions_endpoint(payload: GenerateQuestionsRequest) -> List[Question]:
    return generate_questions(payload)


@app.post("/v2/questions/generate-grounded", response_model=GroundedQuestionResponse)
def generate_grounded_questions_endpoint(payload: GroundedGenerateRequest) -> GroundedQuestionResponse:
    result = generate_grounded_questions(payload)
    return GroundedQuestionResponse(**result)


@app.get("/v2/questions/review", response_model=List[ReviewQuestionRecord])
def list_review_questions_endpoint(
    exam_code: str,
    paper_name: Optional[str] = None,
    subject_name: Optional[str] = None,
    topic_name: Optional[str] = None,
    status: Optional[ReviewStatus] = None,
    limit: int = 50,
    offset: int = 0,
    _: dict = Depends(require_reviewer_auth),
) -> List[ReviewQuestionRecord]:
    if limit < 1 or limit > 200:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 200")
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset must be >= 0")

    result = list_review_questions(
        exam_code=exam_code,
        paper_name=paper_name,
        subject_name=subject_name,
        topic_name=topic_name,
        status=status.value if status else None,
        limit=limit,
        offset=offset,
    )
    return [ReviewQuestionRecord(**item) for item in result]


@app.post("/v2/questions/{question_id}/approve", response_model=ReviewQuestionRecord)
def approve_question_endpoint(
    question_id: int,
    payload: ReviewActionRequest,
    _: dict = Depends(require_reviewer_auth),
) -> ReviewQuestionRecord:
    try:
        result = approve_question(question_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ReviewQuestionRecord(**result)


@app.post("/v2/questions/{question_id}/reject", response_model=ReviewQuestionRecord)
def reject_question_endpoint(
    question_id: int,
    payload: ReviewActionRequest,
    _: dict = Depends(require_reviewer_auth),
) -> ReviewQuestionRecord:
    try:
        result = reject_question(question_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ReviewQuestionRecord(**result)


@app.put("/v2/questions/{question_id}", response_model=ReviewQuestionRecord)
def edit_question_endpoint(
    question_id: int,
    payload: QuestionEditRequest,
    _: dict = Depends(require_reviewer_auth),
) -> ReviewQuestionRecord:
    try:
        result = edit_question(question_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ReviewQuestionRecord(**result)




@app.post("/v2/publish/report", response_model=PublishReportResponse)
def publish_report_endpoint(payload: PublishReportRequest) -> PublishReportResponse:
    return PublishReportResponse(**publish_questions_with_report(payload))


@app.post("/v1/questions/validate", response_model=List[ValidationIssue])
def validate_questions_endpoint(question_ids: List[str]) -> List[ValidationIssue]:
    return validate_questions(question_ids)


@app.post("/v1/questions/review")
def review_questions_endpoint(payload: ReviewDecision) -> dict:
    return review_questions(payload)


@app.get("/v1/questions", response_model=List[Question])
def list_questions_endpoint(status: Optional[str] = None) -> List[Question]:
    return list_questions(status=status)
