"""LLM이 뽑아낸 조건을 안전하게 실행하는 계층.

자유 SQL 문자열을 그대로 실행하지 않고, 화이트리스트에 등록된 필터만 조합한다.
"""

from app.data.supabase_client import get_supabase

ALLOWED_FILTERS = {"ingredient_ids", "max_cooking_time"}


def execute_filtered_query(table: str, filters: dict) -> list[dict]:
    unknown = set(filters) - ALLOWED_FILTERS
    if unknown:
        raise ValueError(f"허용되지 않은 필터: {unknown}")

    supabase = get_supabase()
    query = supabase.table(table).select("*")
    if "ingredient_ids" in filters:
        query = query.in_("ingredient_id", filters["ingredient_ids"])
    if "max_cooking_time" in filters:
        query = query.lte("cooking_time", filters["max_cooking_time"])
    return query.execute().data
