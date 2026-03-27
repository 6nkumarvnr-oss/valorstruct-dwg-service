"""add review workflow columns to generated questions

Revision ID: 20260327_0002
Revises: 20260326_0001
Create Date: 2026-03-27
"""

from alembic import op
import sqlalchemy as sa


revision = "20260327_0002"
down_revision = "20260326_0001"
branch_labels = None
depends_on = None


question_status = sa.Enum("draft", "approved", "rejected", name="question_status")


def upgrade() -> None:
    bind = op.get_bind()
    question_status.create(bind, checkfirst=True)

    op.add_column(
        "generated_questions",
        sa.Column("status", question_status, nullable=False, server_default="draft"),
    )
    op.add_column("generated_questions", sa.Column("reviewer_email", sa.String(length=255), nullable=True))
    op.add_column("generated_questions", sa.Column("review_comments", sa.Text(), nullable=True))
    op.add_column("generated_questions", sa.Column("reviewed_at", sa.DateTime(), nullable=True))
    op.create_index("ix_generated_questions_status", "generated_questions", ["status"], unique=False)

    op.alter_column("generated_questions", "status", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_generated_questions_status", table_name="generated_questions")
    op.drop_column("generated_questions", "reviewed_at")
    op.drop_column("generated_questions", "review_comments")
    op.drop_column("generated_questions", "reviewer_email")
    op.drop_column("generated_questions", "status")
    question_status.drop(op.get_bind(), checkfirst=True)
