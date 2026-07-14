import json
from concurrent.futures import ThreadPoolExecutor

from app.data.redis_client import get_redis
from app.data.supabase_client import get_supabase


def get_ingredient_names_by_ids(ingredient_ids: list[str]) -> list[str]:
    if not ingredient_ids:
        return []

    supabase = get_supabase()
    response = (
        supabase.table("ingredients_master").select("name").in_("id", ingredient_ids).execute()
    )
    return [row["name"] for row in response.data]


PAGE_SIZE = 1000
MAX_PAGE_WORKERS = 8

_ALL_INGREDIENTS_CACHE_KEY = "ingredients:all"
_ALL_INGREDIENTS_CACHE_TTL_SECONDS = 1800


def _select_ingredients_page(offset: int, count: str | None = None):
    supabase = get_supabase()
    query = supabase.table("ingredients_master").select(
        "id, name, description, allergen_master(id, allergen_name, category)",
        count=count,
    )
    return query.order("name").range(offset, offset + PAGE_SIZE - 1).execute()


def find_all_ingredients() -> list[dict]:
    """Supabase(PostgREST)는 한 번의 조회당 최대 PAGE_SIZE개로 응답을 제한하므로,
    전체 재료(4천개 이상)를 여러 페이지로 나눠 조회한다. 첫 페이지 응답에 담겨오는
    전체 개수(count)로 남은 페이지 수를 계산해, 순차 대신 스레드풀로 동시에 요청한다.
    재료 마스터는 자주 바뀌지 않는 데이터라 결과를 Redis에 캐싱해 재조회를 건너뛴다."""
    redis_client = get_redis()
    cached = redis_client.get(_ALL_INGREDIENTS_CACHE_KEY)
    if cached is not None:
        return json.loads(cached)

    first = _select_ingredients_page(0, count="exact")
    rows: list[dict] = list(first.data)

    remaining_offsets = range(PAGE_SIZE, first.count or 0, PAGE_SIZE)
    if remaining_offsets:
        workers = min(len(remaining_offsets), MAX_PAGE_WORKERS)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for page in executor.map(_select_ingredients_page, remaining_offsets):
                rows.extend(page.data)

    redis_client.set(
        _ALL_INGREDIENTS_CACHE_KEY, json.dumps(rows), ex=_ALL_INGREDIENTS_CACHE_TTL_SECONDS
    )
    return rows


def find_ingredients_by_ids(ingredient_ids: list[str]) -> list[dict]:
    if not ingredient_ids:
        return []
    supabase = get_supabase()
    response = (
        supabase.table("ingredients_master")
        .select("id, name, description, allergen_master(id, allergen_name, category)")
        .in_("id", ingredient_ids)
        .execute()
    )
    return response.data


def resolve_ingredient_id(name: str) -> int | None:
    supabase = get_supabase()

    response = supabase.table("ingredients_master").select("id").eq("name", name).execute()
    if response.data:
        return response.data[0]["id"]

    syn_response = (
        supabase.table("ingredient_synonyms")
        .select("ingredient_id")
        .eq("synonym_name", name)
        .execute()
    )
    if syn_response.data:
        return syn_response.data[0]["ingredient_id"]

    return None
