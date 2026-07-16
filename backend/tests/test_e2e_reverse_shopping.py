import json
from ml import generate_outfit_nlp

def test_reverse_shopping_e2e():
    products = [
        {"id": 1, "category": "top", "price": 500, "tags": ["work", "shirt", "cotton"], "name": "White Shirt", "occasions": ["work"]},
        {"id": 2, "category": "bottom", "price": 1000, "tags": ["formal", "pants"], "name": "Black Pants", "occasions": ["work"]},
        {"id": 3, "category": "accessory", "price": 300, "tags": ["work", "watch"], "name": "Silver Watch", "occasions": ["work"]},
        {"id": 4, "category": "accessory", "price": 2000, "tags": ["work", "bag"], "name": "Leather Bag", "occasions": ["work"]}
    ]
    user_profile = {"dna": {"minimalist": 80}, "budget": "premium"}
    res = generate_outfit_nlp("Interview tomorrow under 2k", user_profile, products)
    assert res["within_budget"] == True
    assert res["parsed_intent"]["budget_total"] == 2000
    assert len(res["outfits"]) > 0

