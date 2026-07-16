"""add immutable decision snapshots

Revision ID: a66d2cc193f6
Revises: e5d4e4c23f42
Create Date: 2026-07-16 15:47:48.866535

"""

from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a66d2cc193f6"
down_revision: Union[str, Sequence[str], None] = "e5d4e4c23f42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add and backfill immutable decision snapshot fields."""

    # ------------------------------------------------------------------
    # 1. Add all new columns as nullable first.
    #
    # Existing rows do not yet have values for these columns, so adding
    # them as NOT NULL immediately would make the migration fail.
    # ------------------------------------------------------------------

    op.add_column(
        "recommendation_sessions",
        sa.Column(
            "profile_version",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "recommendation_sessions",
        sa.Column(
            "profile_snapshot",
            sa.JSON(),
            nullable=True,
        ),
    )

    op.add_column(
        "recommendation_sessions",
        sa.Column(
            "context_snapshot",
            sa.JSON(),
            nullable=True,
        ),
    )

    op.add_column(
        "recommendation_items",
        sa.Column(
            "snapshot_id",
            sa.Uuid(),
            nullable=True,
        ),
    )

    op.add_column(
        "recommendation_items",
        sa.Column(
            "product_snapshot",
            sa.JSON(),
            nullable=True,
        ),
    )

    op.add_column(
        "recommendation_items",
        sa.Column(
            "evidence_sources",
            sa.JSON(),
            nullable=True,
        ),
    )

    op.add_column(
        "recommendation_items",
        sa.Column(
            "regret_signals",
            sa.JSON(),
            nullable=True,
        ),
    )

    # ------------------------------------------------------------------
    # 2. Define lightweight tables for data backfilling.
    #
    # These are migration-only table definitions. Do not import ORM
    # models inside an Alembic migration because models may change later.
    # ------------------------------------------------------------------

    recommendation_sessions = sa.table(
        "recommendation_sessions",
        sa.column(
            "id",
            sa.Integer(),
        ),
        sa.column(
            "profile_version",
            sa.Integer(),
        ),
        sa.column(
            "profile_snapshot",
            sa.JSON(),
        ),
        sa.column(
            "context_snapshot",
            sa.JSON(),
        ),
    )

    recommendation_items = sa.table(
        "recommendation_items",
        sa.column(
            "id",
            sa.Integer(),
        ),
        sa.column(
            "product_id",
            sa.Integer(),
        ),
        sa.column(
            "snapshot_id",
            sa.Uuid(),
        ),
        sa.column(
            "product_snapshot",
            sa.JSON(),
        ),
        sa.column(
            "evidence_sources",
            sa.JSON(),
        ),
        sa.column(
            "regret_signals",
            sa.JSON(),
        ),
    )

    products = sa.table(
        "products",
        sa.column(
            "id",
            sa.Integer(),
        ),
        sa.column(
            "sku",
            sa.String(length=64),
        ),
        sa.column(
            "name",
            sa.String(),
        ),
        sa.column(
            "brand",
            sa.String(),
        ),
        sa.column(
            "description",
            sa.Text(),
        ),
        sa.column(
            "price",
            sa.Float(),
        ),
        sa.column(
            "originalPrice",
            sa.Float(),
        ),
        sa.column(
            "image",
            sa.Text(),
        ),
        sa.column(
            "category",
            sa.String(length=50),
        ),
        sa.column(
            "subcategory",
            sa.String(length=80),
        ),
        sa.column(
            "primary_colour",
            sa.String(length=40),
        ),
        sa.column(
            "tags",
            sa.JSON(),
        ),
        sa.column(
            "occasions",
            sa.JSON(),
        ),
        sa.column(
            "budgetTier",
            sa.String(),
        ),
        sa.column(
            "season",
            sa.String(),
        ),
    )

    bind = op.get_bind()

    # ------------------------------------------------------------------
    # 3. Backfill old recommendation sessions.
    #
    # Existing recommendation rows were created before immutable profile
    # snapshots existed, so version 0 identifies them as legacy records.
    # ------------------------------------------------------------------

    bind.execute(
        recommendation_sessions.update().values(
            profile_version=0,
            profile_snapshot={},
            context_snapshot={},
        ),
    )

    # ------------------------------------------------------------------
    # 4. Load every existing recommendation item and its current product.
    #
    # Each old recommendation item receives:
    # - its own UUID
    # - a product snapshot
    # - empty evidence sources
    # - an empty regret signal list
    # ------------------------------------------------------------------

    existing_items = bind.execute(
        sa.select(
            recommendation_items.c.id.label(
                "recommendation_item_id",
            ),
            products.c.id.label(
                "product_id",
            ),
            products.c.sku,
            products.c.name,
            products.c.brand,
            products.c.description,
            products.c.price,
            products.c.originalPrice,
            products.c.image,
            products.c.category,
            products.c.subcategory,
            products.c.primary_colour,
            products.c.tags,
            products.c.occasions,
            products.c.budgetTier,
            products.c.season,
        ).select_from(
            recommendation_items.join(
                products,
                recommendation_items.c.product_id
                == products.c.id,
            ),
        ),
    ).mappings().all()

    for row in existing_items:
        product_snapshot = {
            "id": row["product_id"],
            "sku": row["sku"],
            "name": row["name"],
            "brand": row["brand"],
            "description": row["description"],
            "price": row["price"],
            "originalPrice": row["originalPrice"],
            "image": row["image"],
            "category": row["category"],
            "subcategory": row["subcategory"],
            "primary_colour": row["primary_colour"],
            "tags": row["tags"] or [],
            "occasions": row["occasions"] or [],
            "budgetTier": row["budgetTier"],
            "season": row["season"],
        }

        bind.execute(
            recommendation_items.update()
            .where(
                recommendation_items.c.id
                == row["recommendation_item_id"],
            )
            .values(
                snapshot_id=uuid4(),
                product_snapshot=product_snapshot,
                evidence_sources={},
                regret_signals=[],
            ),
        )

    # ------------------------------------------------------------------
    # 5. Enforce NOT NULL only after every existing row is populated.
    # ------------------------------------------------------------------

    with op.batch_alter_table(
        "recommendation_sessions",
        schema=None,
    ) as batch_op:
        batch_op.alter_column(
            "profile_version",
            existing_type=sa.Integer(),
            nullable=False,
        )

        batch_op.alter_column(
            "profile_snapshot",
            existing_type=sa.JSON(),
            nullable=False,
        )

        batch_op.alter_column(
            "context_snapshot",
            existing_type=sa.JSON(),
            nullable=False,
        )

    with op.batch_alter_table(
        "recommendation_items",
        schema=None,
    ) as batch_op:
        batch_op.alter_column(
            "snapshot_id",
            existing_type=sa.Uuid(),
            nullable=False,
        )

        batch_op.alter_column(
            "product_snapshot",
            existing_type=sa.JSON(),
            nullable=False,
        )

        batch_op.alter_column(
            "evidence_sources",
            existing_type=sa.JSON(),
            nullable=False,
        )

        batch_op.alter_column(
            "regret_signals",
            existing_type=sa.JSON(),
            nullable=False,
        )

        # Create the unique index only after every old row has received
        # a distinct UUID.
        batch_op.create_index(
            "ix_recommendation_items_snapshot_id",
            ["snapshot_id"],
            unique=True,
        )


def downgrade() -> None:
    """Remove immutable decision snapshot fields."""

    with op.batch_alter_table(
        "recommendation_items",
        schema=None,
    ) as batch_op:
        batch_op.drop_index(
            "ix_recommendation_items_snapshot_id",
        )

        batch_op.drop_column(
            "regret_signals",
        )

        batch_op.drop_column(
            "evidence_sources",
        )

        batch_op.drop_column(
            "product_snapshot",
        )

        batch_op.drop_column(
            "snapshot_id",
        )

    with op.batch_alter_table(
        "recommendation_sessions",
        schema=None,
    ) as batch_op:
        batch_op.drop_column(
            "context_snapshot",
        )

        batch_op.drop_column(
            "profile_snapshot",
        )

        batch_op.drop_column(
            "profile_version",
        )