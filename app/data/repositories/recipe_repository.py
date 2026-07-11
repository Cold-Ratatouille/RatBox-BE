from app.data.supabase_client import get_supabase


def get_recipe_by_id(recipe_id: str) -> dict | None:
    supabase = get_supabase()
    response = (
        supabase.table("recipes")
        .select("id, name, cooking_time, difficulty, category, cooking_method")
        .eq("id", recipe_id)
        .execute()
    )
    return response.data[0] if response.data else None


def get_recipe_ingredient_names(recipe_id: str) -> list[dict]:
    supabase = get_supabase()
    response = (
        supabase.table("recipe_ingredients")
        .select("is_required, ingredients_master(name)")
        .eq("recipe_id", recipe_id)
        .execute()
    )
    return [
        {"name": row["ingredients_master"]["name"], "is_required": row["is_required"]}
        for row in response.data
    ]
