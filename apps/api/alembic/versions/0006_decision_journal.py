"""decision journal & choice confidence

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "decision_journal_entries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "session_id",
            sa.String(36),
            sa.ForeignKey("request_sessions.id"),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column(
            "winner_candidate_id",
            sa.String(36),
            sa.ForeignKey("candidate_products.id"),
            nullable=False,
        ),
        sa.Column("choice_log", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column(
            "decided_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("confidence", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("followup_due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("followup_satisfaction", sa.Integer(), nullable=True),
        sa.Column("followup_answered_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("decision_journal_entries")
