from app.data.supabase_client import get_supabase


def find_user_by_username(username: str) -> dict | None:
    supabase = get_supabase()
    response = supabase.table("users").select("*").eq("username", username).execute()
    return response.data[0] if response.data else None


def find_user_by_id(user_id: str) -> dict | None:
    supabase = get_supabase()
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    return response.data[0] if response.data else None


def create_user(username: str, password_hash: str, name: str) -> dict:
    supabase = get_supabase()
    response = (
        supabase.table("users")
        .insert({"username": username, "password": password_hash, "name": name})
        .execute()
    )
    return response.data[0]
