from __future__ import annotations

import ast
import json
import re
import sqlite3
from collections import Counter
from html import escape
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_ROOT.parent

DATABASE_PATH = BACKEND_ROOT / "myntra.db"
OUTPUT_PATH = (
    BACKEND_ROOT
    / "seed_data"
    / "products.json"
)

CATALOG_ASSET_DIR = (
    PROJECT_ROOT
    / "public"
    / "catalog"
)

TARGET_PRODUCT_COUNT = 120

TARGET_CATEGORY_COUNTS = {
    "top": 25,
    "bottom": 20,
    "dress": 15,
    "outerwear": 10,
    "footwear": 18,
    "accessory": 22,
    "ethnic_set": 10,
}

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

CATEGORY_DISPLAY_NAMES = {
    "top": "Top",
    "bottom": "Bottom",
    "dress": "Dress",
    "outerwear": "Outerwear",
    "footwear": "Footwear",
    "accessory": "Accessory",
    "ethnic_set": "Ethnic Set",
}

CATEGORY_ASSET_COLOURS = {
    "top": "#ff3f6c",
    "bottom": "#4f46e5",
    "dress": "#a855f7",
    "outerwear": "#475569",
    "footwear": "#0f766e",
    "accessory": "#d97706",
    "ethnic_set": "#be123c",
}


def curated_product(
    *,
    name: str,
    brand: str,
    price: int,
    original_price: int,
    tags: list[str],
    occasions: list[str],
    budget_tier: str = "budget",
    season: str = "all_season",
) -> dict[str, Any]:
    return {
        "name": name,
        "brand": brand,
        "price": price,
        "originalPrice": original_price,
        "tags": tags,
        "occasions": occasions,
        "budgetTier": budget_tier,
        "season": season,
    }


