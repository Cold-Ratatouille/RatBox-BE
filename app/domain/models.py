from pydantic import BaseModel


class RecipeCandidate(BaseModel):
    id: str
    name: str
    cooking_time: int | None = None
    missing_ingredients: list[str] = []


class SubstituteCandidate(BaseModel):
    ingredient_name: str
    substitute_name: str
    note: str | None = None
    allergy_conflict: bool = False


class RecipeDetail(BaseModel):
    id: str
    name: str
    cooking_time: int | None = None
    difficulty: str | None = None
    category: str | None = None
    cooking_method: str | None = None
