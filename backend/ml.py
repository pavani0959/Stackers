import re
from datetime import datetime
from itertools import product as cartesian_product

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from services.intent_parser import extract_intent
from services.outfit_builder import build_outfits

# These are the ML clusters we define as the "Ground Truth" aesthetics.
AESTHETIC_PROFILES = {
    "minimalist": "minimalist neutral clean quietLuxury smart basic everyday",
    "streetwear": "streetwear bold baggy casual cool sneakers y2k hype",
    "campusCasual": "campusCasual comfortable easy basic casual everyday smart",
    "quietLuxury": "quietLuxury elegant refined neutral expensive smart classic",
    "y2k": "y2k colorful bold retro nostalgic bright statement",
    "darkAcademia": "darkAcademia moody intellectual vintage classic cozy brown",
    "vintage": "vintage classic retro nostalgic old-school denim",
    "colorful": "colorful bold bright statement neon pop",
    "bold": "bold statement expressive unique confident",
    "feminine": "feminine soft colorful floral elegant delicate",
}

AESTHETIC_LABELS = {
    "minimalist": "Minimalist",
    "streetwear": "Streetwear",
    "campusCasual": "Campus Casual",
    "quietLuxury": "Quiet Luxury",
    "y2k": "Y2K",
    "darkAcademia": "Dark Academia",
    "vintage": "Vintage",
    "colorful": "Colorful",
    "bold": "Bold & Expressive",
    "feminine": "Soft & Feminine",
}

IDENTITY_MAP = {
    "minimalist+campusCasual": (
        "Campus Minimalist",
        "You keep it clean, you keep it real. Neutral tones, comfortable silhouettes.",
    ),
    "minimalist+quietLuxury": (
        "Quiet Luxury Minimalist",
        "You dress like you know things others don't. Subtle signals, refined taste.",
    ),
    "streetwear+bold": (
        "Bold Street Player",
        "You make a statement before you say a word. Fashion is your language.",
    ),
    "streetwear+y2k": (
        "Y2K Street Rebel",
        "Nostalgia with attitude. You're always 5 minutes ahead of the trend cycle.",
    ),
    "darkAcademia+vintage": (
        "Dark Scholar",
        "Structured, literary, moody. Your wardrobe tells stories.",
    ),
    "feminine+colorful": (
        "Soft Maximalist",
        "Playful, expressive, joyful. Your style is a mood board in motion.",
    ),
}

BUDGET_TIERS = [
    "budget-explorer",
    "smart-spender",
    "campus-casual",
    "style-investor",
    "luxury-seeker",
]

# The onboarding budget is described as a complete-outfit budget.
PROFILE_BUDGET_LIMITS = {
    "budget-explorer": 500,
    "smart-spender": 1500,
    "campus-casual": 3000,
    "style-investor": 7000,
    "luxury-seeker": 15000,
}

# Query concepts bridge natural phrases such as "college" and "classy" to
# the vocabulary used by the product catalogue.
QUERY_CONCEPTS = [
    {
        "triggers": {"interview", "office", "internship", "professional", "formal"},
        "tags": {"smart", "formal", "classic", "minimalist", "neutral", "quietluxury"},
        "occasions": {"work"},
    },
    {
        "triggers": {"college", "campus", "class", "lecture"},
        "tags": {"campuscasual", "casual", "comfort", "comfortable", "everyday", "clean"},
        "occasions": {"campus"},
    },
    {
        "triggers": {"fest", "festival", "concert", "retro", "y2k"},
        "tags": {"y2k", "vintage", "retro", "bold", "colorful", "streetwear", "statement"},
        "occasions": {"fest", "concerts"},
    },
    {
        "triggers": {"date", "cafe", "cute", "romantic"},
        "tags": {"feminine", "elegant", "soft", "casual", "quietluxury"},
        "occasions": {"dates", "cafe"},
    },
    {
        "triggers": {"party", "night", "club", "bold"},
        "tags": {"bold", "statement", "elegant", "quietluxury", "colorful"},
        "occasions": {"night-out"},
    },
    {
        "triggers": {"gym", "workout", "running", "sports", "athletic"},
        "tags": {"sporty", "athletic", "comfort", "casual"},
        "occasions": {"gym"},
    },
    {
        "triggers": {"puja", "traditional", "ethnic", "family"},
        "tags": {"ethnic", "traditional", "festive", "colorful"},
        "occasions": {"puja", "festivals", "family"},
    },
    {
        "triggers": {"classy", "elegant", "luxury", "refined"},
        "tags": {"quietluxury", "elegant", "smart", "classic", "neutral"},
        "occasions": set(),
    },
    {
        "triggers": {"minimal", "minimalist", "clean", "simple"},
        "tags": {"minimalist", "clean", "neutral", "everyday"},
        "occasions": set(),
    },
    {
        "triggers": {"street", "streetwear", "oversized", "baggy"},
        "tags": {"streetwear", "bold", "casual", "y2k"},
        "occasions": set(),
    },
]