CURATED_BASE_PRODUCTS = [
    # Budget-safe interview tops.
    curated_product(
        name="Essential Interview Shirt",
        brand="StyleCore",
        price=449,
        original_price=899,
        tags=[
            "smart casual",
            "minimalist",
            "formal",
            "interview",
            "hard_budget_anchor",
        ],
        occasions=[
            "interview",
            "office",
        ],
    ),
    curated_product(
        name="Soft Interview Blouse",
        brand="StyleCore",
        price=499,
        original_price=999,
        tags=[
            "smart casual",
            "minimalist",
            "formal",
            "interview",
            "hard_budget_anchor",
        ],
        occasions=[
            "interview",
            "office",
        ],
    ),
    curated_product(
        name="Minimal Interview Top",
        brand="StyleCore",
        price=549,
        original_price=1099,
        tags=[
            "smart casual",
            "minimalist",
            "formal",
            "interview",
            "hard_budget_anchor",
        ],
        occasions=[
            "interview",
            "office",
        ],
    ),

    # Budget-safe interview bottoms.
    curated_product(
        name="Straight Interview Trousers",
        brand="StyleCore",
        price=549,
        original_price=1099,
        tags=[
            "smart casual",
            "minimalist",
            "formal",
            "interview",
            "hard_budget_anchor",
        ],
        occasions=[
            "interview",
            "office",
        ],
    ),
    curated_product(
        name="Tailored Interview Trousers",
        brand="StyleCore",
        price=599,
        original_price=1199,
        tags=[
            "smart casual",
            "minimalist",
            "formal",
            "interview",
            "hard_budget_anchor",
        ],
        occasions=[
            "interview",
            "office",
        ],
    ),
    curated_product(
        name="Formal Straight Trousers",
        brand="StyleCore",
        price=649,
        original_price=1299,
        tags=[
            "smart casual",
            "minimalist",
            "formal",
            "interview",
            "hard_budget_anchor",
        ],
        occasions=[
            "interview",
            "office",
        ],
    ),

    # Budget-safe interview footwear.
    curated_product(
        name="Minimal Interview Flats",
        brand="StyleCore",
        price=499,
        original_price=999,
        tags=[
            "smart casual",
            "minimalist",
            "comfortable",
            "interview",
            "hard_budget_anchor",
        ],
        occasions=[
            "interview",
            "office",
        ],
    ),
    curated_product(
        name="Formal Interview Flats",
        brand="StyleCore",
        price=549,
        original_price=1099,
        tags=[
            "smart casual",
            "formal",
            "comfortable",
            "interview",
            "hard_budget_anchor",
        ],
        occasions=[
            "interview",
            "office",
        ],
    ),
    curated_product(
        name="Classic Formal Shoes",
        brand="StyleCore",
        price=599,
        original_price=1199,
        tags=[
            "smart casual",
            "formal",
            "comfortable",
            "interview",
            "hard_budget_anchor",
        ],
        occasions=[
            "interview",
            "office",
        ],
    ),

    # Budget-safe interview accessory.
    curated_product(
        name="Structured Interview Tote Bag",
        brand="StyleCore",
        price=449,
        original_price=899,
        tags=[
            "smart casual",
            "minimalist",
            "formal",
            "interview",
            "hard_budget_anchor",
        ],
        occasions=[
            "interview",
            "office",
        ],
    ),

    # Dresses.
    curated_product(
        name="Everyday Cotton Casual Dress",
        brand="Myntra Edit",
        price=799,
        original_price=1599,
        tags=[
            "casual",
            "minimalist",
            "comfortable",
        ],
        occasions=[
            "casual",
            "campus",
            "date",
        ],
        season="summer",
    ),
    curated_product(
        name="Relaxed Shirt Dress",
        brand="Myntra Edit",
        price=899,
        original_price=1799,
        tags=[
            "casual",
            "smart casual",
            "minimalist",
        ],
        occasions=[
            "casual",
            "office",
            "date",
        ],
    ),
    curated_product(
        name="Floral Party Dress",
        brand="Myntra Edit",
        price=1099,
        original_price=2199,
        tags=[
            "party",
            "feminine",
            "statement",
        ],
        occasions=[
            "party",
            "date",
        ],
    ),
    curated_product(
        name="Elegant Maxi Dress",
        brand="Myntra Edit",
        price=1199,
        original_price=2399,
        tags=[
            "maxi",
            "elegant",
            "occasion",
        ],
        occasions=[
            "party",
            "wedding",
            "date",
        ],
    ),
    curated_product(
        name="Classic Bodycon Dress",
        brand="Myntra Edit",
        price=999,
        original_price=1999,
        tags=[
            "bodycon",
            "party",
            "statement",
        ],
        occasions=[
            "party",
            "date",
        ],
    ),

    # Ethnic sets.
    curated_product(
        name="Minimal Cotton Kurta Set",
        brand="Myntra Ethnic",
        price=899,
        original_price=1799,
        tags=[
            "ethnic",
            "minimalist",
            "comfortable",
        ],
        occasions=[
            "festival",
            "casual",
            "campus",
        ],
    ),
    curated_product(
        name="Pastel Palazzo Kurta Set",
        brand="Myntra Ethnic",
        price=1099,
        original_price=2199,
        tags=[
            "ethnic",
            "pastel",
            "elegant",
        ],
        occasions=[
            "festival",
            "wedding",
        ],
    ),
    curated_product(
        name="Embroidered Festive Kurta Set",
        brand="Myntra Ethnic",
        price=1299,
        original_price=2599,
        tags=[
            "ethnic",
            "embroidered",
            "festive",
        ],
        occasions=[
            "festival",
            "wedding",
        ],
    ),
    curated_product(
        name="Contemporary Ethnic Set",
        brand="Myntra Ethnic",
        price=999,
        original_price=1999,
        tags=[
            "ethnic",
            "contemporary",
            "smart casual",
        ],
        occasions=[
            "festival",
            "office",
            "casual",
        ],
    ),
]


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
        normalized = str(value).strip().lower()

        return [normalized] if normalized else []

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

        if isinstance(
            parsed,
            (
                list,
                tuple,
                set,
            ),
        ):
            return [
                str(item).strip().lower()
                for item in parsed
                if str(item).strip()
            ]
    except (
        ValueError,
        SyntaxError,
    ):
        pass

    if "," in stripped:
        return [
            item.strip().strip("'\"").lower()
            for item in stripped.split(",")
            if item.strip().strip("'\"")
        ]

    cleaned = stripped.strip(
        "[]{}()'\" "
    ).lower()

    return [cleaned] if cleaned else []


def unique_strings(
    values: list[str],
) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()

    for value in values:
        normalized = value.strip().lower()

        if (
            normalized
            and normalized not in seen
        ):
            result.append(normalized)
            seen.add(normalized)

    return result


