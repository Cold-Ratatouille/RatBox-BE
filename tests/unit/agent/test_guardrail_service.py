from app.agent.services.guardrail_service import filter_allergens, is_blocked_input


def test_is_blocked_input_detects_keyword():
    assert is_blocked_input("이 바보야") is True
    assert is_blocked_input("계란있어") is False


def test_filter_allergens_excludes_matching_recipes():
    recipes = [
        {"name": "새우볶음", "ingredients": ["새우", "밥"]},
        {"name": "계란밥", "ingredients": ["계란", "밥"]},
    ]
    filtered = filter_allergens(recipes, ["새우"])
    assert [r["name"] for r in filtered] == ["계란밥"]