BOTTOM_KEYWORDS = {"pants", "jeans", "trousers", "shorts", "cargo", "skirt"}

PROMPT_STOP_WORDS = {
    "a", "an", "and", "at", "be", "for", "from", "i", "in", "is", "it",
    "look", "me", "my", "of", "on", "or", "outfit", "please", "the", "to",
    "tomorrow", "want", "with", "friends", "saturday", "day",
}

ACCESSORY_KEYWORDS = {
    "bag",
    "tote",
    "watch",
    "earrings",
    "sneakers",
    "shoes",
    "heels",
    "sandals",
}





def calc_confidence_ml(product: dict, user_profile: dict):
    """Calculate explainable recommendation confidence for one product."""
    user_dna = user_profile.get("dna", {})
    user_top_tags = [key for key, value in user_dna.items() if value > 20]
    product_tags = product.get("tags", [])

    if not user_top_tags or not product_tags:
        style_match = 70
    else:
        corpus = [" ".join(user_top_tags), " ".join(product_tags)]
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(corpus)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        style_match = min(100, int(round((similarity * 100) + 30)))

    user_occasions = user_profile.get("occasions", [])
    product_occasions = product.get("occasions", [])
    occasion_overlap = len(set(user_occasions).intersection(product_occasions))
    if occasion_overlap > 0:
        occasion_match = min(
            100,
            int(round((occasion_overlap / max(len(product_occasions), 1)) * 100 + 15)),
        )
    else:
        occasion_match = 40

    user_budget = user_profile.get("budget", "campus-casual")
    product_budget = product.get("budgetTier", "campus-casual")
    try:
        difference = abs(BUDGET_TIERS.index(user_budget) - BUDGET_TIERS.index(product_budget))
        budget_match = 95 if difference == 0 else (80 if difference == 1 else 60)
    except ValueError:
        budget_match = 80

    month = datetime.now().month
    is_summer = 3 <= month <= 8
    product_season = product.get("season", "all")
    if product_season == "all":
        weather_match = 90
    elif (product_season == "summer" and is_summer) or (
        product_season == "winter" and not is_summer
    ):
        weather_match = 92
    else:
        weather_match = 72

    memory = user_profile.get("purchaseMemory", [])
    memory_tags = []
    for item in memory:
        memory_tags.extend(item.get("tags", []))

    wardrobe_overlap = len(set(product_tags).intersection(memory_tags))
    if memory:
        wardrobe_match = min(
            100,
            int(round((wardrobe_overlap / max(len(product_tags), 1)) * 100 + 20)),
        )
    else:
        wardrobe_match = 75

    overall = int(
        round(
            (
                style_match
                + occasion_match
                + budget_match
                + weather_match
                + wardrobe_match
            )
            / 5
        )
    )

    return {
        "overall": overall,
        "styleMatch": style_match,
        "occasionMatch": occasion_match,
        "budgetMatch": budget_match,
        "weatherMatch": weather_match,
        "wardrobeMatch": wardrobe_match,
    }


def _canonical(value: str) -> str:
    """Convert camelCase and punctuation into a stable lowercase token."""
    with_spaces = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value or "")
    return re.sub(r"[^a-z0-9]+", "", with_spaces.lower())


def _words(value: str) -> set[str]:
    with_spaces = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value or "")
    return set(re.findall(r"[a-z0-9]+", with_spaces.lower()))


