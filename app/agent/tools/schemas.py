from pydantic import BaseModel, Field

from app.domain.models import RecipeCandidate


class SearchRecipesInput(BaseModel):
    ingredients: list[str] = Field(..., description="사용자가 보유한 재료명 목록")
    excluded_ingredients: list[str] = Field(default_factory=list)


class SearchRecipesOutput(BaseModel):
    recipes: list[RecipeCandidate]


class ClassifyMissingInput(BaseModel):
    recipe_id: int
    available_ingredients: list[str]


class ClassifyMissingOutput(BaseModel):
    required: list[str]
    optional: list[str]
    reason: str
