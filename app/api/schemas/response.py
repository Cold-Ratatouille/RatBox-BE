from uuid import UUID

from pydantic import BaseModel


class RecipeSummary(BaseModel):
    id: int
    name: str
    cooking_time: int | None = None


class RecommendResponse(BaseModel):
    recipes: list[RecipeSummary]
    message: str


class SignupResponse(BaseModel):
    id: UUID
    username: str
    name: str


class AllergenResponse(BaseModel):
    id: UUID
    allergen_name: str
    category: str
