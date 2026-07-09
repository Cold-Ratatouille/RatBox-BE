INGREDIENT_SYNONYMS = {
    "계란": ["달걀", "왕란", "계란(달걀)"],
    "밥": ["쌀밥", "흰쌀밥"],
    "돼지고기": ["삼겹살", "돈육", "돼지肉"],
    "소금": ["천일염", "소금(천일염)"],
    "참기름": ["깨기름"],
    "고추": ["건고추", "고추(말린)"],
    "파": ["대파", "쪽파"],
    "마늘": ["다진마늘"],
    "양파": ["양파(다진)", "다진양파"],
}

SYNONYM_TO_STANDARD = {}
for _standard, _synonyms in INGREDIENT_SYNONYMS.items():
    SYNONYM_TO_STANDARD[_standard] = _standard
    for _syn in _synonyms:
        SYNONYM_TO_STANDARD[_syn] = _standard

INGREDIENT_CATEGORIES = {
    "육류": ["계란", "돼지고기", "소고기", "닭고기", "생선"],
    "채소": ["대파", "양파", "마늘", "고추", "당근", "브로콜리"],
    "양념": ["소금", "설탕", "간장", "참기름", "고추장"],
    "곡류": ["밥", "밀가루", "쌀"],
    "유제품": ["우유", "치즈", "버터"],
}

ALLERGEN_MAPPING = {
    "계란": "계란",
    "우유": "우유",
    "견과류": "견과류",
    "새우": "갑각류",
    "게": "갑각류",
    "돼지고기": "돼지",
    "소고기": "소",
    "닭고기": "닭",
    "생선": "생선",
    "고등어": "생선",
    "연어": "생선",
    "옥수수": "옥수수",
    "소금": None,
    "설탕": None,
    "간장": "대두",
    "참기름": None,
}


def get_ingredient_category(ingredient_name: str) -> str:
    for category, items in INGREDIENT_CATEGORIES.items():
        if ingredient_name in items:
            return category
    return "기타"
