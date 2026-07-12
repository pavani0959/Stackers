from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# These are the ML clusters we define as the "Ground Truth" aesthetics
# In a real model, this would be trained on thousands of user wardrobes
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
    "feminine": "feminine soft colorful floral elegant delicate"
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
    "feminine": "Soft & Feminine"
}

IDENTITY_MAP = {
    "minimalist+campusCasual": ("Campus Minimalist", "You keep it clean, you keep it real. Neutral tones, comfortable silhouettes."),
    "minimalist+quietLuxury": ("Quiet Luxury Minimalist", "You dress like you know things others don't. Subtle signals, refined taste."),
    "streetwear+bold": ("Bold Street Player", "You make a statement before you say a word. Fashion is your language."),
    "streetwear+y2k": ("Y2K Street Rebel", "Nostalgia with attitude. You're always 5 minutes ahead of the trend cycle."),
    "darkAcademia+vintage": ("Dark Scholar", "Structured, literary, moody. Your wardrobe tells stories."),
    "feminine+colorful": ("Soft Maximalist", "Playful, expressive, joyful. Your style is a mood board in motion.")
}

def calculate_dna_ml(user_tags_list: list):
    """
    Uses TF-IDF Vectorization and Cosine Similarity (Real ML) to match 
    user tags to predefined aesthetic clusters.
    """
    # 1. Prepare corpus
    cluster_names = list(AESTHETIC_PROFILES.keys())
    corpus = list(AESTHETIC_PROFILES.values())
    
    # Add user document to corpus
    user_document = " ".join(user_tags_list)
    corpus.append(user_document)
    
    # 2. Vectorize using TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    # 3. Calculate Cosine Similarity
    # Compare user document (last in matrix) with all clusters
    user_vector = tfidf_matrix[-1]
    cluster_vectors = tfidf_matrix[:-1]
    
    similarities = cosine_similarity(user_vector, cluster_vectors)[0]
    
    # 4. Normalize scores to percentages
    total_score = np.sum(similarities)
    if total_score == 0:
        total_score = 1  # prevent div by zero
        
    dna_results = {}
    for i, score in enumerate(similarities):
        pct = round((score / total_score) * 100)
        if pct > 0:
            dna_results[cluster_names[i]] = pct
            
    # Sort by highest match
    sorted_dna = sorted(dna_results.items(), key=lambda x: x[1], reverse=True)
    
    # Get Identity
    top1 = sorted_dna[0][0] if len(sorted_dna) > 0 else "minimalist"
    top2 = sorted_dna[1][0] if len(sorted_dna) > 1 else "campusCasual"
    
    key1 = f"{top1}+{top2}"
    key2 = f"{top2}+{top1}"
    
    identity_name, identity_desc = IDENTITY_MAP.get(
        key1, 
        IDENTITY_MAP.get(key2, (f"{AESTHETIC_LABELS.get(top1, top1)} Explorer", f"Your style is a unique blend of {AESTHETIC_LABELS.get(top1, top1)} and {AESTHETIC_LABELS.get(top2, top2)}."))
    )
    
    top_bars = [
        {"tag": k, "label": AESTHETIC_LABELS.get(k, k), "percentage": v}
        for k, v in sorted_dna[:4]
    ]
    
    return {
        "dna": dict(sorted_dna),
        "identity": {
            "name": identity_name,
            "desc": identity_desc
        },
        "topBars": top_bars
    }

from datetime import datetime

BUDGET_TIERS = ['budget-explorer', 'smart-spender', 'campus-casual', 'style-investor', 'luxury-seeker']

