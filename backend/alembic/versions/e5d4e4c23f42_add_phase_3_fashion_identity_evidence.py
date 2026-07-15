"""add phase 3 fashion identity evidence

Revision ID: e5d4e4c23f42
Revises: df221ccca24f
Create Date: 2026-07-15 23:23:43.301044

"""
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5d4e4c23f42'
down_revision: Union[str, Sequence[str], None] = 'df221ccca24f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_preferences",
        sa.Column(
            "fashion_goal",
            sa.String(length=80),
            nullable=True,
        ),
    )
    op.add_column(
        "user_preferences",
        sa.Column(
            "comfort_expression_balance",
            sa.Float(),
            nullable=False,
            server_default="0.5",
        ),
    )
    op.add_column(
        "user_preferences",
        sa.Column(
            "occasion_priorities",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
    )

    op.add_column(
        "style_profiles",
        sa.Column(
            "profile_id",
            sa.Uuid(),
            nullable=True,
        ),
    )
    op.add_column(
        "style_profiles",
        sa.Column(
            "identity",
            sa.JSON(),
            nullable=True,
        ),
    )
    op.add_column(
        "style_profiles",
        sa.Column(
            "confidence_breakdown",
            sa.JSON(),
            nullable=True,
        ),
    )
    op.add_column(
        "style_profiles",
        sa.Column(
            "evidence",
            sa.JSON(),
            nullable=True,
        ),
    )

    style_profiles = sa.table(
        "style_profiles",
        sa.column("id", sa.Integer()),
        sa.column("profile_id", sa.Uuid()),
        sa.column("primary_identity", sa.String()),
        sa.column("secondary_identity", sa.String()),
        sa.column("identity", sa.JSON()),
        sa.column(
            "confidence_breakdown",
            sa.JSON(),
        ),
        sa.column("evidence", sa.JSON()),
    )

    bind = op.get_bind()

    rows = bind.execute(
        sa.select(
            style_profiles.c.id,
            style_profiles.c.primary_identity,
            style_profiles.c.secondary_identity,
        ),
    ).all()

    for row in rows:
        primary = (
            row.primary_identity
            or "Style Explorer"
        )

        bind.execute(
            style_profiles.update()
            .where(
                style_profiles.c.id == row.id,
            )
            .values(
                profile_id=uuid4(),
                identity={
                    "name": primary,
                    "description": "",
                    "primary": primary,
                    "secondary": (
                        row.secondary_identity
                    ),
                },
                confidence_breakdown={
                    "quiz_completeness": 0,
                    "answer_consistency": 0,
                    "preference_coverage": 0,
                    "behavior_evidence": 0,
                },
                evidence={
                    "quiz_answers": 0,
                    "behavior_events": 0,
                },
            ),
        )

    with op.batch_alter_table(
        "style_profiles",
    ) as batch_op:
        batch_op.alter_column(
            "profile_id",
            existing_type=sa.Uuid(),
            nullable=False,
        )
        batch_op.alter_column(
            "identity",
            existing_type=sa.JSON(),
            nullable=False,
        )
        batch_op.alter_column(
            "confidence_breakdown",
            existing_type=sa.JSON(),
            nullable=False,
        )
        batch_op.alter_column(
            "evidence",
            existing_type=sa.JSON(),
            nullable=False,
        )

        batch_op.create_index(
            "ix_style_profiles_profile_id",
            ["profile_id"],
            unique=True,
        )


def downgrade() -> None:
    with op.batch_alter_table(
        "style_profiles",
    ) as batch_op:
        batch_op.drop_index(
            "ix_style_profiles_profile_id",
        )

    op.drop_column(
        "style_profiles",
        "evidence",
    )
    op.drop_column(
        "style_profiles",
        "confidence_breakdown",
    )
    op.drop_column(
        "style_profiles",
        "identity",
    )
    op.drop_column(
        "style_profiles",
        "profile_id",
    )

    op.drop_column(
        "user_preferences",
        "occasion_priorities",
    )
    op.drop_column(
        "user_preferences",
        "comfort_expression_balance",
    )
    op.drop_column(
        "user_preferences",
        "fashion_goal",
    )
