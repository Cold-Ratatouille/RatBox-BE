"""Phase A: 결정론적 후보 레시피 검색.

LLM이 매번 SQL을 새로 생성하던 방식(generate_sql/execute_sql)을 대체한다. 재료 매칭 개수
기준으로 후보를 찾는 것은 항상 같은 입력에 같은 결과가 나와야 하는 검색 로직이라 LLM에
맡기지 않고, 결과가 실제로 적절한지 판단(verify_relevance)만 LLM이 맡는다.
"""

from app.data.repositories.recipe_repository import (
    find_recipe_ids_by_ingredient_ids,
    get_recipe_ingredient_ids,
    get_recipes_by_ids,
)
from app.domain.models import RecipeCandidate


def search_recipes(
    ingredient_ids: list[str], min_match: int, limit: int
) -> list[RecipeCandidate]:
    """ingredient_ids와 min_match개 이상 겹치는 레시피를, 매칭 개수 내림차순으로
    최대 limit개 반환한다. 카테고리 선택으로 넘어온 id를 그대로 매칭에 쓴다 - 재료명은
    자유 입력이라 표기가 갈릴 수 있지만 id는 정규화된 값이라 매칭이 더 정확하다."""
    recipe_ids = find_recipe_ids_by_ingredient_ids(ingredient_ids)
    if not recipe_ids:
        return []

    selected = set(ingredient_ids)
    scored: list[tuple[int, str]] = []
    for recipe_id in recipe_ids:
        ids = set(get_recipe_ingredient_ids(recipe_id))
        match_count = len(ids & selected)
        if match_count >= min_match:
            scored.append((match_count, recipe_id))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    top_ids = [recipe_id for _, recipe_id in scored[:limit]]

    recipes_by_id = {recipe["id"]: recipe for recipe in get_recipes_by_ids(top_ids)}
    return [
        RecipeCandidate(
            id=recipe_id,
            name=recipes_by_id[recipe_id]["name"],
            cooking_time=recipes_by_id[recipe_id].get("cooking_time"),
        )
        for recipe_id in top_ids
        if recipe_id in recipes_by_id
    ]
