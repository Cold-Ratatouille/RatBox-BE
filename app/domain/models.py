from pydantic import BaseModel


class RecipeCandidate(BaseModel):
    id: int
    name: str
    cooking_time: int | None = None


class SubstituteCandidate(BaseModel):
    ingredient_name: str
    substitute_name: str
    note: str | None = None
