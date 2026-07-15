from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from schemas import DNAQuizAnswer


EXPECTED_QUESTION_IDS = {
    "everyday-look",
    "silhouette",
    "brand-personality",
    "colour-palette",
    "comfort-expression",
    "occasion-priority",
    "shopping-motivation",
    "fashion-goal",
}


QUESTION_STYLE_WEIGHTS = {
    "everyday-look": {
        "minimal-campus": {
            "minimalist": 4,
            "campusCasual": 3,
            "quietLuxury": 1,
        },
        "street-ready": {
            "streetwear": 4,
            "y2k": 2,
            "campusCasual": 1,
        },
        "soft-romantic": {
            "romantic": 4,
            "bohemian": 2,
            "minimalist": 1,
        },
        "quiet-luxury": {
            "quietLuxury": 4,
            "minimalist": 3,
        },
    },
    "silhouette": {
        "relaxed-fit": {
            "campusCasual": 3,
            "minimalist": 2,
            "bohemian": 1,
        },
        "oversized-fit": {
            "streetwear": 3,
            "y2k": 2,
            "campusCasual": 1,
        },
        "regular-fit": {
            "minimalist": 3,
            "campusCasual": 2,
        },
        "fitted-fit": {
            "quietLuxury": 3,
            "romantic": 2,
            "y2k": 1,
        },
    },
    "brand-personality": {
        "clean-premium": {
            "quietLuxury": 4,
            "minimalist": 3,
        },
        "youth-street": {
            "streetwear": 4,
            "y2k": 2,
        },
        "sporty-active": {
            "sporty": 4,
            "campusCasual": 2,
        },
        "expressive-trend": {
            "y2k": 3,
            "romantic": 2,
            "streetwear": 1,
        },
    },
    "colour-palette": {
        "neutral-palette": {
            "minimalist": 4,
            "quietLuxury": 3,
        },
        "earthy-palette": {
            "bohemian": 4,
            "minimalist": 1,
        },
        "pastel-palette": {
            "romantic": 4,
            "minimalist": 1,
        },
        "bold-palette": {
            "streetwear": 3,
            "y2k": 3,
        },
    },
    "comfort-expression": {
        "comfort-first": {
            "campusCasual": 4,
            "sporty": 2,
        },
        "comfort-balanced": {
            "minimalist": 3,
            "campusCasual": 2,
        },
        "expression-balanced": {
            "streetwear": 2,
            "romantic": 2,
            "quietLuxury": 1,
        },
        "expression-first": {
            "y2k": 3,
            "streetwear": 3,
            "romantic": 1,
        },
    },
    "occasion-priority": {
        "campus-priority": {
            "campusCasual": 4,
            "streetwear": 1,
        },
        "work-priority": {
            "quietLuxury": 3,
            "minimalist": 3,
        },
        "party-priority": {
            "y2k": 3,
            "streetwear": 2,
            "romantic": 1,
        },
        "everyday-priority": {
            "minimalist": 3,
            "campusCasual": 3,
        },
    },
    "shopping-motivation": {
        "versatility-first": {
            "minimalist": 4,
            "campusCasual": 2,
        },
        "trend-discovery": {
            "y2k": 3,
            "streetwear": 2,
        },
        "statement-pieces": {
            "streetwear": 3,
            "romantic": 2,
            "y2k": 1,
        },
        "quality-first": {
            "quietLuxury": 4,
            "minimalist": 2,
        },
    },
    "fashion-goal": {
        "refine-signature": {
            "quietLuxury": 2,
            "minimalist": 2,
        },
        "experiment-more": {
            "y2k": 2,
            "streetwear": 2,
            "bohemian": 1,
        },
        "build-wardrobe": {
            "minimalist": 3,
            "campusCasual": 2,
        },
        "shop-smarter": {
            "minimalist": 3,
            "quietLuxury": 1,
        },
    },
}


@dataclass(frozen=True)
class FeatureBundle:
    scores: dict[str, float]
    preference_updates: dict[str, Any]
    quiz_answer_count: int


def _answer_map(
    answers: list[DNAQuizAnswer],
) -> dict[str, str]:
    mapped = {
        answer.question_id: answer.choice_id
        for answer in answers
    }

    if set(mapped) != EXPECTED_QUESTION_IDS:
        missing = sorted(
            EXPECTED_QUESTION_IDS - set(mapped),
        )
        unexpected = sorted(
            set(mapped) - EXPECTED_QUESTION_IDS,
        )

        raise ValueError(
            "Invalid quiz questions. "
            f"Missing: {missing}. "
            f"Unexpected: {unexpected}."
        )

    return mapped


