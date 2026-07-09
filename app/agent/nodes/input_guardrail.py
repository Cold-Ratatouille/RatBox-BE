from app.agent.services.guardrail_service import is_blocked_input
from app.agent.state import AgentState


def input_guardrail(state: AgentState) -> AgentState:
    if is_blocked_input(state.message):
        state.final_message = "요리 관련 질의만 도와드려요."
    return state
