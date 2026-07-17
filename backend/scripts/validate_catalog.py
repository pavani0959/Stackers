import json
import sys
from collections import Counter
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


MINIMUM_CATEGORY_COUNTS = {
    "top": 20,
    "bottom": 18,
    "dress": 12,
    "outerwear": 8,
    "footwear": 15,
    "accessory": 20,
    "ethnic_set": 8,
}


def fail(message: str) -> None:
    raise ValueError(message)


def main() -> None:
    catalog_path = (
        BACKEND_ROOT
        / "seed_data"
        / "products.json"
    )

    if not catalog_path.exists():
        fail(
            f"Catalogue file does not exist: "
            f"{catalog_path}"
        )

    try:
        products = json.loads(
            catalog_path.read_text(
                encoding="utf-8",
            )
        )
    except json.JSONDecodeError as error:
        fail(
            "products.json contains invalid JSON: "
            f"{error}"
        )

    if not isinstance(products, list):
        fail(
            "The catalogue root must be a JSON array."
        )

    if not 100 <= len(products) <= 150:
        fail(
            "The catalogue must contain between "
            "100 and 150 products; found "
            f"{len(products)}."
        )

    # Validate the minimum number of products
    # required in every important category.
    category_counts = Counter(
        product.get("category")
        for product in products
    )

    for (
        category,
        minimum,
    ) in MINIMUM_CATEGORY_COUNTS.items():
        actual = category_counts.get(
            category,
            0,
        )

        if actual < minimum:
            fail(
                f"Category '{category}' requires "
                f"at least {minimum} products; "
                f"found {actual}."
            )

    # Every product should use its own image.
    image_counts = Counter(
        product.get("image")
        for product in products
    )

    duplicate_images = {
        image: count
        for image, count in image_counts.items()
        if image and count > 1
    }

    if duplicate_images:
        examples = list(
            duplicate_images.items()
        )[:10]

        fail(
            "Catalogue images must not be reused. "
            f"Duplicate examples: {examples}"
        )

    seen_skus: set[str] = set()

    required_fields = {
        "sku",
        "name",
        "category",
        "subcategory",
        "primary_colour",
        "gender_segment",
        "season",
        "occasions",
        "tags",
        "sizes",
        "image",
    }

    for index, product in enumerate(
        products,
        start=1,
    ):
        if not isinstance(product, dict):
            fail(
                f"Product at position {index} "
                "must be a JSON object."
            )

        missing_fields = (
            required_fields
            - set(product)
        )

        if missing_fields:
            fail(
                f"Product at position {index} "
                "is missing required fields: "
                f"{sorted(missing_fields)}"
            )

        sku = product["sku"]

        if not isinstance(sku, str) or not sku.strip():
            fail(
                f"Product at position {index} "
                "has an invalid SKU."
            )

        if sku in seen_skus:
            fail(
                f"Duplicate SKU: {sku}"
            )

        seen_skus.add(sku)

        category = product["category"]
        subcategory = product["subcategory"]

        if category not in PRODUCT_CATEGORIES:
            fail(
                f"{sku}: invalid category "
                f"'{category}'"
            )

        valid_subcategories = (
            PRODUCT_SUBCATEGORIES.get(
                category,
                set(),
            )
        )

        if subcategory not in valid_subcategories:
            fail(
                f"{sku}: invalid subcategory "
                f"'{subcategory}' for "
                f"'{category}'"
            )

        primary_colour = product[
            "primary_colour"
        ]

        if primary_colour not in PRODUCT_COLOURS:
            fail(
                f"{sku}: invalid primary colour "
                f"'{primary_colour}'"
            )

        gender_segment = product[
            "gender_segment"
        ]

        if gender_segment not in GENDER_SEGMENTS:
            fail(
                f"{sku}: invalid gender segment "
                f"'{gender_segment}'"
            )

        season = product["season"]

        if season not in PRODUCT_SEASONS:
            fail(
                f"{sku}: invalid season "
                f"'{season}'"
            )

        occasions = product["occasions"]

        if not isinstance(occasions, list):
            fail(
                f"{sku}: occasions must be a list."
            )

        invalid_occasions = (
            set(occasions)
            - PRODUCT_OCCASIONS
        )

        if invalid_occasions:
            fail(
                f"{sku}: invalid occasions "
                f"{sorted(invalid_occasions)}"
            )

        tags = product["tags"]

        if (
            not isinstance(tags, list)
            or not tags
        ):
            fail(
                f"{sku}: tags must be "
                "a non-empty list."
            )

        sizes = product["sizes"]

        if (
            not isinstance(sizes, list)
            or not sizes
        ):
            fail(
                f"{sku}: sizes must be "
                "a non-empty list."
            )

        image = product["image"]

        if not isinstance(image, str):
            fail(
                f"{sku}: image must be a string."
            )

        if not image.startswith("/catalog/"):
            fail(
                f"{sku}: product image must use "
                "a local /catalog/ asset; "
                f"found '{image}'."
            )

        image_path = (
            PROJECT_ROOT
            / "public"
            / image.removeprefix("/")
        )

        if not image_path.is_file():
            fail(
                f"{sku}: missing image file "
                f"'{image_path}'."
            )

    print(
        "Catalog validation passed:"
    )

    print(
        f"- Products: {len(products)}"
    )

    print(
        f"- Unique SKUs: {len(seen_skus)}"
    )

    print(
        f"- Unique images: "
        f"{len(image_counts)}"
    )

    print("- Category distribution:")

    for category in sorted(
        PRODUCT_CATEGORIES
    ):
        print(
            f"  - {category}: "
            f"{category_counts.get(category, 0)}"
        )


if __name__ == "__main__":
    main()