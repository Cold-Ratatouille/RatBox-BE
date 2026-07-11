from fastapi import APIRouter

from app.agent.graph import run_agent
from app.api.schemas.request import RecommendRequest
from app.api.schemas.response import (
    ClassificationSummary,
    RecipeDetailResponse,
    RecipeSummary,
    RecommendResponse,
    SubstituteSummary,
)

router = APIRouter()


@router.post("/recommend", response_model=RecommendResponse)
def recommend(payload: RecommendRequest) -> RecommendResponse:
    """동기 함수로 둬서 FastAPI가 워커 스레드에서 실행하게 한다 (LangGraph invoke가 동기 호출)."""
    state = run_agent(
        ingredient_ids=payload.ingredient_ids,
        allergen_ids=payload.allergen_ids,
        recipe_id=payload.recipe_id,
    )

    recipes = [
        RecipeSummary(
            id=recipe.id,
            name=recipe.name,
            cooking_time=recipe.cooking_time,
            missing_ingredients=recipe.missing_ingredients,
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
            missing_ingredients=state.missing_ingredients,
            classification=(
                ClassificationSummary(**state.missing_classification.model_dump())
                if state.missing_classification
                else None
            ),
            substitutes=[SubstituteSummary(**s.model_dump()) for s in state.substitutes],
        )

    return RecommendResponse(recipes=recipes, detail=detail, message=state.final_message or "")
