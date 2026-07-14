from app.data.supabase_client import execute_with_retry, get_supabase


def find_recipe_ids_by_ingredient_names(ingredient_names: list[str]) -> list[str]:
    """ingredient_names 중 하나라도 쓰이는 레시피 id 목록(중복 제거, 순서 유지)을 반환한다."""
    if not ingredient_names:
        return []

    supabase = get_supabase()
    ingredient_response = execute_with_retry(
        supabase.table("ingredients_master").select("id").in_("name", ingredient_names)
    )
    ingredient_ids = [row["id"] for row in ingredient_response.data]
    if not ingredient_ids:
        return []

    recipe_ingredient_response = execute_with_retry(
        supabase.table("recipe_ingredients")
        .select("recipe_id")
        .in_("ingredient_id", ingredient_ids)
    )
    return list(dict.fromkeys(row["recipe_id"] for row in recipe_ingredient_response.data))


def get_recipes_by_ids(recipe_ids: list[str]) -> list[dict]:
    if not recipe_ids:
        return []

    supabase = get_supabase()
    response = execute_with_retry(
        supabase.table("recipes").select("id, name, cooking_time").in_("id", recipe_ids)
    )
    return response.data


def get_recipe_by_id(recipe_id: str) -> dict | None:
    supabase = get_supabase()
    response = execute_with_retry(
        supabase.table("recipes")
        .select("id, name, cooking_time, difficulty, category, cooking_method")
        .eq("id", recipe_id)
    )
    return response.data[0] if response.data else None


def get_recipe_ingredient_names(recipe_id: str) -> list[dict]:
    supabase = get_supabase()
    response = execute_with_retry(
        supabase.table("recipe_ingredients")
        .select("is_required, ingredients_master(name)")
        .eq("recipe_id", recipe_id)
    )
    return [
        {"name": row["ingredients_master"]["name"], "is_required": row["is_required"]}
        for row in response.data
    ]
