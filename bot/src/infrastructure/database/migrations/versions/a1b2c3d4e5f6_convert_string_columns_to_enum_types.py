"""convert string columns to enum types

Revision ID: a1b2c3d4e5f6
Revises: 9f5a66667685
Create Date: 2026-03-21 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '9f5a66667685'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Enum определения
topic_level = sa.Enum('beginner', 'intermediate', 'advanced', name='topiclevel')
game_session_status = sa.Enum('in_progress', 'completed', 'abandoned', name='gamesessionstatus')
test_type = sa.Enum('eng_level', 'vocabulary', 'idioms', name='testtype')


def upgrade() -> None:
    # 1. Создаём типы ENUM в PostgreSQL
    topic_level.create(op.get_bind(), checkfirst=True)
    game_session_status.create(op.get_bind(), checkfirst=True)
    test_type.create(op.get_bind(), checkfirst=True)

    # 2. educational_topics.level: VARCHAR → topiclevel
    op.alter_column(
        'educational_topics', 'level',
        type_=topic_level,
        existing_type=sa.String(length=50),
        existing_nullable=False,
        postgresql_using="level::topiclevel",
    )

    # 3. interactive_topics.level: VARCHAR → topiclevel
    op.alter_column(
        'interactive_topics', 'level',
        type_=topic_level,
        existing_type=sa.String(length=50),
        existing_nullable=True,
        postgresql_using="level::topiclevel",
    )

    # 4. game_sessions.status: VARCHAR → gamesessionstatus
    op.alter_column(
        'game_sessions', 'status',
        type_=game_session_status,
        existing_type=sa.String(length=20),
        existing_nullable=False,
        postgresql_using="status::gamesessionstatus",
    )

    # 5. test_results.test_type: VARCHAR → testtype
    op.alter_column(
        'test_results', 'test_type',
        type_=test_type,
        existing_type=sa.String(length=50),
        existing_nullable=False,
        postgresql_using="test_type::testtype",
    )


def downgrade() -> None:
    # Откат: ENUM → VARCHAR
    op.alter_column(
        'test_results', 'test_type',
        type_=sa.String(length=50),
        existing_type=test_type,
        existing_nullable=False,
        postgresql_using="test_type::text",
    )

    op.alter_column(
        'game_sessions', 'status',
        type_=sa.String(length=20),
        existing_type=game_session_status,
        existing_nullable=False,
        postgresql_using="status::text",
    )

    op.alter_column(
        'interactive_topics', 'level',
        type_=sa.String(length=50),
        existing_type=topic_level,
        existing_nullable=True,
        postgresql_using="level::text",
    )

    op.alter_column(
        'educational_topics', 'level',
        type_=sa.String(length=50),
        existing_type=topic_level,
        existing_nullable=False,
        postgresql_using="level::text",
    )

    # Удаляем типы ENUM
    test_type.drop(op.get_bind(), checkfirst=True)
    game_session_status.drop(op.get_bind(), checkfirst=True)
    topic_level.drop(op.get_bind(), checkfirst=True)
