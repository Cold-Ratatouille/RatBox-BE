from fastapi import APIRouter

from app.agent.graph import run_agent
from app.api.schemas.request import RecommendRequest
from app.api.schemas.response import (
    ClassificationSummary,
    IngredientRef,
    RecipeDetailResponse,
    RecipeSummary,
    RecommendResponse,
    SubstituteSummary,
)
from app.data.repositories.ingredient_repository import get_ingredient_categories_by_names

router = APIRouter(tags=["recommend"])


def _to_ingredient_refs(names: list[str], categories: dict[str, str | None]) -> list[IngredientRef]:
    return [IngredientRef(name=name, category=categories.get(name)) for name in names]


@router.post("/recommend", response_model=RecommendResponse)
def recommend(payload: RecommendRequest) -> RecommendResponse:
    """동기 함수로 둬서 FastAPI가 워커 스레드에서 실행하게 한다 (LangGraph invoke가 동기 호출)."""
    state = run_agent(
        ingredient_ids=payload.ingredient_ids,
        allergen_ids=payload.allergen_ids,
        recipe_id=payload.recipe_id,
    )

    # FE가 부족/보유 재료를 카테고리별로 묶어 보여줄 수 있도록, 응답 경계에서만 카테고리를
    # 덧붙인다 - 그래프 내부 로직(매칭/분류/프롬프트)은 그대로 재료 이름 기반으로 둔다.
    all_names = {
        name for recipe in state.candidate_recipes for name in recipe.missing_ingredients
    } | set(state.owned_ingredients) | set(state.missing_ingredients)
    categories = get_ingredient_categories_by_names(list(all_names))

    recipes = [
        RecipeSummary(
            id=recipe.id,
            name=recipe.name,
            cooking_time=recipe.cooking_time,
            missing_ingredients=_to_ingredient_refs(recipe.missing_ingredients, categories),
        )
        for recipe in state.candidate_recipes
    ]

    detail = None
    if state.recipe_detail is not None:
        detail = RecipeDetailResponse(
            recipe_id=state.recipe_detail.id,
            name=state.recipe_detail.name,
            cooking_time=state.recipe_detail.cooking_time,
            difficulty=state.recipe_detail.difficulty,
            category=state.recipe_detail.category,
            cooking_method=state.recipe_detail.cooking_method,
            owned_ingredients=_to_ingredient_refs(state.owned_ingredients, categories),
            missing_ingredients=_to_ingredient_refs(state.missing_ingredients, categories),
            classification=(
                ClassificationSummary(**state.missing_classification.model_dump())
                if state.missing_classification
                else None
            ),
            substitutes=[SubstituteSummary(**s.model_dump()) for s in state.substitutes],
            cooking_steps=state.cooking_steps,
        )

    return RecommendResponse(recipes=recipes, detail=detail, message=state.final_message or "")
