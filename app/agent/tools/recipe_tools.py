from app.agent.tools.schemas import SearchRecipesInput, SearchRecipesOutput
from app.data.mappers.recipe_mapper import map_recipe_row
from app.data.repositories.ingredient_repository import resolve_ingredient_id
from app.data.repositories.recipe_repository import find_recipes_by_ingredient_ids


def search_recipes(payload: SearchRecipesInput) -> SearchRecipesOutput:
    ids = [i for i in (resolve_ingredient_id(name) for name in payload.ingredients) if i]
    rows = find_recipes_by_ingredient_ids(ids)
    return SearchRecipesOutput(recipes=[map_recipe_row(row) for row in rows])