def calc_confidence_ml(product: dict, user_profile: dict):
    """
    ML-assisted Recommender Engine:
    Style match uses cosine similarity.
    Other metrics use weighted rules.
    """
    # 1. Style Match (ML Cosine Similarity)
    user_dna = user_profile.get('dna', {})
    user_top_tags = [k for k, v in user_dna.items() if v > 20]
    
    prod_tags = product.get('tags', [])
    
    if not user_top_tags or not prod_tags:
        style_match = 70
    else:
        # Use TFIDF cosine similarity to match product tags to user's DNA tags
        corpus = [" ".join(user_top_tags), " ".join(prod_tags)]
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(corpus)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        style_match = min(100, int(round((similarity * 100) + 30))) # Base boost for aesthetics
    
    # 2. Occasion Match
    user_occasions = user_profile.get('occasions', [])
    prod_occasions = product.get('occasions', [])
    occ_overlap = len(set(user_occasions).intersection(set(prod_occasions)))
    
    if occ_overlap > 0:
        occasion_match = min(100, int(round((occ_overlap / max(len(prod_occasions), 1)) * 100 + 15)))
    else:
        occasion_match = 40
        
    # 3. Budget Match
    user_budget = user_profile.get('budget', 'campus-casual')
    prod_budget = product.get('budgetTier', 'campus-casual')
    try:
        user_idx = BUDGET_TIERS.index(user_budget)
        prod_idx = BUDGET_TIERS.index(prod_budget)
        diff = abs(user_idx - prod_idx)
        budget_match = 95 if diff == 0 else (80 if diff == 1 else 60)
    except ValueError:
        budget_match = 80
        
    # 4. Weather Match
    month = datetime.now().month
    is_summer = month >= 3 and month <= 8
    prod_season = product.get('season', 'all')
    
    if prod_season == 'all':
        weather_match = 90
    elif (prod_season == 'summer' and is_summer) or (prod_season == 'winter' and not is_summer):
        weather_match = 92
    else:
        weather_match = 72
        
    # 5. Wardrobe Match
    memory = user_profile.get('purchaseMemory', [])
    memory_tags = []
    for item in memory:
        memory_tags.extend(item.get('tags', []))
        
    wardrobe_overlap = len(set(prod_tags).intersection(set(memory_tags)))
    if memory:
        wardrobe_match = min(100, int(round((wardrobe_overlap / max(len(prod_tags), 1)) * 100 + 20)))
    else:
        wardrobe_match = 75
        
    overall = int(round((style_match + occasion_match + budget_match + weather_match + wardrobe_match) / 5))
    
    return {
        "overall": overall,
        "styleMatch": style_match,
        "occasionMatch": occasion_match,
        "budgetMatch": budget_match,
        "weatherMatch": weather_match,
        "wardrobeMatch": wardrobe_match
    }

def generate_outfit_nlp(prompt: str, user_profile: dict, all_products: list):
    """
    NLP Engine for Reverse Shopping.
    Returns 3 complete outfit suggestions (each = 1 Top + 1 Bottom + 1 Accessory).
    """
    if not all_products:
        return []
        
    # 1. Vectorize the product tags
    product_docs = [" ".join(p["tags"]) + " " + " ".join(p["occasions"]) + " " + p["name"].lower() for p in all_products]
    corpus = product_docs + [prompt.lower()]
    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    # 2. Calculate semantic similarity to the prompt
    prompt_vector = tfidf_matrix[-1]
    product_vectors = tfidf_matrix[:-1]
    similarities = cosine_similarity(prompt_vector, product_vectors)[0]
    
    # 3. Score all products
    scored_products = []
    for i, p in enumerate(all_products):
        nlp_score = int(round(similarities[i] * 100))
        dna_conf = calc_confidence_ml(p, user_profile)
        final_score = int(round((nlp_score * 0.6) + (dna_conf["overall"] * 0.4)))
        
        name_lower = p["name"].lower()
        category = "accessory"
        if any(w in name_lower for w in ["tee", "shirt", "hoodie", "blazer", "top", "sweater", "kurta", "bralette", "jacket"]):
            category = "top"
        elif any(w in name_lower for w in ["pants", "jeans", "trousers", "shorts", "cargo"]):
            category = "bottom"
            
        p_out = p.copy()
        p_out["confidence"] = dna_conf
        p_out["nlp_score"] = nlp_score
        p_out["final_score"] = final_score
        p_out["category"] = category
        scored_products.append(p_out)
        
    scored_products.sort(key=lambda x: x["final_score"], reverse=True)
    
    # 4. Separate by category
    tops = [p for p in scored_products if p["category"] == "top"]
    bottoms = [p for p in scored_products if p["category"] == "bottom"]
    accessories = [p for p in scored_products if p["category"] == "accessory"]
    
    # Fallback if any category empty
    if not tops: tops = scored_products[:3]
    if not bottoms: bottoms = scored_products[3:6]
    if not accessories: accessories = scored_products[6:9]
    
    # 5. Build 3 outfits
    outfits = []
    num_outfits = min(3, len(tops), len(bottoms), len(accessories))
    
    for i in range(num_outfits):
        outfit_score = int(round((tops[i]["final_score"] + bottoms[i]["final_score"] + accessories[i]["final_score"]) / 3))
        for item in [tops[i], bottoms[i], accessories[i]]:
            item_copy = item.copy()
            item_copy["outfit_index"] = i + 1
            item_copy["outfit_score"] = outfit_score
            outfits.append(item_copy)
    
    # Ensure at least 3 items always returned
    if len(outfits) < 3:
        used_ids = {p["id"] for p in outfits}
        for p in scored_products:
            if p["id"] not in used_ids:
                p_copy = p.copy()
                p_copy["outfit_index"] = 1
                p_copy["outfit_score"] = p["final_score"]
                outfits.append(p_copy)
            if len(outfits) >= 3:
                break
                
    return outfits

