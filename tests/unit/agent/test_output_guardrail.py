from app.agent.nodes.output_guardrail import output_guardrail
from app.agent.state import AgentState
from app.agent.tools.schemas import ClassifyMissingOutput


def test_output_guardrail_strips_allergens_from_missing_and_classification():
    state = AgentState(
        selected_ingredients=["밥"],
        allergies=["새우"],
        missing_ingredients=["새우", "대파"],
        missing_classification=ClassifyMissingOutput(
            required=["새우"], optional=["대파"], reason="테스트"
        ),
    )

    result = output_guardrail(state)

    assert result["missing_ingredients"] == ["대파"]
    assert result["missing_classification"].required == []
    assert result["missing_classification"].optional == ["대파"]


def test_output_guardrail_noop_when_guardrail_blocked():
    state = AgentState(selected_ingredients=["밥"], guardrail_blocked=True)

    assert output_guardrail(state) == {}