def classify_product(
    name: str,
) -> tuple[str, str]:
    normalized = name.lower()

    # Ethnic sets must be checked before
    # the generic kurta/top rule.
    if any(
        token in normalized
        for token in (
            "kurta set",
            "kurti set",
            "ethnic set",
            "salwar suit",
            "palazzo kurta set",
            "anarkali set",
            "co-ord ethnic",
        )
    ):
        return "ethnic_set", "kurta_set"

    # Use only subcategories that exist in
    # backend/catalog_taxonomy.py.
    if "bodycon dress" in normalized:
        return "dress", "bodycon_dress"

    if "maxi dress" in normalized:
        return "dress", "maxi_dress"

    if "party dress" in normalized:
        return "dress", "party_dress"

    if "dress" in normalized:
        return "dress", "casual_dress"

    if any(
        token in normalized
        for token in (
            "earring",
            "earrings",
            "necklace",
            "necklaces",
            "bracelet",
            "bracelets",
            "jewellery",
            "jewelry",
            "pendant",
            "bangle",
            "bangles",
        )
    ):
        return "accessory", "jewellery"

    if (
        "bag" in normalized
        or "tote" in normalized
    ):
        return "accessory", "bag"

    if "watch" in normalized:
        return "accessory", "watch"

    if "sunglass" in normalized:
        return "accessory", "sunglasses"

    if "belt" in normalized:
        return "accessory", "belt"

    if "cap" in normalized:
        return "accessory", "cap"

    if "scarf" in normalized:
        return "accessory", "scarf"

    if "formal shoe" in normalized:
        return "footwear", "formal_shoes"

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

    if "blazer" in normalized:
        return "outerwear", "blazer"

    if "jacket" in normalized:
        return "outerwear", "jacket"

    if "cardigan" in normalized:
        return "outerwear", "cardigan"

    if "coat" in normalized:
        return "outerwear", "coat"

    if "cargo" in normalized:
        return "bottom", "cargo_pants"

    if (
        "jean" in normalized
        or "denim pants" in normalized
    ):
        return "bottom", "jeans"

    if (
        "trouser" in normalized
        or "pant" in normalized
    ):
        return "bottom", "trousers"

    if "short" in normalized:
        return "bottom", "shorts"

    if "skirt" in normalized:
        return "bottom", "skirt"

    if "legging" in normalized:
        return "bottom", "leggings"

    if "palazzo" in normalized:
        return "bottom", "palazzo"

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

    if (
        "shirt" in normalized
        or "button-up" in normalized
    ):
        return "top", "shirt"

    return "top", "t_shirt"


def infer_colour(
    name: str,
    variant_index: int,
) -> str:
    normalized = name.lower()

    for colour in COLOURS:
        if colour in normalized:
            base_index = COLOURS.index(colour)

            return COLOURS[
                (
                    base_index
                    + variant_index
                )
                % len(COLOURS)
            ]

    return COLOURS[
        variant_index
        % len(COLOURS)
    ]


def normalize_occasions(
    values: list[str],
) -> list[str]:
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
        return [
            "casual",
            "campus",
        ]

    return result


def normalize_season(
    value: Any,
) -> str:
    normalized = (
        str(value or "")
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    aliases = {
        "all": "all_season",
        "allseason": "all_season",
        "all_seasons": "all_season",
        "year_round": "all_season",
    }

    normalized = aliases.get(
        normalized,
        normalized,
    )

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
        return [
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
        ]

    return [
        "XS",
        "S",
        "M",
        "L",
        "XL",
    ]


def normalize_budget_tier(
    value: Any,
) -> str:
    normalized = (
        str(value or "")
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    aliases = {
        "campus_casual": "budget",
        "budget_friendly": "budget",
        "midrange": "mid_range",
        "mid": "mid_range",
        "luxury": "premium",
    }

    normalized = aliases.get(
        normalized,
        normalized,
    )

    if normalized not in {
        "budget",
        "mid_range",
        "premium",
    }:
        return "mid_range"

    return normalized


def load_base_products() -> list[dict[str, Any]]:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}"
        )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                name,
                brand,
                price,
                "originalPrice",
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

    if not rows:
        raise RuntimeError(
            "No existing products were found "
            "in myntra.db."
        )

    return [
        dict(row)
        for row in rows
    ]


