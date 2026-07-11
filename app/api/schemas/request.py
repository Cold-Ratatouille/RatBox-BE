from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    ingredient_ids: list[str] = Field(
        ..., description="사용자가 목록에서 선택한 재료 id 목록 (ingredients_master.id)"
    )
    allergen_ids: list[str] = Field(
        default_factory=list, description="사용자의 등록된 알레르기 id 목록 (allergen_master.id)"
    )
    recipe_id: str | None = Field(
        None, description="후보 3개 중 사용자가 선택한 레시피 id. 없으면 후보 추천 단계로 처리"
    )
