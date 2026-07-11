"""Phase B: 사용자가 선택한 레시피 한 건에 대해서만 부족 재료 분류 + 대체재 판단을 수행한다.

에이전트가 도구를 자율 선택할 필요가 없는 결정론적 파이프라인이라 react_agent 루프를
쓰지 않고 Service를 직접 호출한다.
"""

from app.agent.services import classification_service, substitute_service
from app.agent.state import AgentState
from app.data.repositories.recipe_repository import get_recipe_by_id, get_recipe_ingredient_names
from app.domain.models import RecipeDetail


def classify_and_substitute(state: AgentState) -> dict:
    recipe = get_recipe_by_id(state.recipe_id)
    if recipe is None:
        return {
            "guardrail_blocked": True,
            "guardrail_reason": "레시피를 찾을 수 없음",
            "final_message": "선택한 레시피를 찾을 수 없어요.",
        }

    recipe_detail = RecipeDetail(**recipe)

    full_names = [row["name"] for row in get_recipe_ingredient_names(state.recipe_id)]
    missing = [name for name in full_names if name not in state.selected_ingredients]

    if not missing:
        return {"recipe_detail": recipe_detail, "missing_ingredients": []}

    classification = classification_service.classify(state.recipe_id, state.selected_ingredients)

    substitutes = []
    for name in missing:
        result = substitute_service.find(name, recipe_detail.name, recipe_detail.category)
        substitutes.extend(result.substitutes)

    return {
        "recipe_detail": recipe_detail,
        "missing_ingredients": missing,
        "missing_classification": classification,
        "substitutes": substitutes,
    }