def _contains_trigger(prompt_lower: str, prompt_words: set[str], trigger: str) -> bool:
    if " " in trigger or "-" in trigger:
        return trigger in prompt_lower
    return trigger in prompt_words


def analyse_prompt(prompt: str) -> dict:
    prompt_lower = prompt.lower().strip()
    prompt_words = _words(prompt_lower)
    tags = set()
    occasions = set()
    matched_terms = set()

    for concept in QUERY_CONCEPTS:
        matching_triggers = {
            trigger
            for trigger in concept["triggers"]
            if _contains_trigger(prompt_lower, prompt_words, trigger)
        }
        if matching_triggers:
            matched_terms.update(matching_triggers)
            tags.update(concept["tags"])
            occasions.update(concept["occasions"])

    # Preserve only meaningful free-text words. Stop words and budget numbers
    # would dilute the actual fashion concepts in a short prompt.
    tags.update(
        _canonical(word)
        for word in prompt_words
        if len(word) > 2 and word not in PROMPT_STOP_WORDS and not word.isdigit()
    )

    # Context priority: "college interview" is an interview, and "college fest"
    # is a fest. Do not let the word college turn either into a campus-day query.
    if "interview" in matched_terms or "formal" in matched_terms:
        occasions.discard("campus")
        tags.difference_update({"campuscasual", "comfort", "comfortable"})
    elif "fest" in matched_terms or "festival" in matched_terms or "concert" in matched_terms:
        occasions.discard("campus")
        tags.discard("campuscasual")

    return {
        "tags": tags,
        "occasions": occasions,
        "matched_terms": sorted(matched_terms),
        "expanded_document": " ".join(sorted(tags.union(occasions).union(prompt_words))),
    }


def parse_budget_limit(prompt: str) -> int | None:
    """Parse ₹1500, 1,500, 1.5k, 'budget 2000', or 'under 2k'."""
    lowered = prompt.lower().replace(",", "")

    explicit_patterns = [
        r"(?:₹|rs\.?|inr)\s*(\d+(?:\.\d+)?)\s*(k)?",
        r"(?:budget|under|below|within|upto|up to|max(?:imum)?)\s*(?:of|is|:|-)?\s*"
        r"(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(k)?",
        r"(\d+(?:\.\d+)?)\s*(k)\s*(?:budget|rupees?|inr)?",
    ]

    for pattern in explicit_patterns:
        match = re.search(pattern, lowered)
        if not match:
            continue
        value = float(match.group(1))
        if match.group(2):
            value *= 1000
        return max(1, int(round(value)))

    return None


def _profile_budget_limit(user_profile: dict) -> int:
    return PROFILE_BUDGET_LIMITS.get(user_profile.get("budget", "campus-casual"), 3000)


def classify_product(product: dict) -> str:
    name_words = _words(product.get("name", ""))
    tag_tokens = {_canonical(tag) for tag in product.get("tags", [])}

    if name_words.intersection(BOTTOM_KEYWORDS):
        return "bottom"
    if "accessory" in tag_tokens or name_words.intersection(ACCESSORY_KEYWORDS):
        return "accessory"
    return "top"


def _product_document(product: dict) -> str:
    fields = [
        product.get("name", ""),
        product.get("brand", ""),
        " ".join(product.get("tags", [])),
        " ".join(product.get("occasions", [])),
    ]
    return " ".join(fields).lower()


