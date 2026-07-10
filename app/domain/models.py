from pydantic import BaseModel


class User(BaseModel):
    id: str
    username: str
    name: str


class RecipeCandidate(BaseModel):
    id: int
    name: str
    cooking_time: int | None = None


class SubstituteCandidate(BaseModel):
    ingredient_name: str
    substitute_name: str
    note: str | None = None
