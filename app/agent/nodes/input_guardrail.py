"""목록 선택 입력을 검증하는 진입 가드레일. 자유 텍스트가 없어 욕설/무관 입력 필터링은
불필요하고, 대신 재료가 아예 선택되지 않은 요청을 막는다."""

from langfuse import observe

from app.agent.state import AgentState


@observe(name="input_guardrail")
def input_guardrail(state: AgentState) -> dict:
    if not state.selected_ingredients:
        return {
            "guardrail_blocked": True,
            "guardrail_reason": "재료가 선택되지 않음",
            "final_message": "재료를 1개 이상 선택해주세요.",
        }
    return {"guardrail_blocked": False}
