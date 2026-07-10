from app.data.supabase_client import get_supabase


def find_all_allergens() -> list[dict]:
    supabase = get_supabase()
    response = supabase.table("allergen_master").select("*").order("category").execute()
    return response.data
