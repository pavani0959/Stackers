from services.outfit_builder import build_outfits

def test_build_outfits():
    intent = {"budget_total": 2000, "occasion": "interview"}
    products = [
        {"id": 1, "category": "top", "price": 500, "tags": ["work"]},
        {"id": 2, "category": "bottom", "price": 1000, "tags": ["formal"]},
        {"id": 3, "category": "accessory", "price": 300, "tags": ["work"]},
        {"id": 4, "category": "accessory", "price": 2000, "tags": ["work"]}
    ]
    res = build_outfits(intent, products, 3000)
    assert len(res["outfits"]) > 0
    # The expensive accessory should be filtered out
    for outfit in res["outfits"]:
        assert outfit["total_price"] <= 2000
