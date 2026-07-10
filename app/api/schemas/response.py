from pydantic import BaseModel


class RecipeSummary(BaseModel):
    id: int
    name: str
    cooking_time: int | None = None


class RecommendResponse(BaseModel):
    recipes: list[RecipeSummary]
    message: str


class SignupResponse(BaseModel):
    id: str
    username: str
    name: str
