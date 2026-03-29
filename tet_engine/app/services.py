from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from uuid import uuid4

from .models import (
    AdminUserCreate,
    AuthLoginRequest,
    AuthRefreshRequest,
    CourseCreate,
    ExamCreate,
    GenerateQuestionsRequest,
    GroundedGenerateRequest,
    PaperCreate,
    Question,
    QuestionOption,
    ReviewDecision,
    PublishReportRequest,
    SourceUpload,
    SubjectCreate,
    TopicCreate,
    ValidationIssue,
)
from .phase2.db import GeneratedQuestion, SessionLocal, SourceChunk, SourceDocument
from .phase2.exam_catalog import as_dict as exam_catalog_as_dict
from .phase2.pdf_ingestion import ParsedChunk, chunk_text, extract_text_from_pdf, keyword_retrieve
from .phase2.prompt_chain import generate_grounded_mcqs
from .phase2.auth import create_access_token, create_refresh_token, decode_token, hash_password, verify_password


@dataclass
class Storage:
    exams: Dict[str, dict]
    courses: Dict[str, dict]
    papers: Dict[str, dict]
    subjects: Dict[str, dict]
    topics: Dict[str, dict]
    sources_by_exam: Dict[str, List[dict]]
    questions: Dict[str, Question]
    admin_users: Dict[str, dict]
    published_questions: Dict[str, dict]
    access_tokens: Dict[str, dict]
    refresh_tokens: Dict[str, str]


storage = Storage(
    exams={},
    courses={},
    papers={},
    subjects={},
    topics={},
    sources_by_exam=defaultdict(list),
    questions={},
    admin_users={},
    published_questions={},
    access_tokens={},
    refresh_tokens={},
)

