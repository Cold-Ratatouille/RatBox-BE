from app.domain.models import RecipeCandidate


def map_recipe_row(row: dict) -> RecipeCandidate:
    recipe = row.get("recipes") or {}
    return RecipeCandidate(
        id=row["recipe_id"],
        name=recipe.get("name", ""),
        cooking_time=recipe.get("cooking_time"),
    )
