from __future__ import annotations

from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class ExamCreate(BaseModel):
    code: str = Field(..., description="Unique code like TET or CTET")
    name: str


class CourseCreate(BaseModel):
    exam_code: str
    name: str


class PaperCreate(BaseModel):
    course_id: str
    name: str


class SubjectCreate(BaseModel):
    paper_id: str
    name: str


class TopicCreate(BaseModel):
    subject_id: str
    name: str


class SourceUpload(BaseModel):
    exam_code: str
    source_name: str
    source_type: str = Field(..., description="book | notes | previous_year_paper")
    text: str = Field(..., description="Raw source text (replace with PDF parser later)")


class GenerateQuestionsRequest(BaseModel):
    exam_code: str
    paper_name: str
    subject_name: str
    topic_name: str
    count: int = Field(10, ge=1, le=100)
    difficulty: Difficulty = Difficulty.medium
    language: str = "en"


class GroundedGenerateRequest(GenerateQuestionsRequest):
    top_k_chunks: int = Field(5, ge=1, le=20)


class QuestionOption(BaseModel):
    label: str
    text: str


class Question(BaseModel):
    id: str
    exam_code: str
    paper_name: str
    subject_name: str
    topic_name: str
    question_text: str
    options: List[QuestionOption]
    correct_option: str
    explanation: str
    difficulty: Difficulty
    tags: List[str]
    source_reference: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    status: str = "draft"


class ValidationIssue(BaseModel):
    question_id: str
    issue: str
    severity: str = "warning"


class ReviewDecision(BaseModel):
    question_ids: List[str]
    approved: bool
    reviewer: Optional[str] = "admin"


class GroundedQuestionResponse(BaseModel):
    questions: List[dict[str, Any]]
    retrieved_chunks: List[dict[str, Any]]


class AdminRole(str, Enum):
    super_admin = "super_admin"
    content_admin = "content_admin"
    reviewer = "reviewer"


class AdminUserCreate(BaseModel):
    email: str
    name: str
    role: AdminRole
    password: str = Field(..., min_length=8)


class PublishReportRequest(BaseModel):
    exam_code: str
    paper_name: str
    subject_name: str
    topic_name: str
    question_ids: List[str]
    reviewer: str = "admin"


class PublishReportResponse(BaseModel):
    report_path: str
    published_count: int
    status: str


class AuthLoginRequest(BaseModel):
    email: str
    password: str


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800


class AuthRefreshRequest(BaseModel):
    refresh_token: str
