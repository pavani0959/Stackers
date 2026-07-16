import re

def parse_budget(prompt: str) -> int | None:
    """Extract budget from strings like ₹2000, Rs 2000, under 2k, maximum 3000."""
    prompt_lower = prompt.lower()
    
    # Check for "under Xk" or "Xk"
    k_match = re.search(r'(\d+(?:\.\d+)?)\s*k\b', prompt_lower)
    if k_match:
        return int(float(k_match.group(1)) * 1000)
    
    # Check for ₹XXXX or Rs XXXX or budget is XXXX
    num_match = re.search(r'(?:₹|rs\.?|rupees|budget(?:\s+is)?\s*)\s*(\d+(?:,\d+)*)', prompt_lower)
    if num_match:
        return int(num_match.group(1).replace(',', ''))
    
    # General fallback for standalone large numbers (e.g., 1500, 2000)
    # Only pick up reasonable budget numbers between 500 and 50000
    gen_match = re.findall(r'\b(\d{3,5})\b', prompt_lower)
    if gen_match:
        for match in gen_match:
            val = int(match)
            if 500 <= val <= 50000:
                return val
            
    return None

def parse_occasion(prompt: str) -> str | None:
    """Map synonyms to standard occasion tags."""
    prompt_lower = prompt.lower()
    mapping = {
        "interview": "interview",
        "office presentation": "work_formal",
        "office": "work_casual",
        "college fest": "college_fest",
        "college": "campus",
        "date": "date_casual",
        "wedding": "wedding_guest",
        "night out": "party",
        "party": "party",
        "beach": "vacation",
        "gym": "workout",
        "workout": "workout"
    }
    for keyword, standard_occasion in mapping.items():
        if keyword in prompt_lower:
            return standard_occasion
    return None

def parse_themes(prompt: str) -> list[str]:
    prompt_lower = prompt.lower()
    themes = ["retro", "minimal", "minimalist", "streetwear", "traditional", "formal", "smart casual", "y2k", "quiet luxury"]
    found = []
    for theme in themes:
        if theme in prompt_lower:
            found.append(theme)
    # normalize minimal -> minimalist
    if "minimal" in found and "minimalist" not in found:
        found.remove("minimal")
        found.append("minimalist")
    return found

def extract_intent(prompt: str) -> dict:
    """Extract structured intent from raw prompt."""
    return {
        "occasion": parse_occasion(prompt),
        "theme": parse_themes(prompt),
        "budget_total": parse_budget(prompt),
        "dress_code": None,
        "location": None,
        "preferred_colours": [],
        "excluded_categories": []
    }
