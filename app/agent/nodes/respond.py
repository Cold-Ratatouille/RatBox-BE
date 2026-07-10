"""최종 자연어 응답 생성 노드. 응답 생성 프롬프트 연동은 별도 이슈에서 구현."""

from app.agent.state import AgentState


def respond(state: AgentState) -> AgentState:
    state.final_message = state.final_message or f"{len(state.recipes)}개의 레시피를 찾았습니다."
    return state
