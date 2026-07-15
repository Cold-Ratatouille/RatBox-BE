"""후보 레시피를 알레르기 기준으로 걸러내고, 부족 재료 개수 오름차순으로 상위 3개를 고른다.

LLM이 아니라 결정론적인 Python 로직으로 처리한다 — 정렬/필터링은 매번 같은 결과가
나와야 하는 안전 관련 로직이라 LLM 판단에 맡기지 않는다.
"""

from app.data.repositories.recipe_repository import get_recipe_ingredient_names
from app.domain.models import RecipeCandidate

TOP_N = 3


def rank_candidates(
    candidates: list[RecipeCandidate], selected_ingredients: list[str], allergies: list[str]
) -> list[RecipeCandidate]:
    selected = set(selected_ingredients)
    allergy_set = set(allergies)

    ranked: list[tuple[int, RecipeCandidate]] = []
    for candidate in candidates:
        ingredient_names = {
            row["name"] for row in get_recipe_ingredient_names(candidate.id)
        }
        if ingredient_names & allergy_set:
            continue

        missing = sorted(ingredient_names - selected)
        matched = sorted(ingredient_names & selected)
        ranked.append(
            (
                len(missing),
                candidate.model_copy(
                    update={"missing_ingredients": missing, "matched_ingredients": matched}
                ),
            )
        )

    ranked.sort(key=lambda pair: pair[0])
    return [candidate for _, candidate in ranked[:TOP_N]]
