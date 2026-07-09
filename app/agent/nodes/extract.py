"""자연어 → 재료/알레르기 구조화 추출. LLM 연동은 'LangGraph Agent 핵심구현' 이슈에서 구현."""

from app.agent.state import AgentState


def extract(state: AgentState) -> AgentState:
    state.ingredients = [token.strip() for token in state.message.split(",") if token.strip()]
    return state
