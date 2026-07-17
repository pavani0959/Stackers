from __future__ import annotations

import html
import shutil
import subprocess
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIRECTORY = PROJECT_ROOT / "public" / "quiz"

ASSETS = [
    (
        "balance-comfort-balanced.webp",
        "Balanced Comfort",
        "Comfort with polished structure",
        "#0f766e",
        "#ccfbf1",
    ),
    (
        "balance-comfort-first.webp",
        "Comfort First",
        "Soft, relaxed and effortless",
        "#0369a1",
        "#e0f2fe",
    ),
    (
        "balance-expression-balanced.webp",
        "Balanced Expression",
        "Personal style without excess",
        "#7c3aed",
        "#ede9fe",
    ),
    (
        "balance-expression-first.webp",
        "Expression First",
        "Bold looks with personality",
        "#be123c",
        "#ffe4e6",
    ),
    (
        "brand-clean-premium.webp",
        "Clean Premium",
        "Refined, minimal and elevated",
        "#334155",
        "#f1f5f9",
    ),
    (
        "brand-expressive-trend.webp",
        "Expressive Trends",
        "Current, playful and noticeable",
        "#c026d3",
        "#fae8ff",
    ),
    (
        "brand-sporty-active.webp",
        "Sporty Active",
        "Performance-inspired everyday style",
        "#15803d",
        "#dcfce7",
    ),
    (
        "brand-youth-street.webp",
        "Youth Street",
        "Urban, relaxed and experimental",
        "#1d4ed8",
        "#dbeafe",
    ),
    (
        "everyday-minimal-campus.webp",
        "Minimal Campus",
        "Clean everyday college styling",
        "#475569",
        "#f8fafc",
    ),
    (
        "everyday-quiet-luxury.webp",
        "Quiet Luxury",
        "Subtle quality and timeless polish",
        "#92400e",
        "#fef3c7",
    ),
    (
        "everyday-soft-romantic.webp",
        "Soft Romantic",
        "Gentle colours and flowing shapes",
        "#be185d",
        "#fce7f3",
    ),
    (
        "everyday-street-ready.webp",
        "Street Ready",
        "Layered and confident city style",
        "#4338ca",
        "#e0e7ff",
    ),
    (
        "fit-fitted.webp",
        "Fitted",
        "Defined and close to the body",
        "#be123c",
        "#ffe4e6",
    ),
    (
        "fit-oversized.webp",
        "Oversized",
        "Loose proportions and street influence",
        "#3730a3",
        "#e0e7ff",
    ),
    (
        "fit-regular.webp",
        "Regular Fit",
        "Classic proportions for everyday wear",
        "#0369a1",
        "#e0f2fe",
    ),
    (
        "fit-relaxed.webp",
        "Relaxed Fit",
        "Easy movement and natural shape",
        "#047857",
        "#d1fae5",
    ),
    (
        "goal-experiment.webp",
        "Experiment More",
        "Discover new silhouettes and colours",
        "#a21caf",
        "#fae8ff",
    ),
    (
        "goal-signature.webp",
        "Build a Signature",
        "Create a recognisable personal style",
        "#9f1239",
        "#ffe4e6",
    ),
    (
        "goal-smart-shopping.webp",
        "Shop Smarter",
        "Buy versatile pieces with confidence",
        "#0f766e",
        "#ccfbf1",
    ),
    (
        "goal-wardrobe.webp",
        "Improve Wardrobe",
        "Build outfits from what you own",
        "#1d4ed8",
        "#dbeafe",
    ),
    (
        "motivation-quality.webp",
        "Quality",
        "Materials, construction and longevity",
        "#92400e",
        "#fef3c7",
    ),
    (
        "motivation-statement.webp",
        "Make a Statement",
        "Memorable pieces that stand out",
        "#be123c",
        "#ffe4e6",
    ),
    (
        "motivation-trend.webp",
        "Follow Trends",
        "Fresh ideas from current fashion",
        "#c026d3",
        "#fae8ff",
    ),
    (
        "motivation-versatility.webp",
        "Versatility",
        "Pieces that work in many outfits",
        "#047857",
        "#d1fae5",
    ),
    (
        "occasion-campus.webp",
        "Campus",
        "Comfortable style for college life",
        "#1d4ed8",
        "#dbeafe",
    ),
    (
        "occasion-everyday.webp",
        "Everyday",
        "Practical looks for daily routines",
        "#0f766e",
        "#ccfbf1",
    ),
    (
        "occasion-party.webp",
        "Party",
        "Confident evening and celebration looks",
        "#be185d",
        "#fce7f3",
    ),
    (
        "occasion-work.webp",
        "Work",
        "Polished and professional combinations",
        "#334155",
        "#f1f5f9",
    ),
    (
        "palette-bold.webp",
        "Bold Palette",
        "Strong colours and high contrast",
        "#dc2626",
        "#fee2e2",
    ),
    (
        "palette-earthy.webp",
        "Earthy Palette",
        "Brown, olive and natural warmth",
        "#78350f",
        "#fef3c7",
    ),
    (
        "palette-neutral.webp",
        "Neutral Palette",
        "Black, white, grey and beige",
        "#374151",
        "#f3f4f6",
    ),
    (
        "palette-pastel.webp",
        "Pastel Palette",
        "Soft pink, blue and lavender",
        "#7e22ce",
        "#f3e8ff",
    ),
]


