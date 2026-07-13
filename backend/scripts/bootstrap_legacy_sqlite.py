from __future__ import annotations

import sys
from pathlib import Path

# Make backend modules such as database.py importable when this file is
# executed directly with:
# python scripts/bootstrap_legacy_sqlite.py
BACKEND_ROOT = Path(__file__).resolve().parent.parent

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text

from database import engine


INITIAL_REVISION = "f9a575fbbce5"

EXPECTED_COLUMNS = {
    "products": {
        "id",
        "name",
        "brand",
        "price",
        "originalPrice",
        "image",
        "tags",
        "occasions",
        "budgetTier",
        "season",
    },
    "community_profiles": {
        "id",
        "name",
        "handle",
        "avatar",
        "role",
        "dna_json",
        "dna_label",
        "recent_purchases",
    },
}


def get_current_revision(connection) -> str | None:
    inspector = inspect(connection)

    if "alembic_version" not in inspector.get_table_names():
        return None

    return connection.execute(
        text("SELECT version_num FROM alembic_version LIMIT 1")
    ).scalar_one_or_none()


def validate_initial_schema(connection) -> None:
    inspector = inspect(connection)
    available_tables = set(inspector.get_table_names())

    expected_tables = set(EXPECTED_COLUMNS)
    existing_application_tables = available_tables & expected_tables

    if not existing_application_tables:
        # This is a fresh database. Alembic will create the schema.
        return

    if existing_application_tables != expected_tables:
        missing_tables = expected_tables - existing_application_tables

        raise RuntimeError(
            "Legacy database contains only part of the expected schema. "
            "Refusing to stamp it automatically. "
            f"Missing tables: {sorted(missing_tables)}"
        )

    for table_name, expected_columns in EXPECTED_COLUMNS.items():
        actual_columns = {
            column["name"]
            for column in inspector.get_columns(table_name)
        }

        if actual_columns != expected_columns:
            missing_columns = expected_columns - actual_columns
            unexpected_columns = actual_columns - expected_columns

            raise RuntimeError(
                f"Legacy table '{table_name}' does not match the "
                "initial migration.\n"
                f"Missing columns: {sorted(missing_columns)}\n"
                f"Unexpected columns: {sorted(unexpected_columns)}"
            )


def build_alembic_config() -> Config:
    alembic_config = Config(str(BACKEND_ROOT / "alembic.ini"))

    alembic_config.set_main_option(
        "script_location",
        str(BACKEND_ROOT / "alembic"),
    )

    return alembic_config


def main() -> None:
    if engine.dialect.name != "sqlite":
        print("Legacy bootstrap skipped: database is not SQLite.")
        return

    with engine.connect() as connection:
        current_revision = get_current_revision(connection)

        if current_revision:
            print(
                "Database already managed by Alembic: "
                f"{current_revision}"
            )
            return

        validate_initial_schema(connection)

        inspector = inspect(connection)
        existing_application_tables = (
            set(inspector.get_table_names()) & set(EXPECTED_COLUMNS)
        )

    if not existing_application_tables:
        print(
            "Fresh database detected. "
            "Alembic will create the schema."
        )
        return

    alembic_config = build_alembic_config()
    command.stamp(alembic_config, INITIAL_REVISION)

    print(
        "Compatible legacy SQLite schema stamped at "
        f"{INITIAL_REVISION}."
    )


if __name__ == "__main__":
    main()