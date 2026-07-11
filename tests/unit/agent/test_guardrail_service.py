from app.agent.services.guardrail_service import check_substitute_conflict, filter_allergens


def test_filter_allergens_excludes_matching_recipes():
    recipes = [
        {"name": "새우볶음", "ingredients": ["새우", "밥"]},
        {"name": "계란밥", "ingredients": ["계란", "밥"]},
    ]
    filtered = filter_allergens(recipes, ["새우"])
    assert [r["name"] for r in filtered] == ["계란밥"]


def test_check_substitute_conflict_detects_allergen_match():
    assert check_substitute_conflict("새우", ["새우", "우유"]) is True


def test_check_substitute_conflict_returns_false_when_safe():
    assert check_substitute_conflict("소금", ["새우", "우유"]) is False
