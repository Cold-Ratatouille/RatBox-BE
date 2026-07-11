from app.data.supabase_client import get_supabase


def get_allergen_names_by_ids(allergen_ids: list[str]) -> list[str]:
    if not allergen_ids:
        return []

    supabase = get_supabase()
    response = (
        supabase.table("allergen_master").select("allergen_name").in_("id", allergen_ids).execute()
    )
    return [row["allergen_name"] for row in response.data]


def find_all_allergens() -> list[dict]:
    supabase = get_supabase()
    response = supabase.table("allergen_master").select("*").order("category").execute()
    return response.data


def find_allergens_by_ids(allergen_ids: list[str]) -> list[dict]:
    if not allergen_ids:
        return []
    supabase = get_supabase()
    response = supabase.table("allergen_master").select("*").in_("id", allergen_ids).execute()
    return response.data
