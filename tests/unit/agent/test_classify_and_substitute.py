from app.agent.nodes import classify_and_substitute as node_module
from app.agent.state import AgentState
from app.agent.tools.schemas import ClassifyMissingOutput, FindSubstitutesOutput
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

    result = node_module.classify_and_substitute(
        AgentState(selected_ingredients=["계란"], recipe_id="r1")
    )

    assert result["missing_ingredients"] == []
    assert "missing_classification" not in result


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
    monkeypatch.setattr(
        node_module.substitute_service,
        "find",
        lambda ingredient_name, recipe_name, recipe_context: FindSubstitutesOutput(
            substitutes=[
                SubstituteCandidate(ingredient_name="대파", substitute_name="쪽파")
            ],
            reason="비슷한 향",
        ),
    )

    result = node_module.classify_and_substitute(
        AgentState(selected_ingredients=["계란"], recipe_id="r1")
    )

    assert result["missing_ingredients"] == ["대파"]
    assert result["missing_classification"].optional == ["대파"]
    assert [s.substitute_name for s in result["substitutes"]] == ["쪽파"]