def rank_products_for_query(prompt: str, user_profile: dict, all_products: list) -> tuple[list, dict]:
    """Rank catalogue products using prompt concepts, TF-IDF, and Fashion DNA."""
    if not all_products:
        return [], analyse_prompt(prompt)

    analysis = analyse_prompt(prompt)
    product_documents = [_product_document(product) for product in all_products]
    query_document = analysis["expanded_document"] or prompt.lower() or "style"

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(product_documents + [query_document])
    similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]

    scored_products = []
    for index, product in enumerate(all_products):
        product_tags = {_canonical(tag) for tag in product.get("tags", [])}
        product_occasions = {_canonical(item) for item in product.get("occasions", [])}
        product_name_words = {_canonical(word) for word in _words(product.get("name", ""))}

        query_tags = analysis["tags"]
        query_occasions = {_canonical(item) for item in analysis["occasions"]}

        tag_overlap = len(query_tags.intersection(product_tags.union(product_name_words)))
        tag_score = int(round((tag_overlap / max(len(query_tags), 1)) * 100))

        occasion_overlap = len(query_occasions.intersection(product_occasions))
        occasion_score = 100 if occasion_overlap else (45 if not query_occasions else 0)

        nlp_score = int(round(similarities[index] * 100))
        confidence = calc_confidence_ml(product, user_profile)

        concept_score = int(round((tag_score * 0.65) + (occasion_score * 0.35)))
        final_score = int(
            round(
                (nlp_score * 0.35)
                + (concept_score * 0.40)
                + (confidence["overall"] * 0.25)
            )
        )

        # A direct occasion mismatch should not outrank a relevant item solely
        # because of the user's general DNA.
        if query_occasions and occasion_overlap == 0:
            final_score = max(0, final_score - 10)

        result = product.copy()
        result.update(
            {
                "confidence": confidence,
                "nlp_score": nlp_score,
                "final_score": final_score,
                "category": (
            product.get("category")
            or classify_product(product)
        ),
            }
        )
        scored_products.append(result)

    scored_products.sort(key=lambda item: (-item["final_score"], item["price"], item["id"]))
    return scored_products, analysis









def _format_price(value: int) -> str:
    return f"₹{value:,}"


def _display_style_key(key: str) -> str:
    return AESTHETIC_LABELS.get(key, re.sub(r"([a-z])([A-Z])", r"\1 \2", key).title())


