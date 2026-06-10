"""initial: pgvector extension, categories, request_sessions

Revision ID: 0001
Revises:
Create Date: 2026-06-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "categories",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name_ko", sa.String(100), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("spec_schema", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "request_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("category_id", sa.String(50), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("budget", sa.Integer(), nullable=False),
        sa.Column("budget_tolerance_pct", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("usage_text", sa.String(2000), nullable=False),
        sa.Column("priorities", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("tournament_size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("engine_phase", sa.String(20), nullable=False, server_default="created"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("request_sessions")
    op.drop_table("categories")
    op.execute("DROP EXTENSION IF EXISTS vector")