def split_title(
    title: str,
) -> tuple[str, str]:
    words = title.split()

    if len(title) <= 19:
        return title, ""

    midpoint = max(
        1,
        len(words) // 2,
    )

    return (
        " ".join(words[:midpoint]),
        " ".join(words[midpoint:]),
    )


def create_svg(
    *,
    title: str,
    subtitle: str,
    accent: str,
    background: str,
) -> str:
    first_line, second_line = split_title(
        title
    )

    first_line = html.escape(first_line)
    second_line = html.escape(second_line)
    subtitle = html.escape(subtitle)

    second_title_element = ""

    if second_line:
        second_title_element = f"""
  <text
    x="300"
    y="520"
    text-anchor="middle"
    font-family="DejaVu Sans, Arial, sans-serif"
    font-size="38"
    font-weight="700"
    fill="#111827"
  >
    {second_line}
  </text>
"""

    return f"""\
<svg
  xmlns="http://www.w3.org/2000/svg"
  width="600"
  height="800"
  viewBox="0 0 600 800"
>
  <rect
    width="600"
    height="800"
    rx="36"
    fill="{background}"
  />

  <circle
    cx="490"
    cy="120"
    r="165"
    fill="{accent}"
    opacity="0.12"
  />

  <circle
    cx="100"
    cy="690"
    r="190"
    fill="{accent}"
    opacity="0.10"
  />

  <rect
    x="55"
    y="50"
    width="490"
    height="700"
    rx="30"
    fill="#ffffff"
    opacity="0.94"
  />

  <!-- Stylised fashion figure -->
  <circle
    cx="300"
    cy="200"
    r="48"
    fill="{accent}"
    opacity="0.88"
  />

  <path
    d="
      M235 275
      Q300 235 365 275
      L405 410
      L350 425
      L335 355
      L335 430
      L265 430
      L265 355
      L250 425
      L195 410
      Z
    "
    fill="{accent}"
    opacity="0.82"
  />

  <path
    d="
      M265 430
      L295 430
      L285 630
      L235 630
      Z
    "
    fill="#1f2937"
    opacity="0.88"
  />

  <path
    d="
      M305 430
      L335 430
      L365 630
      L315 630
      Z
    "
    fill="#1f2937"
    opacity="0.88"
  />

  <text
    x="300"
    y="475"
    text-anchor="middle"
    font-family="DejaVu Sans, Arial, sans-serif"
    font-size="38"
    font-weight="700"
    fill="#111827"
  >
    {first_line}
  </text>

  {second_title_element}

  <text
    x="300"
    y="680"
    text-anchor="middle"
    font-family="DejaVu Sans, Arial, sans-serif"
    font-size="18"
    fill="#4b5563"
  >
    {subtitle}
  </text>

  <text
    x="300"
    y="720"
    text-anchor="middle"
    font-family="DejaVu Sans, Arial, sans-serif"
    font-size="14"
    font-weight="700"
    letter-spacing="2"
    fill="{accent}"
  >
    MYNTRA IDENTITY
  </text>
</svg>
"""


def find_converter() -> str:
    converter = (
        shutil.which("magick")
        or shutil.which("convert")
    )

    if converter is None:
        raise RuntimeError(
            "ImageMagick was not found. Install it "
            "with: sudo dnf install -y ImageMagick"
        )

    return converter


def main() -> None:
    converter = find_converter()

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    for (
        filename,
        title,
        subtitle,
        accent,
        background,
    ) in ASSETS:
        svg = create_svg(
            title=title,
            subtitle=subtitle,
            accent=accent,
            background=background,
        )

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".svg",
            encoding="utf-8",
            delete=False,
        ) as temporary_file:
            temporary_file.write(svg)
            temporary_path = Path(
                temporary_file.name
            )

        output_path = (
            OUTPUT_DIRECTORY
            / filename
        )

        try:
            subprocess.run(
                [
                    converter,
                    str(temporary_path),
                    "-resize",
                    "600x800!",
                    "-strip",
                    "-quality",
                    "88",
                    str(output_path),
                ],
                check=True,
            )
        finally:
            temporary_path.unlink(
                missing_ok=True
            )

        print(
            f"Created {output_path.relative_to(PROJECT_ROOT)}"
        )

    print()
    print(
        f"Created {len(ASSETS)} quiz assets."
    )


if __name__ == "__main__":
    main()
