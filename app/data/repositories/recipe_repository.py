from app.data.supabase_client import get_supabase


def find_recipes_by_ingredient_ids(ingredient_ids: list[int]) -> list[dict]:
    supabase = get_supabase()
    response = (
        supabase.table("recipe_ingredients")
        .select("recipe_id, recipes(name, cooking_time), ingredient_id")
        .in_("ingredient_id", ingredient_ids)
        .execute()
    )
    return response.data
