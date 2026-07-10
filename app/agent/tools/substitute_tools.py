from app.data.repositories.substitute_repository import find_substitutes


def find_ingredient_substitutes(ingredient_id: int) -> list[dict]:
    return find_substitutes(ingredient_id)
