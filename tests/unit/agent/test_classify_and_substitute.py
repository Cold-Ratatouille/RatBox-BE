from app.agent.nodes import classify_and_substitute as node_module
from app.agent.state import AgentState
from app.agent.tools.schemas import (
    ClassifyMissingOutput,
    FindSubstitutesOutput,
    GenerateCookingStepsOutput,
)
from app.domain.models import SubstituteCandidate


def test_returns_blocked_when_recipe_not_found(monkeypatch):
    monkeypatch.setattr(node_module, "get_recipe_by_id", lambda recipe_id: None)

    result = node_module.classify_and_substitute(
        AgentState(selected_ingredients=["계란"], recipe_id="missing")
    )

    assert result["guardrail_blocked"] is True


def test_skips_llm_calls_when_nothing_missing(monkeypatch):
    monkeypatch.setattr(
        node_module,
        "get_recipe_by_id",
        lambda recipe_id: {
            "id": "r1",
            "name": "계란밥",
            "cooking_time": 10,
            "difficulty": None,
            "category": None,
            "cooking_method": None,
        },
    )
    monkeypatch.setattr(
        node_module,
        "get_recipe_ingredient_names",
        lambda recipe_id: [{"name": "계란", "is_required": True}],
    )
    monkeypatch.setattr(
        node_module.steps_service,
        "generate",
        lambda recipe_name, category, cooking_method, ingredients: GenerateCookingStepsOutput(
            steps=["계란을 풀어 그릇에 담는다.", "팬에 기름을 두르고 익힌다."]
        ),
    )

    result = node_module.classify_and_substitute(
        AgentState(selected_ingredients=["계란"], recipe_id="r1")
    )

    assert result["owned_ingredients"] == ["계란"]
    assert result["missing_ingredients"] == []
    assert "missing_classification" not in result
    assert result["cooking_steps"] == ["계란을 풀어 그릇에 담는다.", "팬에 기름을 두르고 익힌다."]


def test_classifies_and_finds_substitutes_for_missing(monkeypatch):
    monkeypatch.setattr(
        node_module,
        "get_recipe_by_id",
        lambda recipe_id: {
            "id": "r1",
            "name": "계란밥",
            "cooking_time": 10,
            "difficulty": None,
            "category": "밥",
            "cooking_method": None,
        },
    )
    monkeypatch.setattr(
        node_module,
        "get_recipe_ingredient_names",
        lambda recipe_id: [
            {"name": "계란", "is_required": True},
            {"name": "대파", "is_required": False},
        ],
    )
    monkeypatch.setattr(
        node_module.classification_service,
        "classify",
        lambda recipe_id, available: ClassifyMissingOutput(
            required=[], optional=["대파"], reason="생략 가능"
        ),
    )
    substitute_find_calls = []

    def _fake_find(
        ingredient_name,
        recipe_name,
        recipe_context,
        exclude_ingredients=None,
        owned_ingredients=None,
    ):
        substitute_find_calls.append(owned_ingredients)
        return FindSubstitutesOutput(
            substitutes=[SubstituteCandidate(ingredient_name="대파", substitute_name="쪽파")],
            reason="비슷한 향",
        )

    monkeypatch.setattr(node_module.substitute_service, "find", _fake_find)
    monkeypatch.setattr(
        node_module.steps_service,
        "generate",
        lambda recipe_name, category, cooking_method, ingredients: GenerateCookingStepsOutput(
            steps=["재료를 손질한다.", "밥을 볶는다."]
        ),
    )

    result = node_module.classify_and_substitute(
        AgentState(selected_ingredients=["계란"], recipe_id="r1")
    )

    assert result["owned_ingredients"] == ["계란"]
    assert result["missing_ingredients"] == ["대파"]
    assert result["missing_classification"].optional == ["대파"]
    assert [s.substitute_name for s in result["substitutes"]] == ["쪽파"]
    assert result["cooking_steps"] == ["재료를 손질한다.", "밥을 볶는다."]
    # 대체재를 찾을 때 사용자가 이미 가진 재료(계란)를 넘겨줘야 그걸 우선 추천할 수 있다.
    assert substitute_find_calls == [["계란"]]
