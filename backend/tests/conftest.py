import os
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parent.parent
TEST_DATABASE_PATH = BACKEND_ROOT / "test.db"

# These must be set before importing main, database or config.
os.environ["DATABASE_URL"] = (
    f"sqlite:///{TEST_DATABASE_PATH.resolve().as_posix()}"
)
os.environ["FRONTEND_ORIGINS"] = '["http://testserver"]'
os.environ["ENVIRONMENT"] = "test"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
def migrated_test_database():
    from alembic import command
    from alembic.config import Config

    TEST_DATABASE_PATH.unlink(missing_ok=True)

    alembic_config = Config(str(BACKEND_ROOT / "alembic.ini"))
    alembic_config.set_main_option(
        "script_location",
        str(BACKEND_ROOT / "alembic"),
    )

    command.upgrade(alembic_config, "head")

    yield

    TEST_DATABASE_PATH.unlink(missing_ok=True)