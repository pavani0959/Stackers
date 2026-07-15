"""enforce product catalog fields not null

Revision ID: df221ccca24f
Revises: 4a6069fafba2
Create Date: 2026-07-14 04:52:53.241735

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df221ccca24f'
down_revision: Union[str, Sequence[str], None] = '4a6069fafba2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


"""enforce product catalog fields not null"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # Protect existing databases that may contain older nullable rows.
    op.execute(
        sa.text(
            """
            UPDATE products
            SET sku = 'legacy-' || CAST(id AS TEXT)
            WHERE sku IS NULL OR TRIM(sku) = ''
            """
        )
    )

    op.execute(
        sa.text(
            """
            UPDATE products
            SET category = 'uncategorized'
            WHERE category IS NULL OR TRIM(category) = ''
            """
        )
    )

    op.execute(
        sa.text(
            """
            UPDATE products
            SET subcategory = 'uncategorized'
            WHERE subcategory IS NULL OR TRIM(subcategory) = ''
            """
        )
    )

    op.execute(
        sa.text(
            """
            UPDATE products
            SET primary_colour = 'unknown'
            WHERE primary_colour IS NULL OR TRIM(primary_colour) = ''
            """
        )
    )

    op.execute(
        sa.text(
            """
            UPDATE products
            SET gender_segment = 'unisex'
            WHERE gender_segment IS NULL OR TRIM(gender_segment) = ''
            """
        )
    )

    # Batch mode recreates the table safely on SQLite.
    with op.batch_alter_table("products") as batch_op:
        batch_op.alter_column(
            "sku",
            existing_type=sa.String(length=64),
            nullable=False,
        )
        batch_op.alter_column(
            "category",
            existing_type=sa.String(length=50),
            nullable=False,
        )
        batch_op.alter_column(
            "subcategory",
            existing_type=sa.String(length=80),
            nullable=False,
        )
        batch_op.alter_column(
            "primary_colour",
            existing_type=sa.String(length=40),
            nullable=False,
        )
        batch_op.alter_column(
            "gender_segment",
            existing_type=sa.String(length=30),
            nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("products") as batch_op:
        batch_op.alter_column(
            "gender_segment",
            existing_type=sa.String(length=30),
            nullable=True,
        )
        batch_op.alter_column(
            "primary_colour",
            existing_type=sa.String(length=40),
            nullable=True,
        )
        batch_op.alter_column(
            "subcategory",
            existing_type=sa.String(length=80),
            nullable=True,
        )
        batch_op.alter_column(
            "category",
            existing_type=sa.String(length=50),
            nullable=True,
        )
        batch_op.alter_column(
            "sku",
            existing_type=sa.String(length=64),
            nullable=True,
        )