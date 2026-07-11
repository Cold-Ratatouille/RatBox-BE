from app.data.supabase_client import get_supabase


def get_allergen_names_by_ids(allergen_ids: list[str]) -> list[str]:
    if not allergen_ids:
        return []

    supabase = get_supabase()
    response = (
        supabase.table("allergen_master").select("allergen_name").in_("id", allergen_ids).execute()
    )
    return [row["allergen_name"] for row in response.data]
