"""add ai summary

Revision ID: 1599bb7c0928
Revises: 22c64dc2e964
Create Date: 2026-09-13 09:36:57.858455

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.

revision: str = '1599bb7c0928'
down_revision: Union[str, Sequence[str], None] = '22c64dc2e964'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'documents',
        sa.Column('ai_summary', sa.Text(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('documents', 'ai_summary')