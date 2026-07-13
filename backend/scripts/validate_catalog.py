import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_ROOT.parent

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from catalog_taxonomy import (
    GENDER_SEGMENTS,
    PRODUCT_CATEGORIES,
    PRODUCT_COLOURS,
    PRODUCT_OCCASIONS,
    PRODUCT_SEASONS,
    PRODUCT_SUBCATEGORIES,
)


def fail(message: str) -> None:
    raise ValueError(message)


def main() -> None:
    catalog_path = (
        BACKEND_ROOT
        / "seed_data"
        / "products.json"
    )

    products = json.loads(
        catalog_path.read_text(encoding="utf-8")
    )

    if not 100 <= len(products) <= 150:
        fail(
            "The catalogue must contain between "
            "100 and 150 products."
        )

    seen_skus: set[str] = set()

    for product in products:
        sku = product["sku"]

        if sku in seen_skus:
            fail(f"Duplicate SKU: {sku}")

        seen_skus.add(sku)

        category = product["category"]
        subcategory = product["subcategory"]

        if category not in PRODUCT_CATEGORIES:
            fail(
                f"{sku}: invalid category '{category}'"
            )

        if (
            subcategory
            not in PRODUCT_SUBCATEGORIES[category]
        ):
            fail(
                f"{sku}: invalid subcategory "
                f"'{subcategory}' for '{category}'"
            )

        if (
            product["primary_colour"]
            not in PRODUCT_COLOURS
        ):
            fail(
                f"{sku}: invalid primary colour"
            )

        if (
            product["gender_segment"]
            not in GENDER_SEGMENTS
        ):
            fail(
                f"{sku}: invalid gender segment"
            )

        if product["season"] not in PRODUCT_SEASONS:
            fail(f"{sku}: invalid season")

        invalid_occasions = (
            set(product["occasions"])
            - PRODUCT_OCCASIONS
        )

        if invalid_occasions:
            fail(
                f"{sku}: invalid occasions "
                f"{sorted(invalid_occasions)}"
            )

        if not product["tags"]:
            fail(f"{sku}: tags cannot be empty")

        if not product["sizes"]:
            fail(f"{sku}: sizes cannot be empty")

        image = product["image"]

        if image.startswith("/catalog/"):
            image_path = (
                PROJECT_ROOT
                / "public"
                / image.removeprefix("/")
            )

            if not image_path.exists():
                fail(
                    f"{sku}: missing image "
                    f"{image_path}"
                )

    print(
        f"Catalog validation passed: "
        f"{len(products)} products."
    )


if __name__ == "__main__":
    main()