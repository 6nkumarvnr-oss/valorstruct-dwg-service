"""initial exam engine tables

Revision ID: 20260326_0001
Revises:
Create Date: 2026-03-26
"""

from alembic import op
import sqlalchemy as sa


revision = "20260326_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "exams",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=20), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_exams_code", "exams", ["code"], unique=True)

    op.create_table(
        "source_documents",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("exam_code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_source_documents_exam_code", "source_documents", ["exam_code"], unique=False)

    op.create_table(
        "source_chunks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("source_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("topic_hint", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_source_chunks_document_id", "source_chunks", ["document_id"], unique=False)

    op.create_table(
        "generated_questions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("exam_code", sa.String(length=20), nullable=False),
        sa.Column("paper_name", sa.String(length=100), nullable=False),
        sa.Column("subject_name", sa.String(length=100), nullable=False),
        sa.Column("topic_name", sa.String(length=150), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("options_json", sa.Text(), nullable=False),
        sa.Column("correct_option", sa.String(length=2), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.String(length=20), nullable=False),
        sa.Column("source_chunk_ids", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_generated_questions_exam_code", "generated_questions", ["exam_code"], unique=False)
    op.create_index("ix_generated_questions_difficulty", "generated_questions", ["difficulty"], unique=False)
    op.create_index("ix_generated_questions_topic_name", "generated_questions", ["topic_name"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_generated_questions_topic_name", table_name="generated_questions")
    op.drop_index("ix_generated_questions_difficulty", table_name="generated_questions")
    op.drop_index("ix_generated_questions_exam_code", table_name="generated_questions")
    op.drop_table("generated_questions")

    op.drop_index("ix_source_chunks_document_id", table_name="source_chunks")
    op.drop_table("source_chunks")

    op.drop_index("ix_source_documents_exam_code", table_name="source_documents")
    op.drop_table("source_documents")

    op.drop_index("ix_exams_code", table_name="exams")
    op.drop_table("exams")
