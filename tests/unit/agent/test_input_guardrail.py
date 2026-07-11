from app.agent.nodes.input_guardrail import input_guardrail
from app.agent.state import AgentState


def test_input_guardrail_blocks_empty_selection():
    state = AgentState(selected_ingredients=[])

    result = input_guardrail(state)

    assert result["guardrail_blocked"] is True
    assert result["final_message"] == "재료를 1개 이상 선택해주세요."


def test_input_guardrail_allows_non_empty_selection():
    state = AgentState(selected_ingredients=["계란", "밥"])

    result = input_guardrail(state)

    assert result == {"guardrail_blocked": False}
