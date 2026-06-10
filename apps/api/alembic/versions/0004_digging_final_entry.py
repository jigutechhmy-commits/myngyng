"""digging & final entry: decision_narratives, final_entry_cards

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "decision_narratives",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "candidate_id",
            sa.String(36),
            sa.ForeignKey("candidate_products.id"),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column("narrative", sa.String(300), nullable=False),
        sa.Column("story", sa.Text(), nullable=False),
        sa.Column("digging_scores", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("sources", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("ai_inferred", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "final_entry_cards",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "candidate_id",
            sa.String(36),
            sa.ForeignKey("candidate_products.id"),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column("headline", sa.String(200), nullable=False),
        sa.Column("key_specs", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("pros", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("cons", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("review_digest", sa.Text(), nullable=False),
        sa.Column("worldview", sa.Text(), nullable=False),
        sa.Column("recommended_for", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("not_recommended_for", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("final_entry_cards")
    op.drop_table("decision_narratives")
