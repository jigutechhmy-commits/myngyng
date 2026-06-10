"""review scan & list up: review_summaries, elimination_reason

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "candidate_products",
        sa.Column("elimination_reason", sa.String(50), nullable=True),
    )

    op.create_table(
        "review_summaries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "candidate_id",
            sa.String(36),
            sa.ForeignKey("candidate_products.id"),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("sources", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("fit_score", sa.Integer(), nullable=False),
        sa.Column("budget_score", sa.Integer(), nullable=False),
        sa.Column("satisfaction_score", sa.Integer(), nullable=False),
        sa.Column("missing_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("critical_flaw", sa.String(500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("review_summaries")
    op.drop_column("candidate_products", "elimination_reason")
