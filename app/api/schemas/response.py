from pydantic import BaseModel


class RecipeSummary(BaseModel):
    id: str
    name: str
    cooking_time: int | None = None
    missing_ingredients: list[str] = []


class SubstituteSummary(BaseModel):
    ingredient_name: str
    substitute_name: str
    note: str | None = None
    allergy_conflict: bool = False


class ClassificationSummary(BaseModel):
    required: list[str] = []
    optional: list[str] = []
    reason: str | None = None


class RecipeDetailResponse(BaseModel):
    recipe_id: str
    name: str
    cooking_time: int | None = None
    difficulty: str | None = None
    category: str | None = None
    cooking_method: str | None = None
    missing_ingredients: list[str] = []
    classification: ClassificationSummary | None = None
    substitutes: list[SubstituteSummary] = []


class RecommendResponse(BaseModel):
    recipes: list[RecipeSummary] = []
    detail: RecipeDetailResponse | None = None
    message: str
