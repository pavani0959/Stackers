from __future__ import annotations

import ast
import json
import math
import sqlite3
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = BACKEND_ROOT / "myntra.db"
OUTPUT_PATH = BACKEND_ROOT / "seed_data" / "products.json"

TARGET_PRODUCT_COUNT = 120

COLOURS = [
    "black",
    "white",
    "grey",
    "beige",
    "brown",
    "blue",
    "navy",
    "green",
    "olive",
    "red",
    "pink",
    "purple",
    "yellow",
    "orange",
]

OCCASION_ALIASES = {
    "college": "campus",
    "college fest": "campus",
    "everyday": "casual",
    "daily": "casual",
    "work": "office",
    "formal": "office",
    "job interview": "interview",
    "night out": "party",
    "vacation": "travel",
    "holiday": "travel",
    "gym": "sports",
}

ALLOWED_OCCASIONS = {
    "campus",
    "casual",
    "office",
    "interview",
    "party",
    "wedding",
    "festival",
    "date",
    "travel",
    "sports",
    "beach",
}

ALLOWED_SEASONS = {
    "all_season",
    "summer",
    "winter",
    "monsoon",
    "spring",
    "autumn",
}

CATEGORY_PREFIXES = {
    "top": "TOP",
    "bottom": "BOT",
    "dress": "DRS",
    "outerwear": "OUT",
    "footwear": "FTW",
    "accessory": "ACC",
    "ethnic_set": "ETH",
}