def blend_dna(user_dna: dict, creator_dna: dict, blend_pct: int):
    """
    ML Vector Math: Blends a percentage of the creator's DNA into the user's DNA.
    """
    user_weight = (100 - blend_pct) / 100.0
    creator_weight = blend_pct / 100.0
    
    merged_dna = {}
    all_keys = set(user_dna.keys()).union(set(creator_dna.keys()))
    
    for key in all_keys:
        u_val = user_dna.get(key, 0)
        c_val = creator_dna.get(key, 0)
        merged_val = (u_val * user_weight) + (c_val * creator_weight)
        if merged_val > 5:  # Threshold to keep it clean
            merged_dna[key] = int(round(merged_val))
            
    # Normalize to 100% just in case
    total = sum(merged_dna.values())
    if total > 0:
        merged_dna = {k: int(round((v / total) * 100)) for k, v in merged_dna.items()}
        
    return merged_dna

def find_twins(user_dna: dict, all_profiles: list):
    """
    Uses Cosine Similarity to find community profiles with the closest DNA match to the user.
    """
    if not all_profiles:
        return []
        
    user_tags = [k for k, v in user_dna.items() if v > 15]
    if not user_tags:
        return all_profiles[:3]
        
    user_doc = " ".join(user_tags)
    
    docs = []
    for prof in all_profiles:
        import json
        try:
            prof_dna = json.loads(prof.dna_json)
            docs.append(" ".join([k for k, v in prof_dna.items() if v > 15]))
        except:
            docs.append("")
            
    corpus = docs + [user_doc]
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    user_vector = tfidf_matrix[-1]
    prof_vectors = tfidf_matrix[:-1]
    similarities = cosine_similarity(user_vector, prof_vectors)[0]
    
    scored_profiles = []
    for i, prof in enumerate(all_profiles):
        match_pct = int(round(similarities[i] * 100))
        scored_profiles.append({
            "profile": prof,
            "match": match_pct
        })
        
    scored_profiles.sort(key=lambda x: x["match"], reverse=True)
    return scored_profiles

def muse_chat_response(message: str, user_profile: dict) -> str:
    """
    NLP intent matching for Myntra Muse Chatbot.
    """
    lower = message.lower()
    identity = user_profile.get("identityName", "Minimalist")
    dna = user_profile.get("dna", {})
    
    if "recommend" in lower or "what should i wear" in lower:
        return f"Based on your Fashion DNA, you have a {dna.get('Streetwear', 30)}% affinity for Streetwear. I'd recommend checking out your Home feed—I just updated it!"
    elif "return" in lower or "regret" in lower:
        return "I noticed you returned that bright jacket recently. That item was only a 58% match for your DNA. Next time, look for items above 85% confidence to prevent regret!"
    elif "party" in lower or "night out" in lower:
        return f"For a party, let's stick to your {identity} vibe. I'd suggest a dark, sleek silhouette. Try Reverse Shopping and type 'Night out' to see the NLP outfits!"
    else:
        return "I love that idea! Since you match highly with streetwear and minimalism, I suggest layering with oversized basics."
