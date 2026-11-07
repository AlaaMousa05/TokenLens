"""execution columns

Revision ID: 0002_execution_columns
Revises: 0001_initial
Create Date: 2026-11-06

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_execution_columns"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("results", sa.Column("cached_tokens", sa.Integer(), nullable=True))
    op.add_column("results", sa.Column("reasoning_tokens", sa.Integer(), nullable=True))
    op.add_column("results", sa.Column("completion_outcome", sa.String(length=32), nullable=True))
    op.add_column(
        "results",
        sa.Column("tokens_estimated", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("results", sa.Column("input_price_per_mtok", sa.Numeric(12, 6), nullable=True))
    op.add_column("results", sa.Column("output_price_per_mtok", sa.Numeric(12, 6), nullable=True))
    op.add_column("results", sa.Column("cached_input_price_per_mtok", sa.Numeric(12, 6), nullable=True))

    op.add_column(
        "rubrics",
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
    )
    op.add_column(
        "rubrics",
        sa.Column("is_frozen", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.add_column("dataset_items", sa.Column("category", sa.String(length=64), nullable=True))

    op.add_column("runs", sa.Column("error_message", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("runs", "error_message")

    op.drop_column("dataset_items", "category")

    op.drop_column("rubrics", "is_frozen")
    op.drop_column("rubrics", "version")

    op.drop_column("results", "cached_input_price_per_mtok")
    op.drop_column("results", "output_price_per_mtok")
    op.drop_column("results", "input_price_per_mtok")
    op.drop_column("results", "tokens_estimated")
    op.drop_column("results", "completion_outcome")
    op.drop_column("results", "reasoning_tokens")
    op.drop_column("results", "cached_tokens")
