from pydantic import BaseModel

from app.domain.models import RecipeCandidate


class AgentState(BaseModel):
    message: str
    thread_id: str
    ingredients: list[str] = []
    excluded_ingredients: list[str] = []
    allergies: list[str] = []
    recipes: list[RecipeCandidate] = []
    final_message: str | None = None
