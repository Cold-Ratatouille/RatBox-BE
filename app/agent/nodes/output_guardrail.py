"""알레르기 유발 재료가 최종 결과에 남아있으면 제외하는 출력 가드레일.

레시피별 전체 재료 목록 연동은 'LangGraph Agent 핵심구현' 이슈에서 구현한다.
"""

from app.agent.state import AgentState


def output_guardrail(state: AgentState) -> AgentState:
    return state
