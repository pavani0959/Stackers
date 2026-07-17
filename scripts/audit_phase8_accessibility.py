from pathlib import Path
import re
import sys


SEARCH_ROOTS = [
    Path("src/screens"),
    Path("src/components"),
]

NON_INTERACTIVE_TAGS = {
    "div",
    "span",
    "article",
    "li",
}

CONTROL_TAGS = {
    "button",
    "a",
}

CONTROL_EMOJIS = (
    "🔍",
    "��",
    "👤",
    "🎯",
    "🧬",
    "🎤",
    "✅",
    "⚠️",
    "❤️",
    "♡",
    "←",
    "×",
)


def find_opening_tag_end(
    source: str,
    start: int,
) -> int | None:
    brace_depth = 0
    quote = None
    escaped = False

    index = start

    while index < len(source):
        character = source[index]

        if escaped:
            escaped = False
            index += 1
            continue

        if quote is not None:
            if character == "\\":
                escaped = True
            elif character == quote:
                quote = None

            index += 1
            continue

        if character in {"'", '"', "`"}:
            quote = character
            index += 1
            continue

        if character == "{":
            brace_depth += 1
        elif character == "}":
            brace_depth = max(
                0,
                brace_depth - 1,
            )
        elif (
            character == ">"
            and brace_depth == 0
        ):
            return index

        index += 1

    return None


def line_number(
    source: str,
    position: int,
) -> int:
    return (
        source.count(
            "\n",
            0,
            position,
        )
        + 1
    )


def audit_clickable_elements(
    path: Path,
    source: str,
) -> list[str]:
    problems = []

    pattern = re.compile(
        r"<(div|span|article|li)\b",
    )

    for match in pattern.finditer(source):
        tag_end = find_opening_tag_end(
            source,
            match.end(),
        )

        if tag_end is None:
            continue

        opening_tag = source[
            match.start():
            tag_end + 1
        ]

        if "onClick" not in opening_tag:
            continue

        problems.append(
            (
                f"{path}:"
                f"{line_number(source, match.start())}: "
                f"clickable <{match.group(1)}>"
            )
        )

    return problems


def audit_control_emojis(
    path: Path,
    source: str,
) -> list[str]:
    problems = []

    control_pattern = re.compile(
        r"<(?P<tag>button|a)\b"
        r"(?P<attributes>[\s\S]*?)>"
        r"(?P<body>[\s\S]*?)"
        r"</(?P=tag)>",
    )

    for match in control_pattern.finditer(source):
        control_source = (
            match.group("attributes")
            + match.group("body")
        )

        found = [
            emoji
            for emoji in CONTROL_EMOJIS
            if emoji in control_source
        ]

        if not found:
            continue

        problems.append(
            (
                f"{path}:"
                f"{line_number(source, match.start())}: "
                f"<{match.group('tag')}> contains "
                f"control emoji(s): "
                f"{' '.join(found)}"
            )
        )

    return problems


def audit_icon_only_labels(
    path: Path,
    source: str,
) -> list[str]:
    problems = []

    button_pattern = re.compile(
        r"<button\b"
        r"(?P<attributes>[\s\S]*?)>"
        r"(?P<body>[\s\S]*?)"
        r"</button>",
    )

    lucide_pattern = re.compile(
        r"<[A-Z][A-Za-z0-9]*\b",
    )

    for match in button_pattern.finditer(source):
        attributes = match.group(
            "attributes",
        )

        body = match.group(
            "body",
        )

        contains_icon = bool(
            lucide_pattern.search(body)
        )

        visible_text = re.sub(
            r"<[^>]+>",
            "",
            body,
        )

        visible_text = re.sub(
            r"\{[\s\S]*?\}",
            "",
            visible_text,
        ).strip()

        if (
            contains_icon
            and not visible_text
            and "aria-label=" not in attributes
            and "aria-labelledby=" not in attributes
        ):
            problems.append(
                (
                    f"{path}:"
                    f"{line_number(source, match.start())}: "
                    "icon-only button has no aria-label"
                )
            )

    return problems


all_problems = []

for root in SEARCH_ROOTS:
    if not root.exists():
        continue

    for path in sorted(
        root.rglob("*.jsx"),
    ):
        if ".before-" in path.name:
            continue

        source = path.read_text(
            encoding="utf-8",
        )

        all_problems.extend(
            audit_clickable_elements(
                path,
                source,
            )
        )

        all_problems.extend(
            audit_control_emojis(
                path,
                source,
            )
        )

        all_problems.extend(
            audit_icon_only_labels(
                path,
                source,
            )
        )


if all_problems:
    print(
        "\nPhase 8 accessibility issues:\n"
    )

    for problem in all_problems:
        print(
            f"- {problem}"
        )

    print(
        f"\nTotal issues: "
        f"{len(all_problems)}"
    )

    sys.exit(1)


print(
    "Phase 8 accessibility audit passed."
)
