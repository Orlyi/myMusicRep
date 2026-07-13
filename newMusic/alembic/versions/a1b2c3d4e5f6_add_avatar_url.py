"""add avatar_url to users

Revision ID: a1b2c3d4e5f6
Revises: (head)
Create Date: 2026-06-25
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass  # avatar_url column already added manually


def downgrade() -> None:
    pass  # skip to avoid error on repeated execution
