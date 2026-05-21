"""check_runs table

Revision ID: 002
Revises: 001
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "check_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("overall_status", sa.String(16), nullable=False),
        sa.Column("report_json", postgresql.JSONB(), nullable=False),
        sa.Column("report_markdown", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_check_runs_project_id", "check_runs", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_check_runs_project_id", table_name="check_runs")
    op.drop_table("check_runs")
