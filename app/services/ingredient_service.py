from app.data.repositories.ingredient_repository import find_all_ingredients
from app.domain.models import Allergen, Ingredient


def list_ingredients() -> list[Ingredient]:
    rows = find_all_ingredients()
    return [
        Ingredient(
            id=row["id"],
            name=row["name"],
            description=row.get("description"),
            allergen=_to_allergen(row.get("allergen_master")),
        )
        for row in rows
    ]


def _to_allergen(row: dict | None) -> Allergen | None:
    if not row:
        return None
    return Allergen(id=row["id"], allergen_name=row["allergen_name"], category=row["category"])
