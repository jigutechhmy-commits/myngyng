"""choice: tournaments, tournament_matches

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tournaments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "session_id",
            sa.String(36),
            sa.ForeignKey("request_sessions.id"),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column(
            "winner_candidate_id",
            sa.String(36),
            sa.ForeignKey("candidate_products.id"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "tournament_matches",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "tournament_id",
            sa.String(36),
            sa.ForeignKey("tournaments.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("round_no", sa.Integer(), nullable=False),
        sa.Column("match_no", sa.Integer(), nullable=False),
        sa.Column(
            "candidate_a_id", sa.String(36), sa.ForeignKey("candidate_products.id"), nullable=False
        ),
        sa.Column(
            "candidate_b_id", sa.String(36), sa.ForeignKey("candidate_products.id"), nullable=False
        ),
        sa.Column(
            "winner_candidate_id",
            sa.String(36),
            sa.ForeignKey("candidate_products.id"),
            nullable=True,
        ),
        sa.Column("choice_reason", sa.Text(), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("tournament_matches")
    op.drop_table("tournaments")
