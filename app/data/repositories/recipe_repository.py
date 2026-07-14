from app.data.supabase_client import execute_with_retry, get_supabase


def find_recipe_ids_by_ingredient_ids(ingredient_ids: list[str]) -> list[str]:
    """ingredient_ids 중 하나라도 쓰이는 레시피 id 목록(중복 제거, 순서 유지)을 반환한다.

    카테고리 선택이 넘겨주는 id를 그대로 쓴다 - ingredients_master를 이름으로 되짚어
    id를 다시 조회하던 왕복 쿼리를 없앤다."""
    if not ingredient_ids:
        return []

    supabase = get_supabase()
    recipe_ingredient_response = execute_with_retry(
        supabase.table("recipe_ingredients")
        .select("recipe_id")
        .in_("ingredient_id", ingredient_ids)
    )
    return list(dict.fromkeys(row["recipe_id"] for row in recipe_ingredient_response.data))


def get_recipe_ingredient_ids(recipe_id: str) -> list[str]:
    """후보 검색 단계의 매칭 개수 계산 전용 - ingredients_master 조인 없이 id만 가져온다."""
    supabase = get_supabase()
    response = execute_with_retry(
        supabase.table("recipe_ingredients").select("ingredient_id").eq("recipe_id", recipe_id)
    )
    return [row["ingredient_id"] for row in response.data]


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
