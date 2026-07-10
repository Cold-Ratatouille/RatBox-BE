"""DB에 의존하지 않는 순수 판정 로직."""

BLOCKED_KEYWORDS = {"바보", "씨발"}


def is_blocked_input(text: str) -> bool:
    return any(keyword in text for keyword in BLOCKED_KEYWORDS)


def filter_allergens(recipes: list[dict], allergies: list[str]) -> list[dict]:
    if not allergies:
        return recipes
    return [r for r in recipes if not set(r.get("ingredients", [])) & set(allergies)]
