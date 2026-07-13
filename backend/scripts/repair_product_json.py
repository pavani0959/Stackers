from __future__ import annotations

import ast
import json
import sqlite3
from typing import Any


DATABASE_PATH = "myntra.db"
JSON_COLUMNS = (
    "tags",
    "occasions",
    "sizes",
)


def normalize_list(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    if not isinstance(value, str):
        return [str(value)]

    stripped = value.strip()

    if not stripped:
        return []

    # First try proper JSON.
    try:
        parsed = json.loads(stripped)

        if isinstance(parsed, list):
            return [
                str(item).strip()
                for item in parsed
                if str(item).strip()
            ]

        if isinstance(parsed, str):
            stripped = parsed.strip()
        elif parsed is None:
            return []
        else:
            return [str(parsed)]
    except json.JSONDecodeError:
        pass

    # Support legacy Python-list representations:
    # ['minimalist', 'casual']
    try:
        parsed = ast.literal_eval(stripped)

        if isinstance(parsed, (list, tuple, set)):
            return [
                str(item).strip()
                for item in parsed
                if str(item).strip()
            ]

        if isinstance(parsed, str):
            stripped = parsed.strip()
    except (ValueError, SyntaxError):
        pass

    # Support comma-separated legacy strings.
    if "," in stripped:
        return [
            item.strip().strip("'\"")
            for item in stripped.split(",")
            if item.strip().strip("'\"")
        ]

    # Preserve a single meaningful value rather than discarding it.
    cleaned = stripped.strip("[]{}()'\" ")

    return [cleaned] if cleaned else []


def main() -> None:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    repaired_counts = {
        column: 0
        for column in JSON_COLUMNS
    }

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                tags,
                occasions,
                sizes,
                stock_quantity,
                is_active
            FROM products
            ORDER BY id
            """
        ).fetchall()

        for row in rows:
            product_id = row["id"]

            for column in JSON_COLUMNS:
                current_value = row[column]
                normalized_value = normalize_list(current_value)
                encoded_value = json.dumps(
                    normalized_value,
                    ensure_ascii=False,
                )

                # Rewrite every legacy value into canonical JSON.
                if current_value != encoded_value:
                    connection.execute(
                        f"""
                        UPDATE products
                        SET "{column}" = ?
                        WHERE id = ?
                        """,
                        (
                            encoded_value,
                            product_id,
                        ),
                    )

                    repaired_counts[column] += 1

            if row["stock_quantity"] is None:
                connection.execute(
                    """
                    UPDATE products
                    SET stock_quantity = 0
                    WHERE id = ?
                    """,
                    (product_id,),
                )

            if row["is_active"] is None:
                connection.execute(
                    """
                    UPDATE products
                    SET is_active = 1
                    WHERE id = ?
                    """,
                    (product_id,),
                )

        connection.commit()

        print("Product JSON repair completed.")
        print("Products inspected:", len(rows))

        for column, count in repaired_counts.items():
            print(
                f"{column} values normalized:",
                count,
            )
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    main()