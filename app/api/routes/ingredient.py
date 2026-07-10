from fastapi import APIRouter

from app.api.schemas.response import AllergenResponse, IngredientResponse
from app.services.ingredient_service import list_ingredients

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.get("", response_model=list[IngredientResponse])
async def get_ingredients() -> list[IngredientResponse]:
    return [
        IngredientResponse(
            id=i.id,
            name=i.name,
            description=i.description,
            allergen=(
                AllergenResponse(
                    id=i.allergen.id,
                    allergen_name=i.allergen.allergen_name,
                    category=i.allergen.category,
                )
                if i.allergen
                else None
            ),
        )
        for i in list_ingredients()
    ]