UPLOAD_DIR = Path("tet_engine_data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR = Path("tet_engine_data/reports")
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def create_exam(payload: ExamCreate) -> dict:
    exam = {"code": payload.code.upper(), "name": payload.name}
    storage.exams[exam["code"]] = exam
    return exam


def create_course(payload: CourseCreate) -> dict:
    course_id = f"course_{uuid4().hex[:8]}"
    course = {"id": course_id, "exam_code": payload.exam_code.upper(), "name": payload.name}
    storage.courses[course_id] = course
    return course


def create_paper(payload: PaperCreate) -> dict:
    paper_id = f"paper_{uuid4().hex[:8]}"
    paper = {"id": paper_id, "course_id": payload.course_id, "name": payload.name}
    storage.papers[paper_id] = paper
    return paper


def create_subject(payload: SubjectCreate) -> dict:
    subject_id = f"subject_{uuid4().hex[:8]}"
    subject = {"id": subject_id, "paper_id": payload.paper_id, "name": payload.name}
    storage.subjects[subject_id] = subject
    return subject


def create_topic(payload: TopicCreate) -> dict:
    topic_id = f"topic_{uuid4().hex[:8]}"
    topic = {"id": topic_id, "subject_id": payload.subject_id, "name": payload.name}
    storage.topics[topic_id] = topic
    return topic


def ingest_source(payload: SourceUpload) -> dict:
    source = {
        "id": f"source_{uuid4().hex[:8]}",
        "name": payload.source_name,
        "type": payload.source_type,
        "text": payload.text,
    }
    storage.sources_by_exam[payload.exam_code.upper()].append(source)
    return {"exam_code": payload.exam_code.upper(), "source_id": source["id"]}


def ingest_pdf_source(*, exam_code: str, source_name: str, source_type: str, filename: str, content: bytes) -> dict:
    exam = exam_code.upper()
    safe_filename = f"{uuid4().hex[:8]}_{filename}"
    file_path = UPLOAD_DIR / safe_filename
    file_path.write_bytes(content)

    text = extract_text_from_pdf(file_path)
    parsed_chunks = chunk_text(text)

    with SessionLocal() as session:
        document = SourceDocument(exam_code=exam, name=source_name, source_type=source_type, storage_path=str(file_path))
        session.add(document)
        session.flush()

        for parsed in parsed_chunks:
            session.add(
                SourceChunk(
                    document_id=document.id,
                    chunk_index=parsed.chunk_index,
                    topic_hint="",
                    content=parsed.content,
                )
            )

        session.commit()

    return {
        "exam_code": exam,
        "source_name": source_name,
        "storage_path": str(file_path),
        "chunks_saved": len(parsed_chunks),
    }


def generate_questions(payload: GenerateQuestionsRequest) -> List[Question]:
    exam_code = payload.exam_code.upper()
    source_name = storage.sources_by_exam[exam_code][0]["name"] if storage.sources_by_exam[exam_code] else "manual_seed"

    generated: List[Question] = []
    for idx in range(1, payload.count + 1):
        q_id = f"q_{uuid4().hex[:10]}"
        question = Question(
            id=q_id,
            exam_code=exam_code,
            paper_name=payload.paper_name,
            subject_name=payload.subject_name,
            topic_name=payload.topic_name,
            question_text=(
                f"[{payload.difficulty}] {payload.topic_name}: Sample MCQ #{idx}. "
                "(Replace this template with LLM generation + retrieval pipeline.)"
            ),
            options=[
                QuestionOption(label="A", text="Option A"),
                QuestionOption(label="B", text="Option B"),
                QuestionOption(label="C", text="Option C"),
                QuestionOption(label="D", text="Option D"),
            ],
            correct_option="B",
            explanation=(
                "Template explanation. In production, include grounded explanation with chapter/page reference."
            ),
            difficulty=payload.difficulty,
            tags=[payload.subject_name, payload.topic_name, payload.language],
            source_reference=source_name,
            confidence_score=0.78,
        )
        storage.questions[q_id] = question
        generated.append(question)
    return generated


def generate_grounded_questions(payload: GroundedGenerateRequest) -> dict:
    exam = payload.exam_code.upper()
    with SessionLocal() as session:
        chunks = (
            session.query(SourceChunk)
            .join(SourceDocument, SourceChunk.document_id == SourceDocument.id)
            .filter(SourceDocument.exam_code == exam)
            .all()
        )

        parsed_chunks = [
            {"id": chunk.id, "content": chunk.content, "chunk_index": chunk.chunk_index}
            for chunk in chunks
        ]

        retrieval_chunks = [
            ParsedChunk(chunk_index=item["chunk_index"], content=item["content"])
            for item in parsed_chunks
        ]
        selected = keyword_retrieve(
            chunks=retrieval_chunks,
            query=f"{payload.subject_name} {payload.topic_name}",
            top_k=payload.top_k_chunks,
        )

        selected_by_index = {item.chunk_index for item in selected}
        retrieved = [item for item in parsed_chunks if item["chunk_index"] in selected_by_index]

        llm_result = generate_grounded_mcqs(
            exam_code=exam,
            paper_name=payload.paper_name,
            subject_name=payload.subject_name,
            topic_name=payload.topic_name,
            difficulty=payload.difficulty.value,
            language=payload.language,
            count=payload.count,
            source_chunks=retrieved,
        )

        for question in llm_result.get("questions", []):
            session.add(
                GeneratedQuestion(
                    exam_code=exam,
                    paper_name=payload.paper_name,
                    subject_name=payload.subject_name,
                    topic_name=payload.topic_name,
                    question_text=question["question_text"],
                    options_json=json.dumps(question["options"], ensure_ascii=False),
                    correct_option=question["correct_option"],
                    explanation=question["explanation"],
                    difficulty=payload.difficulty.value,
                    source_chunk_ids=json.dumps(question.get("source_chunk_ids", [])),
                )
            )
        session.commit()

    return {"questions": llm_result.get("questions", []), "retrieved_chunks": retrieved}


def validate_questions(question_ids: List[str]) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    for question_id in question_ids:
        question = storage.questions.get(question_id)
        if not question:
            issues.append(ValidationIssue(question_id=question_id, issue="Question not found", severity="error"))
            continue
        if "Sample MCQ" in question.question_text:
            issues.append(
                ValidationIssue(
                    question_id=question_id,
                    issue="Template content detected; replace with generated production text.",
                    severity="warning",
                )
            )
    return issues


def review_questions(payload: ReviewDecision) -> dict:
    new_status = "approved" if payload.approved else "rejected"
    updated = []
    for question_id in payload.question_ids:
        question = storage.questions.get(question_id)
        if question:
            question.status = new_status
            storage.questions[question_id] = question
            updated.append(question_id)
    return {"updated": updated, "status": new_status, "reviewer": payload.reviewer}


def list_questions(status: str | None = None) -> List[Question]:
    questions = list(storage.questions.values())
    if status:
        return [question for question in questions if question.status == status]
    return questions


def list_exam_catalog() -> list[dict]:
    return exam_catalog_as_dict()


def create_admin_user(payload: AdminUserCreate) -> dict:
    user_id = f"admin_{uuid4().hex[:8]}"
    user = {
        "id": user_id,
        "email": payload.email,
        "name": payload.name,
        "role": payload.role.value,
        "password_hash": hash_password(payload.password),
    }
    storage.admin_users[user_id] = user
    return _public_admin_user(user)


def list_admin_users() -> list[dict]:
    return [_public_admin_user(user) for user in storage.admin_users.values()]


def _public_admin_user(user: dict) -> dict:
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
    }


