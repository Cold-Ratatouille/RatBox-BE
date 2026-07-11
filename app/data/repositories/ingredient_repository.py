from app.data.supabase_client import get_supabase


def get_ingredient_names_by_ids(ingredient_ids: list[str]) -> list[str]:
    if not ingredient_ids:
        return []

    supabase = get_supabase()
    response = (
        supabase.table("ingredients_master").select("name").in_("id", ingredient_ids).execute()
    )
    return [row["name"] for row in response.data]
