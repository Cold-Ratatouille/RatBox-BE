"""DB에 의존하지 않는 순수 판정 로직."""


def filter_allergens(recipes: list[dict], allergies: list[str]) -> list[dict]:
    if not allergies:
        return recipes
    return [r for r in recipes if not set(r.get("ingredients", [])) & set(allergies)]


def check_substitute_conflict(substitute_name: str, allergies: list[str]) -> bool:
    return substitute_name in set(allergies)
