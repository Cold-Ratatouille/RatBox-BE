from app.agent.services import search_service
from app.domain.models import RecipeCandidate


def test_search_recipes_returns_empty_when_no_recipe_ids(monkeypatch):
    monkeypatch.setattr(
        search_service, "find_recipe_ingredient_matches", lambda ids: {}
    )

    result = search_service.search_recipes(["없는재료-id"], min_match=1, limit=20)

    assert result == []


def test_search_recipes_filters_by_min_match_and_sorts_by_match_count(monkeypatch):
    matches = {
        "1": ["계란"],  # match_count=1 -> min_match=2 미달, 제외
        "2": ["계란", "대파"],  # match_count=2
        "3": ["계란", "대파", "양파"],  # match_count=3
    }
    monkeypatch.setattr(
        search_service, "find_recipe_ingredient_matches", lambda ids: matches
    )
    monkeypatch.setattr(
        search_service,
        "get_recipes_by_ids",
        lambda ids: [
            {"id": "2", "name": "대파계란찜", "cooking_time": 15},
            {"id": "3", "name": "삼색나물", "cooking_time": 20},
        ],
    )

    result = search_service.search_recipes(
        ["계란", "대파", "양파"], min_match=2, limit=20
    )

    assert [c.id for c in result] == ["3", "2"]


def test_search_recipes_respects_limit(monkeypatch):
    monkeypatch.setattr(
        search_service,
        "find_recipe_ingredient_matches",
        lambda ids: {"1": ["계란"], "2": ["계란"], "3": ["계란"]},
    )
    monkeypatch.setattr(
        search_service,
        "get_recipes_by_ids",
        lambda ids: [RecipeCandidate(id=i, name=f"레시피{i}").model_dump() for i in ids],
    )

    result = search_service.search_recipes(["계란"], min_match=1, limit=2)

    assert len(result) == 2