def build_source_pools(
    base_products: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    # Curated products must come first so that
    # required interview products are guaranteed
    # to appear before category quotas are filled
    # by products already stored in the database.
    combined_products = [
        *CURATED_BASE_PRODUCTS,
        *base_products,
    ]

    pools: dict[
        str,
        list[dict[str, Any]],
    ] = {
        category: []
        for category
        in TARGET_CATEGORY_COUNTS
    }

    seen_names: set[str] = set()

    for product in combined_products:
        name = str(
            product.get("name") or ""
        ).strip()

        if not name:
            continue

        normalized_name = name.lower()

        if normalized_name in seen_names:
            continue

        category, _ = classify_product(name)

        pools[category].append(product)
        seen_names.add(normalized_name)

    for category, products in pools.items():
        if not products:
            raise RuntimeError(
                "No source products are available "
                f"for category '{category}'."
            )

    return pools


def slugify(value: str) -> str:
    normalized = re.sub(
        r"[^a-z0-9]+",
        "-",
        value.lower(),
    ).strip("-")

    return normalized or "product"


def create_local_catalog_asset(
    *,
    sku: str,
    product_name: str,
    brand: str,
    category: str,
    colour: str,
) -> str:
    CATALOG_ASSET_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = (
        f"{sku.lower()}-"
        f"{slugify(product_name)[:45]}.svg"
    )

    asset_path = (
        CATALOG_ASSET_DIR
        / filename
    )

    background = (
        CATEGORY_ASSET_COLOURS[
            category
        ]
    )

    safe_name = escape(
        product_name[:38]
    )

    safe_brand = escape(
        brand[:28]
    )

    safe_category = escape(
        CATEGORY_DISPLAY_NAMES[
            category
        ]
    )

    safe_colour = escape(
        colour.title()
    )

    svg = f"""\
<svg xmlns="http://www.w3.org/2000/svg"
     width="600"
     height="800"
     viewBox="0 0 600 800"
     role="img"
     aria-labelledby="title description">
  <title id="title">{safe_name}</title>
  <desc id="description">
    Local catalogue artwork for {safe_name}
  </desc>

  <rect width="600"
        height="800"
        rx="36"
        fill="{background}" />

  <circle cx="500"
          cy="110"
          r="150"
          fill="#ffffff"
          opacity="0.12" />

  <circle cx="90"
          cy="700"
          r="190"
          fill="#ffffff"
          opacity="0.08" />

  <rect x="56"
        y="64"
        width="488"
        height="672"
        rx="28"
        fill="#ffffff"
        opacity="0.94" />

  <text x="300"
        y="160"
        text-anchor="middle"
        font-family="Arial, sans-serif"
        font-size="24"
        font-weight="700"
        fill="#111827">
    {safe_brand}
  </text>

  <text x="300"
        y="340"
        text-anchor="middle"
        font-family="Arial, sans-serif"
        font-size="32"
        font-weight="700"
        fill="#111827">
    {safe_category}
  </text>

  <text x="300"
        y="420"
        text-anchor="middle"
        font-family="Arial, sans-serif"
        font-size="25"
        font-weight="600"
        fill="#374151">
    {safe_name}
  </text>

  <text x="300"
        y="485"
        text-anchor="middle"
        font-family="Arial, sans-serif"
        font-size="20"
        fill="#6b7280">
    Colour: {safe_colour}
  </text>

  <text x="300"
        y="665"
        text-anchor="middle"
        font-family="Arial, sans-serif"
        font-size="18"
        font-weight="700"
        fill="{background}">
    MYNTRA IDENTITY CATALOGUE
  </text>
</svg>
"""

    asset_path.write_text(
        svg,
        encoding="utf-8",
    )

    return f"/catalog/{filename}"


def clear_generated_assets() -> None:
    CATALOG_ASSET_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    for asset_path in (
        CATALOG_ASSET_DIR.glob(
            "myi-*.svg"
        )
    ):
        asset_path.unlink()


def create_catalog(
    base_products: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    pools = build_source_pools(
        base_products
    )

    catalog: list[dict[str, Any]] = []

    price_factors = [
        1.00,
        0.92,
        1.08,
        1.15,
        0.88,
        1.12,
        0.97,
    ]

    for (
        category,
        target_count,
    ) in TARGET_CATEGORY_COUNTS.items():
        source_pool = pools[category]

        for category_index in range(
            target_count
        ):
            base_product = source_pool[
                category_index
                % len(source_pool)
            ]

            source_cycle = (
                category_index
                // len(source_pool)
            )

            (
                detected_category,
                subcategory,
            ) = classify_product(
                str(base_product["name"])
            )

            if detected_category != category:
                raise RuntimeError(
                    "Category pool mismatch: "
                    f"expected '{category}', "
                    f"received "
                    f"'{detected_category}'."
                )

            colour = infer_colour(
                str(base_product["name"]),
                category_index,
            )

            product_number = (
                len(catalog)
                + 1
            )

            prefix = (
                CATEGORY_PREFIXES[
                    category
                ]
            )

            sku = (
                f"MYI-{prefix}-"
                f"{product_number:04d}"
            )

            base_name = str(
                base_product["name"]
            ).strip()

            if source_cycle == 0:
                product_name = base_name
            else:
                product_name = (
                    f"{colour.title()} "
                    f"{base_name}"
                )

            base_tags = parse_list(
                base_product.get("tags")
            )

            taxonomy_tags = {
                "top",
                "bottom",
                "dress",
                "outerwear",
                "footwear",
                "accessory",
                "ethnic_set",
                "t_shirt",
                "shirt",
                "blouse",
                "crop_top",
                "sweatshirt",
                "hoodie",
                "kurta",
                "jeans",
                "trousers",
                "cargo_pants",
                "shorts",
                "skirt",
                "leggings",
                "palazzo",
                "casual_dress",
                "party_dress",
                "maxi_dress",
                "bodycon_dress",
                "jacket",
                "blazer",
                "cardigan",
                "coat",
                "sneakers",
                "heels",
                "flats",
                "sandals",
                "boots",
                "formal_shoes",
                "bag",
                "watch",
                "jewellery",
                "sunglasses",
                "belt",
                "cap",
                "scarf",
                "kurta_set",
            }

            cleaned_base_tags = [
                tag
                for tag in base_tags
                if (
                    tag not in taxonomy_tags
                    and tag not in COLOURS
                )
            ]

            if (
                "hard_budget_anchor"
                in base_tags
            ):
                price_factor = 1.0
            else:
                price_factor = (
                    price_factors[
                        category_index
                        % len(price_factors)
                    ]
                )

            base_price = float(
                base_product["price"]
            )

            price = max(
                199,
                round(
                    base_price
                    * price_factor
                ),
            )

            base_original_price = float(
                base_product.get(
                    "originalPrice"
                )
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

            occasions = normalize_occasions(
                parse_list(
                    base_product.get(
                        "occasions"
                    )
                )
            )

            tags = unique_strings(
                cleaned_base_tags
                + [
                    category,
                    subcategory,
                    colour,
                    "fashion_dna",
                ]
            )

            brand = str(
                base_product.get("brand")
                or "Myntra Identity"
            ).strip()

            image = (
                create_local_catalog_asset(
                    sku=sku,
                    product_name=product_name,
                    brand=brand,
                    category=category,
                    colour=colour,
                )
            )

            product = {
                "sku": sku,
                "name": product_name,
                "brand": brand,
                "description": (
                    f"{product_name} designed "
                    f"for "
                    f"{', '.join(occasions)} "
                    "styling. Structured for "
                    "Fashion DNA matching and "
                    "outfit recommendation."
                ),
                "price": price,
                "originalPrice": (
                    original_price
                ),
                "image": image,
                "category": category,
                "subcategory": (
                    subcategory
                ),
                "primary_colour": colour,
                "gender_segment": "unisex",
                "tags": tags,
                "occasions": occasions,
                "sizes": (
                    sizes_for_category(
                        category,
                        subcategory,
                    )
                ),
                "budgetTier": (
                    normalize_budget_tier(
                        base_product.get(
                            "budgetTier"
                        )
                    )
                ),
                "season": (
                    normalize_season(
                        base_product.get(
                            "season"
                        )
                    )
                ),
                "stock_quantity": (
                    15
                    + (
                        product_number
                        * 7
                    )
                    % 86
                ),
                "is_active": True,
            }

            catalog.append(product)

    if len(catalog) != TARGET_PRODUCT_COUNT:
        raise RuntimeError(
            "Generated catalogue count "
            "does not match target: "
            f"expected "
            f"{TARGET_PRODUCT_COUNT}, "
            f"found {len(catalog)}."
        )

    return catalog


def main() -> None:
    if (
        sum(
            TARGET_CATEGORY_COUNTS.values()
        )
        != TARGET_PRODUCT_COUNT
    ):
        raise RuntimeError(
            "TARGET_CATEGORY_COUNTS must "
            f"sum to "
            f"{TARGET_PRODUCT_COUNT}."
        )

    clear_generated_assets()

    base_products = load_base_products()

    catalog = create_catalog(
        base_products
    )

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

    category_counts = Counter(
        product["category"]
        for product in catalog
    )

    print(
        "Phase 2 catalogue generated."
    )

    print(
        f"Database source products: "
        f"{len(base_products)}"
    )

    print(
        f"Curated source products: "
        f"{len(CURATED_BASE_PRODUCTS)}"
    )

    print(
        f"Generated products: "
        f"{len(catalog)}"
    )

    print(
        "Category distribution:"
    )

    for category in (
        TARGET_CATEGORY_COUNTS
    ):
        print(
            f"- {category}: "
            f"{category_counts.get(category, 0)}"
        )

    print(
        f"Local catalogue assets: "
        f"{CATALOG_ASSET_DIR}"
    )

    print(
        f"Output: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()