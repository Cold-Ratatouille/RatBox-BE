"""추천 결과가 사용자 제약(알레르기 등)을 위반하지 않는지 재검증하는 노드.

레시피별 전체 재료 목록 조회 연동은 'LangGraph Agent 핵심구현' 이슈에서 함께 구현한다.
"""

from app.agent.state import AgentState


def validate(state: AgentState) -> AgentState:
    return state
