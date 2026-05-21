"""documents.rag_collection

Revision ID: 004
Revises: 003
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("rag_collection", sa.String(32), nullable=True))
    op.create_index("ix_documents_rag_collection", "documents", ["rag_collection"])


def downgrade() -> None:
    op.drop_index("ix_documents_rag_collection", table_name="documents")
    op.drop_column("documents", "rag_collection")
