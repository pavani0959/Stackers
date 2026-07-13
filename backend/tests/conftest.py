from __future__ import annotations

import os
from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parent.parent
TEST_DATABASE_PATH = BACKEND_ROOT / "test.db"
TEST_DATABASE_URL = (
    f"sqlite:///{TEST_DATABASE_PATH.resolve().as_posix()}"
)

# These variables must be configured before importing anything
# that initializes application settings or the SQLAlchemy engine.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["FRONTEND_ORIGINS"] = '["http://testserver"]'
os.environ["ENVIRONMENT"] = "test"
os.environ["DEMO_USER_ID"] = "1"


# Clear cached settings in case config was imported before pytest
# completed loading this conftest file.
from config import get_settings

get_settings.cache_clear()


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
def migrated_test_database():
    """
    Create a fresh migrated SQLite database for each pytest session.

    The database is removed before and after the test session so stale
    records cannot cause primary-key or unique-constraint failures.
    """
    from alembic import command
    from alembic.config import Config

    # Import these only after DATABASE_URL has been configured.
    from database import SessionLocal, engine
    from models import User

    # Close existing SQLite connections before deleting the database.
    engine.dispose()
    TEST_DATABASE_PATH.unlink(missing_ok=True)

    alembic_config = Config(
        str(BACKEND_ROOT / "alembic.ini")
    )

    alembic_config.set_main_option(
        "script_location",
        str(BACKEND_ROOT / "alembic"),
    )

    alembic_config.set_main_option(
        "sqlalchemy.url",
        TEST_DATABASE_URL,
    )

    command.upgrade(
        alembic_config,
        "head",
    )

    db = SessionLocal()

    try:
        demo_user = User(
            id=1,
            seed_key="test-demo-user",
            name="Test User",
            email="test@example.com",
            gender="women",
            age=20,
            onboarding_completed=False,
            is_synthetic=False,
        )

        db.add(demo_user)
        db.commit()

        created_user = db.get(User, 1)

        if created_user is None:
            raise RuntimeError(
                "Failed to create demo user in test database."
            )
    finally:
        db.close()

    yield

    engine.dispose()
    TEST_DATABASE_PATH.unlink(missing_ok=True)