from fastapi import FastAPI

from app.db.supabase_client import get_supabase

app = FastAPI(title="RatBox API")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/recommend")
async def recommend(ingredients: list[str]):
    supabase = get_supabase()
    ingredient_ids = [
        ingredient_id
        for ingredient_id in (get_ingredient_id(supabase, name) for name in ingredients)
        if ingredient_id is not None
    ]

    response = (
        supabase.table("recipe_ingredients")
        .select("recipe_id, recipes(name, cooking_time), ingredient_id")
        .in_("ingredient_id", ingredient_ids)
        .execute()
    )
    return {"recipes": response.data}


def get_ingredient_id(supabase, ingredient_name: str):
    response = (
        supabase.table("ingredients_master").select("id").eq("name", ingredient_name).execute()
    )
    if response.data:
        return response.data[0]["id"]

    syn_response = (
        supabase.table("ingredient_synonyms")
        .select("ingredient_id")
        .eq("synonym_name", ingredient_name)
        .execute()
    )
    if syn_response.data:
        return syn_response.data[0]["ingredient_id"]

    return None
