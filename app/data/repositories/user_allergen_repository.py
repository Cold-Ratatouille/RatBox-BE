from app.data.supabase_client import get_supabase


def create_user_allergens(user_id: str, allergen_ids: list[str]) -> list[dict]:
    if not allergen_ids:
        return []
    supabase = get_supabase()
    rows = [{"user_id": user_id, "allergen_id": allergen_id} for allergen_id in allergen_ids]
    response = supabase.table("user_allergens").insert(rows).execute()
    return response.data
