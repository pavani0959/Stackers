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
        # Seed the generated catalogue into the
        # isolated pytest database. Running
        # `python seed.py` only updates the
        # development database.
        from seed import seed_products

        seeded_products = seed_products(db)

        if len(seeded_products) != 120:
            raise AssertionError(
                "Expected 120 products in the "
                "pytest catalogue, but seeded "
                f"{len(seeded_products)}."
            )

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
# Reverse Shopping server-profile fixture
@pytest.fixture(autouse=True)
def seed_reverse_server_profile(request):
    """Create server-owned identity data for reverse tests."""

    reverse_test_files = {
        "test_fastapi_reverse.py",
        "test_phase5_reverse_shopping.py",
    }

    if request.node.path.name not in reverse_test_files:
        yield
        return

    from config import get_settings
    from database import SessionLocal

    import models

    settings = get_settings()
    db = SessionLocal()

    try:
        user = (
            db.query(models.User)
            .filter(
                models.User.id
                == settings.demo_user_id
            )
            .first()
        )

        if user is None:
            raise AssertionError(
                "The test database does not contain "
                "the configured demo user."
            )

        user.onboarding_completed = True

        preferences = (
            db.query(models.UserPreference)
            .filter(
                models.UserPreference.user_id
                == user.id
            )
            .first()
        )

        if preferences is None:
            preferences = models.UserPreference(
                user_id=user.id,
                budget_min=500,
                budget_max=3000,
                budget_tier="campus-casual",
                preferred_colours=[
                    "black",
                    "white",
                    "beige",
                ],
                preferred_brands=[],
                preferred_occasions=[
                    "interview",
                    "office",
                    "campus",
                ],
                preferred_aesthetics=[
                    "minimalist",
                    "quietLuxury",
                ],
                fit_preferences=[
                    "regular",
                    "relaxed",
                ],
                comfort_priority=0.7,
                trend_openness=0.3,
                fashion_goal="smart-shopping",
                comfort_expression_balance=0.5,
                occasion_priorities={
                    "interview": 1.0,
                    "office": 0.9,
                    "campus": 0.8,
                },
            )

            db.add(preferences)
        else:
            preferences.budget_min = 500
            preferences.budget_max = 3000
            preferences.budget_tier = (
                "campus-casual"
            )
            preferences.preferred_occasions = [
                "interview",
                "office",
                "campus",
            ]
            preferences.preferred_aesthetics = [
                "minimalist",
                "quietLuxury",
            ]

        style_profile = (
            db.query(models.StyleProfile)
            .filter(
                models.StyleProfile.user_id
                == user.id
            )
            .order_by(
                models.StyleProfile.version.desc()
            )
            .first()
        )

        if style_profile is None:
            from uuid import uuid4

            style_profile = models.StyleProfile(
                profile_id=uuid4(),
                user_id=user.id,
                version=1,
                dna_vector={
                    "minimalist": 70,
                    "quietLuxury": 20,
                    "campusCasual": 10,
                },
                primary_identity=(
                    "Quiet Luxury Minimalist"
                ),
                secondary_identity=(
                    "Campus Minimalist"
                ),
                profile_confidence=90,
                source="pytest",
                model_version="test-v1.0.0",
                identity={
                    "name": (
                        "Quiet Luxury Minimalist"
                    ),
                    "description": (
                        "A clean, professional and "
                        "budget-aware test identity."
                    ),
                },
                confidence_breakdown={
                    "quiz_completeness": 40,
                    "answer_consistency": 25,
                    "preference_coverage": 20,
                    "behavior_evidence": 5,
                },
                evidence={
                    "source": "pytest",
                    "answer_count": 8,
                },
            )

            db.add(style_profile)

        if style_profile.profile_id is None:
            from uuid import uuid4

            style_profile.profile_id = uuid4()

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

    yield

    # Clean Reverse Shopping test records so
    # later test modules start with an isolated
    # profile state.
    cleanup_db = SessionLocal()

    try:
        session_ids = [
            session_id
            for (session_id,) in (
                cleanup_db.query(
                    models.RecommendationSession.id
                )
                .filter(
                    models.RecommendationSession.user_id
                    == settings.demo_user_id
                )
                .all()
            )
        ]

        if session_ids:
            (
                cleanup_db.query(
                    models.RecommendationItem
                )
                .filter(
                    models.RecommendationItem.session_id.in_(
                        session_ids
                    )
                )
                .delete(
                    synchronize_session=False
                )
            )

            (
                cleanup_db.query(
                    models.RecommendationSession
                )
                .filter(
                    models.RecommendationSession.id.in_(
                        session_ids
                    )
                )
                .delete(
                    synchronize_session=False
                )
            )

        (
            cleanup_db.query(
                models.StyleProfile
            )
            .filter(
                models.StyleProfile.user_id
                == settings.demo_user_id,
                models.StyleProfile.source
                == "pytest",
                models.StyleProfile.model_version
                == "test-v1.0.0",
            )
            .delete(
                synchronize_session=False
            )
        )

        cleanup_db.commit()

    except Exception:
        cleanup_db.rollback()
        raise

    finally:
        cleanup_db.close()