def bootstrap_exam_hierarchy() -> list[dict]:
    templates = [
        {"code": "PMP", "name": "Project Management Professional"},
        {"code": "TNTET", "name": "Tamil Nadu Teacher Eligibility Test"},
        {"code": "NCEES_FE_PE", "name": "NCEES FE and PE Exams"},
        {"code": "GATE", "name": "Graduate Aptitude Test in Engineering"},
        {"code": "TNPSC", "name": "Tamil Nadu Public Service Commission Exams"},
    ]
    created = []
    for item in templates:
        storage.exams[item["code"]] = item
        created.append(item)
    return created


def publish_questions_with_report(payload: PublishReportRequest) -> dict:
    published = []
    for qid in payload.question_ids:
        question = storage.questions.get(qid)
        if question:
            question.status = "published"
            storage.questions[qid] = question
            storage.published_questions[qid] = {
                "exam_code": payload.exam_code.upper(),
                "paper_name": payload.paper_name,
                "subject_name": payload.subject_name,
                "topic_name": payload.topic_name,
                "published_at": datetime.utcnow().isoformat(),
            }
            published.append(question)

    report_name = f"publish_{payload.exam_code.lower()}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
    report_path = REPORT_DIR / report_name

    lines = [
        "Question Bank Publish Report",
        f"Exam: {payload.exam_code}",
        f"Paper: {payload.paper_name}",
        f"Subject: {payload.subject_name}",
        f"Topic: {payload.topic_name}",
        f"Reviewer: {payload.reviewer}",
        f"Published Count: {len(published)}",
        "-" * 50,
    ]

    for index, question in enumerate(published, start=1):
        lines.extend(
            [
                f"{index}. {question.id}",
                f"Q: {question.question_text}",
                f"Answer: {question.correct_option}",
                f"Explanation: {question.explanation}",
                "",
            ]
        )

    report_path.write_text("\n".join(lines), encoding="utf-8")

    return {"report_path": str(report_path), "published_count": len(published), "status": "published"}


def login_admin(payload: AuthLoginRequest) -> dict:
    matched = None
    for user in storage.admin_users.values():
        if user["email"].lower() == payload.email.lower():
            matched = user
            break

    if not matched:
        return {"error": "admin user not found"}

    if not verify_password(payload.password, matched["password_hash"]):
        return {"error": "invalid credentials"}

    access_token = create_access_token(user_id=matched["id"], email=matched["email"], role=matched["role"])
    refresh_token = create_refresh_token(user_id=matched["id"], email=matched["email"], role=matched["role"])
    storage.access_tokens[access_token] = {"user_id": matched["id"], "email": matched["email"]}
    storage.refresh_tokens[refresh_token] = matched["id"]
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "expires_in": 1800}


def refresh_access_token(payload: AuthRefreshRequest) -> dict:
    if payload.refresh_token not in storage.refresh_tokens:
        return {"error": "invalid refresh token"}

    try:
        token_data = decode_token(payload.refresh_token)
    except Exception:
        return {"error": "invalid refresh token"}

    if token_data.get("type") != "refresh":
        return {"error": "invalid token type"}

    user_id = token_data.get("sub", "")
    user = storage.admin_users.get(user_id)
    if not user:
        return {"error": "user not found"}

    new_access_token = create_access_token(user_id=user_id, email=user["email"], role=user["role"])
    storage.access_tokens[new_access_token] = {"user_id": user_id, "email": user["email"]}
    return {"access_token": new_access_token, "refresh_token": payload.refresh_token, "token_type": "bearer", "expires_in": 1800}


def list_sources(exam_code: str | None = None) -> list[dict]:
    items: list[dict] = []

    for code, sources in storage.sources_by_exam.items():
        if exam_code and code != exam_code.upper():
            continue
        for source in sources:
            items.append({
                "id": source["id"],
                "exam_code": code,
                "name": source["name"],
                "type": source["type"],
                "origin": "manual",
            })

    with SessionLocal() as session:
        query = session.query(SourceDocument)
        if exam_code:
            query = query.filter(SourceDocument.exam_code == exam_code.upper())
        for row in query.all():
            items.append(
                {
                    "id": str(row.id),
                    "exam_code": row.exam_code,
                    "name": row.name,
                    "type": row.source_type,
                    "origin": "pdf",
                    "storage_path": row.storage_path,
                }
            )

    return items


def delete_source(source_id: str) -> dict:
    for exam_code, sources in storage.sources_by_exam.items():
        for index, source in enumerate(sources):
            if source["id"] == source_id:
                sources.pop(index)
                return {"deleted": True, "source_id": source_id, "origin": "manual", "exam_code": exam_code}

    if source_id.isdigit():
        with SessionLocal() as session:
            row = session.query(SourceDocument).filter(SourceDocument.id == int(source_id)).one_or_none()
            if row:
                session.delete(row)
                session.commit()
                return {"deleted": True, "source_id": source_id, "origin": "pdf", "exam_code": row.exam_code}

    return {"deleted": False, "source_id": source_id, "reason": "not found"}
