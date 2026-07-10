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


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: SignupResponse


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AllergenResponse(BaseModel):
    id: UUID
    allergen_name: str
    category: str


class UserAllergensResponse(BaseModel):
    allergens: list[AllergenResponse]


class IngredientResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    allergen: AllergenResponse | None = None


class MyInfoResponse(BaseModel):
    id: UUID
    username: str
    name: str
    allergens: list[AllergenResponse]