def parse_list(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [
            str(item).strip().lower()
            for item in value
            if str(item).strip()
        ]

    if not isinstance(value, str):
        return [str(value).strip().lower()]

    stripped = value.strip()

    if not stripped:
        return []

    try:
        parsed = json.loads(stripped)

        if isinstance(parsed, list):
            return [
                str(item).strip().lower()
                for item in parsed
                if str(item).strip()
            ]
    except json.JSONDecodeError:
        pass

    try:
        parsed = ast.literal_eval(stripped)

        if isinstance(parsed, (list, tuple, set)):
            return [
                str(item).strip().lower()
                for item in parsed
                if str(item).strip()
            ]
    except (ValueError, SyntaxError):
        pass

    if "," in stripped:
        return [
            item.strip().strip("'\"").lower()
            for item in stripped.split(",")
            if item.strip().strip("'\"")
        ]

    cleaned = stripped.strip("[]{}()'\" ").lower()

    return [cleaned] if cleaned else []


def unique_strings(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()

    for value in values:
        normalized = value.strip().lower()

        if normalized and normalized not in seen:
            result.append(normalized)
            seen.add(normalized)

    return result


def classify_product(name: str) -> tuple[str, str]:
    normalized = name.lower()

    if "kurta set" in normalized:
        return "ethnic_set", "kurta_set"

    if "lehenga" in normalized:
        return "ethnic_set", "lehenga"

    if "saree" in normalized:
        return "ethnic_set", "saree"

    if "salwar" in normalized:
        return "ethnic_set", "salwar_set"

    if "sneaker" in normalized:
        return "footwear", "sneakers"

    if "heel" in normalized:
        return "footwear", "heels"

    if "flat" in normalized:
        return "footwear", "flats"

    if "sandal" in normalized:
        return "footwear", "sandals"

    if "boot" in normalized:
        return "footwear", "boots"

    if "formal shoe" in normalized:
        return "footwear", "formal_shoes"

    if "watch" in normalized:
        return "accessory", "watch"

    if "sunglass" in normalized:
        return "accessory", "sunglasses"

    if "jewellery" in normalized or "necklace" in normalized:
        return "accessory", "jewellery"

    if "belt" in normalized:
        return "accessory", "belt"

    if "cap" in normalized:
        return "accessory", "cap"

    if "scarf" in normalized:
        return "accessory", "scarf"

    if "bag" in normalized or "tote" in normalized:
        return "accessory", "bag"

    if "cargo" in normalized:
        return "bottom", "cargo_pants"

    if "jean" in normalized or "denim pants" in normalized:
        return "bottom", "jeans"

    if "trouser" in normalized or "pant" in normalized:
        return "bottom", "trousers"

    if "short" in normalized:
        return "bottom", "shorts"

    if "skirt" in normalized:
        return "bottom", "skirt"

    if "legging" in normalized:
        return "bottom", "leggings"

    if "palazzo" in normalized:
        return "bottom", "palazzo"

    if "bodycon" in normalized:
        return "dress", "bodycon_dress"

    if "maxi dress" in normalized:
        return "dress", "maxi_dress"

    if "party dress" in normalized:
        return "dress", "party_dress"

    if "dress" in normalized:
        return "dress", "casual_dress"

    if "blazer" in normalized:
        return "outerwear", "blazer"

    if "jacket" in normalized:
        return "outerwear", "jacket"

    if "cardigan" in normalized:
        return "outerwear", "cardigan"

    if "coat" in normalized:
        return "outerwear", "coat"

    if "hoodie" in normalized:
        return "top", "hoodie"

    if "sweatshirt" in normalized:
        return "top", "sweatshirt"

    if "crop top" in normalized:
        return "top", "crop_top"

    if "blouse" in normalized:
        return "top", "blouse"

    if "kurta" in normalized:
        return "top", "kurta"

    if "shirt" in normalized or "button-up" in normalized:
        return "top", "shirt"

    return "top", "t_shirt"


def infer_colour(name: str, variant_index: int) -> str:
    normalized = name.lower()

    for colour in COLOURS:
        if colour in normalized:
            base_index = COLOURS.index(colour)

            return COLOURS[
                (base_index + variant_index) % len(COLOURS)
            ]

    return COLOURS[variant_index % len(COLOURS)]


def normalize_occasions(values: list[str]) -> list[str]:
    result: list[str] = []

    for value in values:
        normalized = value.strip().lower()
        normalized = OCCASION_ALIASES.get(
            normalized,
            normalized,
        )

        if normalized in ALLOWED_OCCASIONS:
            result.append(normalized)

    result = unique_strings(result)

    if not result:
        return ["casual", "campus"]

    return result


def normalize_season(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    normalized = normalized.replace("-", "_")
    normalized = normalized.replace(" ", "_")

    aliases = {
        "all": "all_season",
        "allseason": "all_season",
        "all_seasons": "all_season",
        "year_round": "all_season",
    }

    normalized = aliases.get(normalized, normalized)

    if normalized not in ALLOWED_SEASONS:
        return "all_season"

    return normalized


def sizes_for_category(
    category: str,
    subcategory: str,
) -> list[str]:
    if category == "accessory":
        return ["ONE_SIZE"]

    if category == "footwear":
        return ["5", "6", "7", "8", "9", "10"]

    if subcategory == "saree":
        return ["FREE_SIZE"]

    return ["XS", "S", "M", "L", "XL"]


def normalize_budget_tier(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    normalized = normalized.replace("-", "_")
    normalized = normalized.replace(" ", "_")

    aliases = {
        "campus_casual": "budget",
        "budget_friendly": "budget",
        "midrange": "mid_range",
        "mid": "mid_range",
        "luxury": "premium",
    }

    normalized = aliases.get(normalized, normalized)

    if normalized not in {
        "budget",
        "mid_range",
        "premium",
    }:
        return "mid_range"

    return normalized


def load_base_products() -> list[sqlite3.Row]:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}"
        )

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    try:
        products = connection.execute(
            """
            SELECT
                id,
                name,
                brand,
                price,
                "originalPrice",
                image,
                tags,
                occasions,
                "budgetTier",
                season
            FROM products
            ORDER BY id
            """
        ).fetchall()
    finally:
        connection.close()

    if not products:
        raise RuntimeError(
            "No existing products were found in myntra.db."
        )

    return products


def create_catalog(
    base_products: list[sqlite3.Row],
) -> list[dict[str, Any]]:
    catalog: list[dict[str, Any]] = []

    variants_per_product = math.ceil(
        TARGET_PRODUCT_COUNT / len(base_products)
    )

    price_factors = [
        1.00,
        0.92,
        1.08,
        1.15,
        0.88,
        1.22,
        0.97,
    ]

    for variant_index in range(variants_per_product):
        for base_product in base_products:
            if len(catalog) >= TARGET_PRODUCT_COUNT:
                break

            category, subcategory = classify_product(
                base_product["name"]
            )

            colour = infer_colour(
                base_product["name"],
                variant_index,
            )

            product_number = len(catalog) + 1

            prefix = CATEGORY_PREFIXES[category]

            sku = (
                f"MYI-{prefix}-{product_number:04d}"
            )

            base_price = float(base_product["price"])
            price_factor = price_factors[
                variant_index % len(price_factors)
            ]

            price = max(
                199,
                round(base_price * price_factor),
            )

            base_original_price = float(
                base_product["originalPrice"]
                or base_price
            )

            original_price = max(
                price,
                round(
                    max(
                        base_original_price,
                        price * 1.25,
                    )
                ),
            )

            if variant_index == 0:
                product_name = base_product["name"]
            else:
                product_name = (
                    f"{colour.title()} "
                    f"{base_product['name']}"
                )

            base_tags = parse_list(
                base_product["tags"]
            )

            tags = unique_strings(
                base_tags
                + [
                    category,
                    subcategory,
                    colour,
                    "fashion_dna",
                ]
            )

            occasions = normalize_occasions(
                parse_list(
                    base_product["occasions"]
                )
            )

            product = {
                "sku": sku,
                "name": product_name,
                "brand": base_product["brand"],
                "description": (
                    f"{product_name} designed for "
                    f"{', '.join(occasions)} styling. "
                    "Structured for Fashion DNA matching "
                    "and outfit recommendation."
                ),
                "price": price,
                "originalPrice": original_price,
                "image": base_product["image"],
                "category": category,
                "subcategory": subcategory,
                "primary_colour": colour,
                "gender_segment": "unisex",
                "tags": tags,
                "occasions": occasions,
                "sizes": sizes_for_category(
                    category,
                    subcategory,
                ),
                "budgetTier": normalize_budget_tier(
                    base_product["budgetTier"]
                ),
                "season": normalize_season(
                    base_product["season"]
                ),
                "stock_quantity": (
                    15
                    + (
                        product_number * 7
                    ) % 86
                ),
                "is_active": True,
            }

            catalog.append(product)

    return catalog


def main() -> None:
    base_products = load_base_products()
    catalog = create_catalog(base_products)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            catalog,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        "Phase 2 demonstration catalogue generated."
    )
    print(
        "Base products:",
        len(base_products),
    )
    print(
        "Generated products:",
        len(catalog),
    )
    print(
        "Output:",
        OUTPUT_PATH,
    )


if __name__ == "__main__":
    main()