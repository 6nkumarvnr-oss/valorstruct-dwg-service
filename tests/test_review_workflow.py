from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from types import SimpleNamespace

import pytest

pytest.importorskip("sqlalchemy")

from tet_engine.app.models import QuestionEditRequest, QuestionOption, ReviewActionRequest
from tet_engine.app import services


@dataclass
class DummyColumn:
    name: str

    def __eq__(self, other: object):
        return ("eq", self.name, other)

    def desc(self):
        return ("desc", self.name)


class DummyGeneratedQuestion:
    id = DummyColumn("id")
    exam_code = DummyColumn("exam_code")
    paper_name = DummyColumn("paper_name")
    subject_name = DummyColumn("subject_name")
    topic_name = DummyColumn("topic_name")
    status = DummyColumn("status")


class FakeQuery:
    def __init__(self, rows: list[SimpleNamespace]):
        self.rows = rows

    def filter(self, condition):
        if isinstance(condition, tuple) and condition[0] == "eq":
            _, key, value = condition
            self.rows = [row for row in self.rows if getattr(row, key) == value]
        return self

    def order_by(self, ordering):
        if isinstance(ordering, tuple) and ordering[0] == "desc":
            _, key = ordering
            self.rows = sorted(self.rows, key=lambda row: getattr(row, key), reverse=True)
        return self

    def all(self):
        return list(self.rows)

    def one_or_none(self):
        if not self.rows:
            return None
        return self.rows[0]


class FakeSession:
    def __init__(self, rows: list[SimpleNamespace]):
        self._rows = rows

    def query(self, _model):
        return FakeQuery(self._rows)

    def commit(self):
        return None

    def refresh(self, _row):
        return None


class FakeSessionLocal:
    def __init__(self, rows: list[SimpleNamespace]):
        self.rows = rows

    def __call__(self):
        return self

    def __enter__(self):
        self.session = FakeSession(self.rows)
        return self.session

    def __exit__(self, exc_type, exc, tb):
        return False


def _make_row(**kwargs) -> SimpleNamespace:
    defaults = {
        "id": 1,
        "exam_code": "PMP",
        "paper_name": "Paper A",
        "subject_name": "Planning",
        "topic_name": "Schedule",
        "question_text": "What is CPM?",
        "options_json": '[{"label":"A","text":"A"},{"label":"B","text":"B"}]',
        "correct_option": "A",
        "explanation": "Because A is correct",
        "difficulty": "easy",
        "status": "draft",
        "reviewer_email": None,
        "review_comments": None,
        "reviewed_at": None,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _patch_service_store(monkeypatch, rows: list[SimpleNamespace]):
    monkeypatch.setattr(services, "GeneratedQuestion", DummyGeneratedQuestion)
    monkeypatch.setattr(services, "SessionLocal", FakeSessionLocal(rows))
    monkeypatch.setattr(services, "exam_catalog_as_dict", lambda: [{"code": "PMP"}, {"code": "GATE"}])


def test_approve_flow(monkeypatch):
    row = _make_row()
    _patch_service_store(monkeypatch, [row])

    result = services.approve_question(1, ReviewActionRequest(reviewer_email="reviewer@x.com", comments="ok"))
    assert result["status"] == "approved"
    assert result["reviewer_email"] == "reviewer@x.com"
    assert result["reviewed_at"] is not None


def test_reject_flow(monkeypatch):
    row = _make_row()
    _patch_service_store(monkeypatch, [row])

    result = services.reject_question(1, ReviewActionRequest(reviewer_email="reviewer@x.com", comments="bad"))
    assert result["status"] == "rejected"
    assert result["review_comments"] == "bad"


def test_edit_flow(monkeypatch):
    row = _make_row(status="approved", reviewer_email="old@x.com", review_comments="done", reviewed_at=datetime.utcnow())
    _patch_service_store(monkeypatch, [row])

    payload = QuestionEditRequest(
        question_text="Updated text",
        options=[QuestionOption(label="A", text="Alpha"), QuestionOption(label="B", text="Beta")],
        correct_answer="B",
        explanation="Updated explanation",
    )
    result = services.edit_question(1, payload)
    assert result["question_text"] == "Updated text"
    assert result["correct_option"] == "B"
    assert result["status"] == "draft"
    assert result["reviewer_email"] is None


def test_invalid_approval_fails(monkeypatch):
    row = _make_row(explanation=" ")
    _patch_service_store(monkeypatch, [row])

    with pytest.raises(ValueError):
        services.approve_question(1, ReviewActionRequest(reviewer_email="reviewer@x.com", comments=""))
