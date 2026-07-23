from services.intent_parser import extract_intent

def test_intent_parser():
    res = extract_intent("College fest Saturday, retro theme, ₹2,000 total.")
    assert res["budget_total"] == 2000
    assert res["occasion"] == "college_fest"
    assert "retro" in res["theme"]
    
    res = extract_intent("Interview tomorrow under 2k")
    assert res["budget_total"] == 2000
    assert res["occasion"] == "interview"
    
    res = extract_intent("gym clothes maximum 3000")
    assert res["budget_total"] == 3000
    assert res["occasion"] == "workout"
    
def test_budget_variations():
    budgets = [
        ("₹2000", 2000),
        ("Rs 2000", 2000),
        ("under 2k", 2000),
        ("below 1500", 1500),
        ("maximum 3000", 3000),
        ("budget is 2500", 2500),
    ]
    for prompt, expected in budgets:
        res = extract_intent(f"outfit for party {prompt}")
        assert res["budget_total"] == expected, f"Failed for prompt: {prompt}"

