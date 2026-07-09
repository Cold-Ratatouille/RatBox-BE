"""pgvector 기반 유사 레시피 검색 Tool. pgvector 연동은 별도 이슈에서 구현."""


def search_similar_recipes(recipe_id: int, top_k: int = 3) -> list[dict]:
    raise NotImplementedError("pgvector 연동 이슈에서 구현")
