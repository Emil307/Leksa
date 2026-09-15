"""add_level_to_grammar_questions

Revision ID: 0627f99511d2
Revises: b2c3d4e5f6a7
Create Date: 2026-03-29 01:06:38.975311

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0627f99511d2'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'grammar_questions',
        sa.Column('level', sa.String(20), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('grammar_questions', 'level')
