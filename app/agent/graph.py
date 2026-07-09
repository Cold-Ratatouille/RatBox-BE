"""LangGraph 기반 ReAct 루프는 'LangGraph Agent 핵심구현' 이슈에서 구현한다.

지금은 API가 동작하도록 검색 Tool만 직접 호출하는 최소 버전을 둔다.
"""

from app.agent.state import AgentState
from app.agent.tools.recipe_tools import search_recipes
from app.agent.tools.schemas import SearchRecipesInput


async def run_agent(message: str, thread_id: str) -> AgentState:
    state = AgentState(message=message, thread_id=thread_id, ingredients=_naive_extract(message))
    result = search_recipes(SearchRecipesInput(ingredients=state.ingredients))
    state.recipes = result.recipes
    state.final_message = f"{len(result.recipes)}개의 레시피를 찾았습니다."
    return state


def _naive_extract(message: str) -> list[str]:
    return [token.strip() for token in message.replace("있고", ",").split(",") if token.strip()]
