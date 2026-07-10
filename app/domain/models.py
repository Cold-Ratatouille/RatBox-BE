from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    id: UUID
    username: str
    name: str


class Allergen(BaseModel):
    id: UUID
    allergen_name: str
    category: str


class RecipeCandidate(BaseModel):
    id: int
    name: str
    cooking_time: int | None = None


class SubstituteCandidate(BaseModel):
    ingredient_name: str
    substitute_name: str
    note: str | None = None
