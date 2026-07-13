from __future__ import annotations

from typing import Any

from database import SessionLocal
from models import (
    Product,
    StyleProfile,
    User,
    UserEvent,
    UserPreference,
)
from seed import load_products, seed_database


EXPECTED_SYNTHETIC_USERS = 50
EXPECTED_SYNTHETIC_EVENTS = 1_000

SENTINEL_SEED_KEY = "sentinel-user"
SENTINEL_EMAIL = "sentinel@example.com"

IMAGE_FIELD_CANDIDATES = (
    "image",
    "image_url",
    "images",
    "image_urls",
)


def get_database_counts() -> dict[str, int]:
    """Return counts for every table populated by the seed."""

    db = SessionLocal()

    try:
        return {
            "products": db.query(Product).count(),
            "users": db.query(User).count(),
            "preferences": db.query(UserPreference).count(),
            "style_profiles": db.query(StyleProfile).count(),
            "events": db.query(UserEvent).count(),
        }
    finally:
        db.close()


def delete_sentinel_user() -> None:
    """Remove only the sentinel created by this test."""

    db = SessionLocal()

    try:
        sentinel = (
            db.query(User)
            .filter(
                User.seed_key == SENTINEL_SEED_KEY
            )
            .first()
        )

        if sentinel is not None:
            db.delete(sentinel)
            db.commit()
    finally:
        db.close()


def get_image_value(product: Product) -> Any:
    """
    Find the image field used by the Product model.

    This supports common names such as image and image_url.
    """

    for field_name in IMAGE_FIELD_CANDIDATES:
        if hasattr(product, field_name):
            return getattr(product, field_name)

    raise AssertionError(
        "Product has no supported image field. Expected one of: "
        + ", ".join(IMAGE_FIELD_CANDIDATES)
    )


def assert_non_empty_collection(
    value: Any,
    field_name: str,
    product: Product,
) -> None:
    """Verify that a JSON/list product field contains useful values."""

    assert isinstance(value, (list, tuple)), (
        f"Product {product.sku!r} field {field_name!r} "
        f"must be a list, but received {type(value).__name__}"
    )

    assert len(value) > 0, (
        f"Product {product.sku!r} must have at least one "
        f"{field_name.rstrip('s')}"
    )

    assert all(
        isinstance(item, str) and item.strip()
        for item in value
    ), (
        f"Product {product.sku!r} contains an empty or invalid "
        f"value in {field_name!r}"
    )


def assert_non_empty_image(
    image_value: Any,
    product: Product,
) -> None:
    """Validate either a single image URL or a list of image URLs."""

    if isinstance(image_value, str):
        assert image_value.strip(), (
            f"Product {product.sku!r} has an empty image"
        )
        return

    if isinstance(image_value, (list, tuple)):
        assert image_value, (
            f"Product {product.sku!r} has no images"
        )

        assert all(
            isinstance(image, str) and image.strip()
            for image in image_value
        ), (
            f"Product {product.sku!r} contains an empty "
            "or invalid image"
        )
        return

    raise AssertionError(
        f"Product {product.sku!r} has an invalid image value: "
        f"{image_value!r}"
    )


def test_running_seed_twice_does_not_increase_counts():
    seed_database()
    counts_after_first_run = get_database_counts()

    seed_database()
    counts_after_second_run = get_database_counts()

    assert counts_after_second_run == counts_after_first_run, (
        "Running seed_database() twice changed database counts.\n"
        f"First run: {counts_after_first_run}\n"
        f"Second run: {counts_after_second_run}"
    )


def test_seed_creates_exactly_50_synthetic_users():
    seed_database()

    db = SessionLocal()

    try:
        synthetic_user_count = (
            db.query(User)
            .filter(User.is_synthetic.is_(True))
            .count()
        )

        assert synthetic_user_count == EXPECTED_SYNTHETIC_USERS
    finally:
        db.close()


def test_seed_creates_exactly_1000_synthetic_events():
    seed_database()

    db = SessionLocal()

    try:
        synthetic_event_count = (
            db.query(UserEvent)
            .filter(
                UserEvent.seed_key.like(
                    "synthetic-event-%"
                )
            )
            .count()
        )

        assert synthetic_event_count == EXPECTED_SYNTHETIC_EVENTS
    finally:
        db.close()


def test_every_product_has_valid_category_and_subcategory():
    seed_database()

    product_payloads = load_products()

    assert product_payloads, (
        "seed_data/products.json must not be empty"
    )

    valid_categories = {
        payload["category"]
        for payload in product_payloads
    }

    valid_category_subcategory_pairs = {
        (
            payload["category"],
            payload["subcategory"],
        )
        for payload in product_payloads
    }

    db = SessionLocal()

    try:
        products = db.query(Product).all()

        assert products, (
            "The seed must create at least one product"
        )

        for product in products:
            assert product.category, (
                f"Product {product.sku!r} has an empty category"
            )

            assert product.category in valid_categories, (
                f"Product {product.sku!r} has invalid category "
                f"{product.category!r}"
            )

            assert product.subcategory, (
                f"Product {product.sku!r} has an empty subcategory"
            )

            pair = (
                product.category,
                product.subcategory,
            )

            assert pair in valid_category_subcategory_pairs, (
                f"Product {product.sku!r} has invalid "
                f"category/subcategory combination: {pair!r}"
            )
    finally:
        db.close()


def test_every_product_has_required_metadata():
    seed_database()

    db = SessionLocal()

    try:
        products = db.query(Product).all()

        assert products, (
            "The seed must create at least one product"
        )

        for product in products:
            assert_non_empty_collection(
                product.sizes,
                "sizes",
                product,
            )

            assert_non_empty_collection(
                product.occasions,
                "occasions",
                product,
            )

            assert_non_empty_image(
                get_image_value(product),
                product,
            )
    finally:
        db.close()


def test_seed_preserves_unrelated_user():
    """
    Critical safety test.

    Reseeding must not delete or overwrite a normal unrelated user.
    """

    delete_sentinel_user()

    creation_db = SessionLocal()

    try:
        sentinel = User(
            seed_key=SENTINEL_SEED_KEY,
            name="Sentinel",
            email=SENTINEL_EMAIL,
            gender="women",
            age=25,
            onboarding_completed=True,
            is_synthetic=False,
        )

        creation_db.add(sentinel)
        creation_db.commit()
    finally:
        # seed_database() creates its own SQLAlchemy session.
        # Close this session before calling it.
        creation_db.close()

    try:
        seed_database()

        verification_db = SessionLocal()

        try:
            preserved = (
                verification_db.query(User)
                .filter(
                    User.seed_key
                    == SENTINEL_SEED_KEY
                )
                .first()
            )

            assert preserved is not None, (
                "The unrelated sentinel user was deleted "
                "during reseeding"
            )

            assert preserved.name == "Sentinel"
            assert preserved.email == SENTINEL_EMAIL
            assert preserved.gender == "women"
            assert preserved.age == 25
            assert preserved.onboarding_completed is True
            assert preserved.is_synthetic is False
        finally:
            verification_db.close()
    finally:
        delete_sentinel_user()