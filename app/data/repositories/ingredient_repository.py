from app.data.supabase_client import get_supabase


def get_ingredient_names_by_ids(ingredient_ids: list[str]) -> list[str]:
    if not ingredient_ids:
        return []

    supabase = get_supabase()
    response = (
        supabase.table("ingredients_master").select("name").in_("id", ingredient_ids).execute()
    )
    return [row["name"] for row in response.data]


def find_all_categories() -> list[dict]:
    supabase = get_supabase()
    response = supabase.table("ingredients_category").select("id, name").order("name").execute()
    return response.data


def find_ingredients_by_category_id(category_id: str) -> list[dict]:
    supabase = get_supabase()
    response = (
        supabase.table("ingredients_master")
        .select("id, name, description, allergen_master(id, allergen_name, category)")
        .eq("category_id", category_id)
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