def muse_chat_response(message: str, user_profile: dict, all_products: list) -> dict:
    """Return intent-aware, inventory-grounded Muse responses."""
    clean_message = message.strip()
    lower = clean_message.lower()
    words = _words(lower)
    name = user_profile.get("name", "").strip().split(" ")[0] or "Style Explorer"
    identity = user_profile.get("identityName", "").strip() or "your current Fashion DNA"
    memory = user_profile.get("purchaseMemory", [])

    greeting_words = {"hi", "hello", "hey", "hii", "hola"}
    if words and words.issubset(greeting_words.union({"muse"})):
        return {
            "reply": (
                f"Hi {name}! I’m Myntra Muse. I can use your {identity} profile and the "
                "live catalogue to recommend products, plan for an occasion, check a budget, "
                "or review your Fashion Memory."
            ),
            "intent": "greeting",
            "recommendations": [],
        }

    if any(phrase in lower for phrase in ("what can you do", "help me", "how can you help")):
        return {
            "reply": (
                "Ask me things like ‘interview outfit under ₹3000’, ‘what matches my DNA?’, "
                "‘show campus options’, or ‘review my latest purchase’. My suggestions come "
                "from the products currently stored in Myntra Identity."
            ),
            "intent": "help",
            "recommendations": [],
        }

    if any(term in words for term in {"dna", "identity", "aesthetic", "style"}) and not any(
        term in words for term in {"recommend", "suggest", "wear", "product", "outfit", "boring", "different", "opposite", "break", "anti"}
    ):
        dna = user_profile.get("dna", {})
        top_dna = sorted(dna.items(), key=lambda item: item[1], reverse=True)[:3]
        if top_dna:
            summary = ", ".join(
                f"{_display_style_key(key)} {value}%" for key, value in top_dna
            )
            reply = f"{name}, your identity is {identity}. Your strongest DNA signals are {summary}."
        else:
            reply = (
                f"{name}, I do not have your Fashion DNA yet. Complete the visual DNA quiz "
                "so I can personalise recommendations."
            )
        return {"reply": reply, "intent": "dna", "recommendations": []}

    if any(term in words for term in {"memory", "wardrobe", "purchased", "bought"}):
        named_memory = [item for item in memory if item.get("name")]
        if named_memory:
            recent = named_memory[:3]
            names = ", ".join(item["name"] for item in recent)
            reply = f"Your latest Fashion Memory items are {names}. I’ll avoid repeating them unless they strongly fit your request."
        else:
            reply = "Your Fashion Memory is empty right now. Use Buy All or buy a product to start building it."
        return {"reply": reply, "intent": "wardrobe", "recommendations": []}

    if any(term in words for term in {"return", "regret", "wrong", "bad"}):
        named_memory = [item for item in memory if item.get("name")]
        ranked, _ = rank_products_for_query(clean_message, user_profile, all_products)
        alternatives = ranked[:2]
        if named_memory:
            latest = named_memory[0]
            match_text = (
                f" with a recorded {latest.get('dnaMatch')}% DNA match"
                if latest.get("dnaMatch") is not None
                else ""
            )
            intro = f"Your latest saved purchase is {latest['name']}{match_text}."
        else:
            intro = "I cannot see a returned item in Fashion Memory yet."

        if alternatives:
            product_text = " or ".join(
                f"{item['name']} ({_format_price(item['price'])})" for item in alternatives
            )
            reply = f"{intro} For a safer next choice, compare it with {product_text}."
        else:
            reply = intro

        return {
            "reply": reply,
            "intent": "regret",
            "recommendations": alternatives,
        }

    if any(term in words for term in {"wishlist", "saved", "liked", "favourite", "hearted"}):
        return {
            "reply": (
                f"{name}, your Wishlist is accessible via the Profile tab (👤) in the bottom nav. "
                "Any product you heart (♡) on the product page is saved there with its DNA match score!"
            ),
            "intent": "wishlist",
            "recommendations": [],
        }

    if any(term in words for term in {"search", "find", "look", "browse"}) and not any(
        term in words for term in {"recommend", "outfit", "wear", "match"}
    ):
        return {
            "reply": (
                f"Tap the 🔍 Search tab in the bottom nav to search by name, brand, or keyword. "
                "You can also filter by category and sort by DNA Match to find the most compatible items!"
            ),
            "intent": "search",
            "recommendations": [],
        }

    if any(term in words for term in {"profile", "edit", "settings", "change", "update"}) and any(
        term in words for term in {"name", "budget", "occasion", "profile"}
    ):
        return {
            "reply": (
                f"Go to the 👤 Profile tab to update your name, budget range, and preferred occasions. "
                "Your Fashion DNA is calculated from your quiz answers and updates as you shop!"
            ),
            "intent": "profile",
            "recommendations": [],
        }

    if any(term in words for term in {"anti", "opposite", "different", "break", "boring", "explore", "experiment", "surprise"}) or "anti-trend" in lower or "anti trend" in lower:
        return {
            "reply": (
                f"{name}, go to your Home feed and toggle the 🔀 Anti-Trend Mode switch. "
                "It reverses the ML ranking and shows items with the lowest DNA match — "
                "perfect for breaking out of your style echo chamber!"
            ),
            "intent": "anti_trend",
            "recommendations": [],
        }

    # All remaining messages are treated as recommendation requests.
    ranked, analysis = rank_products_for_query(clean_message, user_profile, all_products)
    explicit_budget = parse_budget_limit(clean_message)
    budget_limit = explicit_budget or _profile_budget_limit(user_profile)
    affordable = [item for item in ranked if item["price"] <= budget_limit]
    recommendations = affordable[:3]

    if not recommendations:
        cheapest = min(ranked, key=lambda item: item["price"], default=None)
        if cheapest:
            reply = (
                f"{name}, I could not find a matching product within {_format_price(budget_limit)}. "
                f"The closest live-catalogue option is {cheapest['name']} at "
                f"{_format_price(cheapest['price'])}."
            )
            recommendations = [cheapest]
        else:
            reply = "The catalogue is empty right now, so I cannot make a grounded recommendation."
    else:
        product_text = ", ".join(
            f"{item['name']} ({_format_price(item['price'])})" for item in recommendations
        )
        context = (
            ", ".join(analysis["matched_terms"][:2])
            if analysis["matched_terms"]
            else identity
        )
        budget_text = (
            f" within your {_format_price(budget_limit)} limit"
            if explicit_budget
            else f" for your {identity} profile"
        )
        reply = (
            f"{name}, for {context}, the strongest live-catalogue matches are "
            f"{product_text}{budget_text}."
        )

    return {
        "reply": reply,
        "intent": "recommendation",
        "recommendations": recommendations,
    }
