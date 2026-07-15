from app.agent.services import recipe_service
from app.domain.models import RecipeCandidate


def _patch_ingredients(monkeypatch, by_id: dict):
    monkeypatch.setattr(
        recipe_service, "get_recipe_ingredient_names", lambda recipe_id: by_id[recipe_id]
    )


def test_rank_candidates_excludes_allergen_recipes(monkeypatch):
    _patch_ingredients(
        monkeypatch,
        {
            "1": [{"name": "새우", "is_required": True}, {"name": "밥", "is_required": True}],
            "2": [{"name": "계란", "is_required": True}, {"name": "밥", "is_required": True}],
        },
    )
    candidates = [
        RecipeCandidate(id="1", name="새우볶음밥"),
        RecipeCandidate(id="2", name="계란밥"),
    ]

    ranked = recipe_service.rank_candidates(candidates, ["밥"], allergies=["새우"])

    assert [c.id for c in ranked] == ["2"]


def test_rank_candidates_sorts_by_missing_count_ascending(monkeypatch):
    _patch_ingredients(
        monkeypatch,
        {
            "1": [{"name": "계란", "is_required": True}, {"name": "대파", "is_required": True}],
            "2": [{"name": "계란", "is_required": True}],
        },
    )
    candidates = [
        RecipeCandidate(id="1", name="대파계란찜"),
        RecipeCandidate(id="2", name="계란밥"),
    ]

    ranked = recipe_service.rank_candidates(candidates, ["계란"], allergies=[])

    assert [c.id for c in ranked] == ["2", "1"]
    assert ranked[0].missing_ingredients == []
    assert ranked[1].missing_ingredients == ["대파"]
    # verify_relevance가 "왜 매칭됐는지" 볼 수 있도록 겹치는 재료도 같이 채워야 한다.
    assert ranked[0].matched_ingredients == ["계란"]
    assert ranked[1].matched_ingredients == ["계란"]


def test_rank_candidates_limits_to_top_three(monkeypatch):
    _patch_ingredients(
        monkeypatch, {str(i): [{"name": "계란", "is_required": True}] for i in range(1, 6)}
    )
    candidates = [RecipeCandidate(id=str(i), name=f"레시피{i}") for i in range(1, 6)]

    ranked = recipe_service.rank_candidates(candidates, ["계란"], allergies=[])

    assert len(ranked) == 3
