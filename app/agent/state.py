from typing import Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from app.agent.tools.schemas import ClassifyMissingOutput
from app.domain.models import RecipeCandidate, RecipeDetail, SubstituteCandidate


class AgentState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages] = []
    ingredient_ids: list[str] = []
    allergen_ids: list[str] = []
    recipe_id: str | None = None  # None=후보 추천 단계, 값 있으면 선택 후 상세 단계

    selected_ingredients: list[str] = []  # resolve_inputs가 ingredient_ids로부터 채움
    allergies: list[str] = []  # resolve_inputs가 allergen_ids로부터 채움

    candidate_recipes: list[RecipeCandidate] = []
    owned_ingredients: list[str] = []
    missing_ingredients: list[str] = []
    missing_classification: ClassifyMissingOutput | None = None
    substitutes: list[SubstituteCandidate] = []
    recipe_detail: RecipeDetail | None = None
    cooking_steps: list[str] = []

    react_turns: int = 0
    sql_failure_count: int = 0

    guardrail_blocked: bool = False
    guardrail_reason: str | None = None
    final_message: str | None = None
