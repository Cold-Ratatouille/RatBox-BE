from app.data.supabase_client import execute_with_retry, get_supabase


def find_recipe_ingredient_matches(ingredient_ids: list[str]) -> dict[str, list[str]]:
    """ingredient_ids 중 하나라도 쓰이는 레시피별로, 실제 겹치는 ingredient_id 목록을 묶어 반환한다.

    후보 recipe_id마다 재료 목록을 왕복 쿼리로 하나씩 가져오면(N+1) 후보가 많을 때
    지연이 누적되므로, 매칭 계산에 필요한 (recipe_id, ingredient_id) 쌍을 애초에
    ingredient_ids(사용자가 고른 소수의 재료) 기준 단 한 번의 쿼리로 가져온다. recipe_id
    기준으로 필터링하면 후보가 많을 때 쿼리 URL이 너무 길어질 수 있어 피한다."""
    if not ingredient_ids:
        return {}

    supabase = get_supabase()
    response = execute_with_retry(
        supabase.table("recipe_ingredients")
        .select("recipe_id, ingredient_id")
        .in_("ingredient_id", ingredient_ids)
    )
    matches: dict[str, list[str]] = {}
    for row in response.data:
        matches.setdefault(row["recipe_id"], []).append(row["ingredient_id"])
    return matches


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
