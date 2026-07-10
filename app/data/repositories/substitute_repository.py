from app.data.supabase_client import get_supabase


def find_substitutes(ingredient_id: int) -> list[dict]:
    supabase = get_supabase()
    response = (
        supabase.table("ingredient_substitutes")
        .select("substitute_id, note")
        .eq("ingredient_id", ingredient_id)
        .execute()
    )
    return response.data
