"""add_user_game_threads_table

Revision ID: 21b98f40486f
Revises: 0627f99511d2
Create Date: 2026-04-08 02:24:44.734739

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21b98f40486f'
down_revision: Union[str, None] = '0627f99511d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_game_threads',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('game_type', sa.String(length=30), nullable=False),
        sa.Column('thread_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'game_type', name='uq_user_game_thread'),
    )
    op.create_index(
        op.f('ix_user_game_threads_user_id'),
        'user_game_threads',
        ['user_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix_user_game_threads_user_id'),
        table_name='user_game_threads',
    )
    op.drop_table('user_game_threads')
