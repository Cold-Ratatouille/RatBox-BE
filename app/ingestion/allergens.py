import uuid

import pandas as pd

# 식약처 21개 알레르기 표시 품목 + FDA 9대 알레르기 항원 세부 재료 기준 시드 데이터.
ALLERGEN_SEED = [
    {"allergen_name": "랍스터", "category": "갑각류"},
    {"allergen_name": "새우", "category": "갑각류"},
    {"allergen_name": "게", "category": "갑각류"},
    {"allergen_name": "가재", "category": "갑각류"},
    {"allergen_name": "크릴", "category": "갑각류"},
    {"allergen_name": "오징어", "category": "갑각류"},
    {"allergen_name": "조개류", "category": "갑각류"},
    {"allergen_name": "굴", "category": "갑각류"},
    {"allergen_name": "전복", "category": "갑각류"},
    {"allergen_name": "홍합", "category": "갑각류"},
    {"allergen_name": "해덕", "category": "어류"},
    {"allergen_name": "대구", "category": "어류"},
    {"allergen_name": "틸라피아", "category": "어류"},
    {"allergen_name": "참치", "category": "어류"},
    {"allergen_name": "연어", "category": "어류"},
    {"allergen_name": "퍼치", "category": "어류"},
    {"allergen_name": "플라운더", "category": "어류"},
    {"allergen_name": "고등어", "category": "어류"},
    {"allergen_name": "땅콩", "category": "땅콩"},
    {"allergen_name": "아몬드", "category": "트리넛"},
    {"allergen_name": "캐슈", "category": "트리넛"},
    {"allergen_name": "피칸", "category": "트리넛"},
    {"allergen_name": "호두", "category": "트리넛"},
    {"allergen_name": "마카다미아", "category": "트리넛"},
    {"allergen_name": "피스타치오", "category": "트리넛"},
    {"allergen_name": "잣", "category": "트리넛"},
    {"allergen_name": "소 우유", "category": "우유"},
    {"allergen_name": "산양유", "category": "우유"},
    {"allergen_name": "양유", "category": "우유"},
    {"allergen_name": "닭 달걀", "category": "달걀"},
    {"allergen_name": "오리알", "category": "달걀"},
    {"allergen_name": "칠면조알", "category": "달걀"},
    {"allergen_name": "메추라기알", "category": "달걀"},
    {"allergen_name": "일반 밀", "category": "밀"},
    {"allergen_name": "두럼밀", "category": "밀"},
    {"allergen_name": "스펠트", "category": "밀"},
    {"allergen_name": "카무트", "category": "밀"},
    {"allergen_name": "트리티칼레", "category": "밀"},
    {"allergen_name": "세몰리나", "category": "밀"},
    {"allergen_name": "아인콘", "category": "밀"},
    {"allergen_name": "에머", "category": "밀"},
    {"allergen_name": "참깨", "category": "참깨"},
    {"allergen_name": "대두", "category": "대두"},
    {"allergen_name": "두부", "category": "대두"},
    {"allergen_name": "간장", "category": "대두"},
    {"allergen_name": "낫토", "category": "대두"},
    {"allergen_name": "미소", "category": "대두"},
    {"allergen_name": "메밀", "category": "메밀"},
    {"allergen_name": "복숭아", "category": "과일류"},
    {"allergen_name": "토마토", "category": "채소류"},
    {"allergen_name": "닭고기", "category": "육류"},
    {"allergen_name": "돼지고기", "category": "육류"},
    {"allergen_name": "쇠고기", "category": "육류"},
    {"allergen_name": "살구씨", "category": "씨앗류"},
    {"allergen_name": "아황산류", "category": "식품첨가물"},
]

# 표준 재료명(SYNONYM_TO_STANDARD 결과)이 allergen_name 표기와 다른 경우의 별칭 매핑.
ALLERGEN_NAME_ALIASES = {
    "계란": "닭 달걀",
    "달걀": "닭 달걀",
    "소고기": "쇠고기",
    "밀가루": "일반 밀",
    "우유": "소 우유",
    "통깨": "참깨",
}


def build_allergen_master() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [str(uuid.uuid4()) for _ in ALLERGEN_SEED],
            "allergen_name": [entry["allergen_name"] for entry in ALLERGEN_SEED],
            "category": [entry["category"] for entry in ALLERGEN_SEED],
        }
    )


def resolve_allergen_id(ingredient_name: str, allergen_id_by_name: dict) -> str | None:
    allergen_name = ALLERGEN_NAME_ALIASES.get(ingredient_name, ingredient_name)
    return allergen_id_by_name.get(allergen_name)
