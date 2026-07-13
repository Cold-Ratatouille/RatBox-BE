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


def find_all_ingredients() -> list[dict]:
    """Supabase(PostgREST)는 한 번의 조회당 최대 PAGE_SIZE개로 응답을 제한하므로,
    전체 재료(4천개 이상)를 다 받으려면 range로 페이지를 나눠 반복 조회해야 한다."""
    supabase = get_supabase()
    rows: list[dict] = []
    offset = 0
    while True:
        response = (
            supabase.table("ingredients_master")
            .select("id, name, description, allergen_master(id, allergen_name, category)")
            .order("name")
            .range(offset, offset + PAGE_SIZE - 1)
            .execute()
        )
        rows.extend(response.data)
        if len(response.data) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
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
