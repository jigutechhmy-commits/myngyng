"""plan & research: spec_sheet column, candidate_products table

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("request_sessions", sa.Column("spec_sheet", sa.JSON(), nullable=True))

    op.create_table(
        "candidate_products",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "session_id",
            sa.String(36),
            sa.ForeignKey("request_sessions.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("brand", sa.String(100), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("specs", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("source", sa.String(20), nullable=False, server_default="ai"),
        sa.Column("status", sa.String(20), nullable=False, server_default="candidate"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("candidate_products")
    op.drop_column("request_sessions", "spec_sheet")
