from app.data.supabase_client import get_supabase


def find_all_ingredients() -> list[dict]:
    supabase = get_supabase()
    response = (
        supabase.table("ingredients_master")
        .select("id, name, description, allergen_master(id, allergen_name, category)")
        .order("name")
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
