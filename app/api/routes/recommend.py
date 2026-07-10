from fastapi import APIRouter

from app.agent.graph import run_agent
from app.api.schemas.request import RecommendRequest
from app.api.schemas.response import RecipeSummary, RecommendResponse

router = APIRouter()


@router.post("/recommend", response_model=RecommendResponse)
async def recommend(payload: RecommendRequest) -> RecommendResponse:
    state = await run_agent(payload.message, payload.thread_id)
    recipes = [
        RecipeSummary(id=r.id, name=r.name, cooking_time=r.cooking_time) for r in state.recipes
    ]
    return RecommendResponse(recipes=recipes, message=state.final_message or "")
