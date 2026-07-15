from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from database import SessionLocal
from models import (
    Product,
    StyleProfile,
    User,
    UserEvent,
    UserPreference,
)

RANDOM_SEED = 20260714
BASE_TIME = datetime(
    2026,
    1,
    1,
    tzinfo=timezone.utc,
)
BACKEND_ROOT = Path(__file__).resolve().parent

AESTHETICS = [
    "minimalist",
    "streetwear",
    "y2k",
    "quiet_luxury",
    "bohemian",
    "athleisure",
]

COLOURS = [
    "black",
    "white",
    "grey",
    "beige",
    "blue",
    "green",
    "pink",
]

OCCASIONS = [
    "campus",
    "casual",
    "office",
    "party",
    "wedding",
    "travel",
]

EVENT_TYPES = [
    "view",
    "save",
    "wishlist",
    "cart_add",
    "purchase",
    "return",
    "keep",
]


def normalized_dna(
    rng: random.Random,
) -> dict[str, float]:
    selected = rng.sample(AESTHETICS, k=3)
    values = [rng.random() for _ in selected]
    total = sum(values)

    result = {
        label: round(value / total * 100, 2)
        for label, value in zip(
            selected,
            values,
            strict=True,
        )
    }

    difference = round(
        100 - sum(result.values()),
        2,
    )

    largest = max(result, key=result.get)
    result[largest] = round(
        result[largest] + difference,
        2,
    )

    return result


def load_products() -> list[dict]:
    path = (
        BACKEND_ROOT
        / "seed_data"
        / "products.json"
    )

    return json.loads(
        path.read_text(encoding="utf-8")
    )


def seed_products(
    db: Session,
) -> list[Product]:
    result: list[Product] = []

    for payload in load_products():
        product = (
            db.query(Product)
            .filter(Product.sku == payload["sku"])
            .first()
        )

        if product is None:
            product = Product(
                **payload,
            )
            db.add(product)
        else:
            for field, value in payload.items():
                setattr(product, field, value)

        result.append(product)

    db.flush()

    return result


def seed_demo_user(
    db: Session,
) -> User:
    user = (
        db.query(User)
        .filter(
            User.seed_key == "demo-user"
        )
        .first()
    )

    if user is None:
        user = User(
            seed_key="demo-user",
            name="Style Explorer",
            email="demo@myntra-identity.local",
            gender="women",
            age=20,
            onboarding_completed=False,
            is_synthetic=False,
        )
        db.add(user)
        db.flush()

    return user


def seed_synthetic_users(
    db: Session,
    rng: random.Random,
) -> list[User]:
    users: list[User] = []

    for index in range(1, 51):
        seed_key = (
            f"synthetic-user-{index:03d}"
        )

        user = (
            db.query(User)
            .filter(User.seed_key == seed_key)
            .first()
        )

        if user is None:
            user = User(
                seed_key=seed_key,
                name=f"Style User {index:03d}",
                email=(
                    f"style.user.{index:03d}"
                    "@example.local"
                ),
                gender=rng.choice(
                    ["women", "men", "unisex"]
                ),
                age=rng.randint(18, 32),
                onboarding_completed=True,
                is_synthetic=True,
            )
            db.add(user)
            db.flush()

        if user.preferences is None:
            preference = UserPreference(
                user_id=user.id,
                budget_min=rng.choice(
                    [500, 800, 1000, 1500]
                ),
                budget_max=rng.choice(
                    [2500, 3500, 5000, 8000]
                ),
                budget_tier=rng.choice(
                    [
                        "budget",
                        "mid_range",
                        "premium",
                    ]
                ),
                preferred_colours=rng.sample(
                    COLOURS,
                    k=3,
                ),
                preferred_occasions=rng.sample(
                    OCCASIONS,
                    k=3,
                ),
                preferred_aesthetics=rng.sample(
                    AESTHETICS,
                    k=2,
                ),
                preferred_brands=[],
                fit_preferences=[
                    rng.choice(
                        [
                            "relaxed",
                            "regular",
                            "fitted",
                        ]
                    )
                ],
                comfort_priority=round(
                    rng.uniform(0.3, 1),
                    2,
                ),
                trend_openness=round(
                    rng.uniform(0.1, 1),
                    2,
                ),
            )
            db.add(preference)

        style_profile = (
            db.query(StyleProfile)
            .filter(
                StyleProfile.user_id == user.id,
                StyleProfile.version == 1,
            )
            .first()
        )

        if style_profile is None:
            dna = normalized_dna(rng)
            ordered = sorted(
                dna,
                key=dna.get,
                reverse=True,
            )

            style_profile = StyleProfile(
                user_id=user.id,
                version=1,
                dna_vector=dna,
                primary_identity=ordered[0],
                secondary_identity=ordered[1],
                profile_confidence=round(
                    rng.uniform(60, 90),
                    2,
                ),
                source="synthetic_seed",
                model_version="dna-v1",
            )
            db.add(style_profile)

        users.append(user)

    db.flush()

    return users


def seed_events(
    db: Session,
    rng: random.Random,
    users: list[User],
    products: list[Product],
) -> None:
    # 50 users × 20 events = exactly 1,000 events.
    for user in users:
        for event_index in range(20):
            seed_key = (
                f"synthetic-event-"
                f"{user.seed_key}-"
                f"{event_index:02d}"
            )

            existing = (
                db.query(UserEvent)
                .filter(
                    UserEvent.seed_key == seed_key
                )
                .first()
            )

            if existing is not None:
                continue

            product = rng.choice(products)

            event_type = rng.choices(
                EVENT_TYPES,
                weights=[
                    35,
                    18,
                    14,
                    12,
                    10,
                    4,
                    7,
                ],
                k=1,
            )[0]

            event = UserEvent(
                seed_key=seed_key,
                user_id=user.id,
                product_id=product.id,
                event_type=event_type,
                event_metadata={
                    "source": "synthetic_seed",
                    "match_score": rng.randint(
                        45,
                        98,
                    ),
                },
                occurred_at=(
                    BASE_TIME
                    + timedelta(
                        days=rng.randint(0, 180),
                        minutes=rng.randint(
                            0,
                            1439,
                        ),
                    )
                ),
            )

            db.add(event)


def seed_database() -> None:
    rng = random.Random(RANDOM_SEED)
    db: Session = SessionLocal()

    try:
        products = seed_products(db)
        seed_demo_user(db)

        synthetic_users = seed_synthetic_users(
            db,
            rng,
        )

        seed_events(
            db,
            rng,
            synthetic_users,
            products,
        )

        db.commit()

        print(
            "Phase 2 seed completed safely."
        )
        print(
            f"Products: {len(products)}"
        )
        print(
            "Synthetic profiles: "
            f"{len(synthetic_users)}"
        )
        print(
            "Synthetic events: 1000"
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()