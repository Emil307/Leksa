"""add_media_to_questions

Revision ID: c7d8e9f0a1b2
Revises: 21b98f40486f
Create Date: 2026-04-09 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c7d8e9f0a1b2'
down_revision: Union[str, None] = '21b98f40486f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'idioms',
        sa.Column('media_file', sa.String(255), nullable=True),
    )
    op.add_column(
        'idioms',
        sa.Column('media_type', sa.String(20), nullable=True),
    )
    op.add_column(
        'grammar_questions',
        sa.Column('media_file', sa.String(255), nullable=True),
    )
    op.add_column(
        'grammar_questions',
        sa.Column('media_type', sa.String(20), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('grammar_questions', 'media_type')
    op.drop_column('grammar_questions', 'media_file')
    op.drop_column('idioms', 'media_type')
    op.drop_column('idioms', 'media_file')