def _build_preference_updates(
    answers: dict[str, str],
) -> dict[str, Any]:
    aesthetic_map = {
        "minimal-campus": [
            "minimalist",
            "campusCasual",
        ],
        "street-ready": [
            "streetwear",
            "y2k",
        ],
        "soft-romantic": [
            "romantic",
            "bohemian",
        ],
        "quiet-luxury": [
            "quietLuxury",
            "minimalist",
        ],
    }

    fit_map = {
        "relaxed-fit": ["relaxed"],
        "oversized-fit": ["oversized"],
        "regular-fit": ["regular"],
        "fitted-fit": ["fitted"],
    }

    brand_map = {
        "clean-premium": [
            "Mango",
            "ONLY",
        ],
        "youth-street": [
            "Roadster",
            "HIGHLANDER",
        ],
        "sporty-active": [
            "Puma",
            "HRX",
        ],
        "expressive-trend": [
            "Sassafras",
            "Tokyo Talkies",
        ],
    }

    colour_map = {
        "neutral-palette": [
            "black",
            "white",
            "beige",
            "grey",
        ],
        "earthy-palette": [
            "brown",
            "olive",
            "rust",
            "cream",
        ],
        "pastel-palette": [
            "lavender",
            "pink",
            "sky blue",
            "mint",
        ],
        "bold-palette": [
            "red",
            "cobalt",
            "orange",
            "magenta",
        ],
    }

    balance_map = {
        "comfort-first": 0.0,
        "comfort-balanced": 0.35,
        "expression-balanced": 0.65,
        "expression-first": 1.0,
    }

    occasion_map = {
        "campus-priority": {
            "preferred": ["campus", "casual"],
            "priorities": {
                "campus": 1.0,
                "casual": 0.8,
            },
        },
        "work-priority": {
            "preferred": [
                "work",
                "interview",
            ],
            "priorities": {
                "work": 1.0,
                "interview": 0.9,
            },
        },
        "party-priority": {
            "preferred": [
                "party",
                "night-out",
            ],
            "priorities": {
                "party": 1.0,
                "night-out": 0.9,
            },
        },
        "everyday-priority": {
            "preferred": [
                "everyday",
                "casual",
            ],
            "priorities": {
                "everyday": 1.0,
                "casual": 0.8,
            },
        },
    }

    goal_map = {
        "refine-signature": "Refine my signature style",
        "experiment-more": "Experiment with new styles",
        "build-wardrobe": "Build a versatile wardrobe",
        "shop-smarter": "Make smarter purchase decisions",
    }

    balance = balance_map[
        answers["comfort-expression"]
    ]

    occasion = occasion_map[
        answers["occasion-priority"]
    ]

    return {
        "preferred_aesthetics": aesthetic_map[
            answers["everyday-look"]
        ],
        "fit_preferences": fit_map[
            answers["silhouette"]
        ],
        "preferred_brands": brand_map[
            answers["brand-personality"]
        ],
        "preferred_colours": colour_map[
            answers["colour-palette"]
        ],
        "comfort_expression_balance": balance,
        "comfort_priority": round(
            1.0 - balance,
            2,
        ),
        "trend_openness": round(
            balance,
            2,
        ),
        "preferred_occasions": occasion[
            "preferred"
        ],
        "occasion_priorities": occasion[
            "priorities"
        ],
        "fashion_goal": goal_map[
            answers["fashion-goal"]
        ],
    }


def build_feature_bundle(
    answers: list[DNAQuizAnswer],
) -> FeatureBundle:
    mapped_answers = _answer_map(answers)
    scores: dict[str, float] = defaultdict(float)

    for question_id, choice_id in (
        mapped_answers.items()
    ):
        question_choices = (
            QUESTION_STYLE_WEIGHTS.get(question_id)
        )

        if (
            question_choices is None
            or choice_id not in question_choices
        ):
            raise ValueError(
                "Unknown answer choice "
                f"'{choice_id}' for "
                f"'{question_id}'."
            )

        for style, weight in (
            question_choices[choice_id].items()
        ):
            scores[style] += weight

    return FeatureBundle(
        scores=dict(scores),
        preference_updates=(
            _build_preference_updates(
                mapped_answers,
            )
        ),
        quiz_answer_count=len(answers),
    )