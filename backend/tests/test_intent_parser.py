from services.intent_parser import extract_intent

def test_intent_parser():
    res = extract_intent("College fest Saturday, retro theme, ₹2,000 total.")
    assert res["budget_total"] == 2000
    assert res["occasion"] == "college_fest"
    assert "retro" in res["theme"]
    
    res = extract_intent("Interview tomorrow under 2k")
    assert res["budget_total"] == 2000
    assert res["occasion"] == "interview"
    
    res = extract_intent("gym clothes maximum 1500")
    assert res["budget_total"] == 1500
    assert res["occasion"] == "workout"
