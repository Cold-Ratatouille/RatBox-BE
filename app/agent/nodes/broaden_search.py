"""Phase A: 검증 실패 시 검색 조건을 완화(min_match 낮추고 limit 늘림)하고 재시도 횟수를
늘리는 노드. 같은 파라미터로 search_recipes를 다시 돌리면 결과가 똑같으므로, 재시도마다
조건이 달라져야 한다."""

from langfuse import observe

from app.agent.state import AgentState

MIN_MATCH_FLOOR = 1
SEARCH_LIMIT_CAP = 40


@observe(name="broaden_search")
def broaden_search(state: AgentState) -> dict:
    return {
        "min_match": max(MIN_MATCH_FLOOR, state.min_match - 1),
        "search_limit": min(SEARCH_LIMIT_CAP, state.search_limit * 2),
        "retry_count": state.retry_count + 1,
    }
