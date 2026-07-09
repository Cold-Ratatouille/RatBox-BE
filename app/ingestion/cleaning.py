import re
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd

from app.ingestion.constants import ALLERGEN_MAPPING, SYNONYM_TO_STANDARD, get_ingredient_category
from app.ingestion.ingredient_parser import parse_ingredient_text
from app.ingestion.schemas import REQUIRED_SOURCE_COLUMNS, SOURCE_CSV_ENCODING
from app.ingestion.validators import require_columns

_SERVINGS_PATTERN = re.compile(r"(\d+)")
_HOURS_PATTERN = re.compile(r"(\d+)\s*시간")
_MINUTES_PATTERN = re.compile(r"(\d+)\s*분")

# DB의 NOT NULL 컬럼인데 원본 CSV에는 값이 없는 행이 있어, 행을 버리지 않고 기본값으로 채운다.
DEFAULT_TEXT_FALLBACK = "미확인"
DEFAULT_NUMBER_FALLBACK = 0


def _fill_text(value) -> str:
    return value if isinstance(value, str) and value.strip() else DEFAULT_TEXT_FALLBACK


def _fill_number(value) -> int | float:
    return value if value is not None else DEFAULT_NUMBER_FALLBACK


def load_recipe_search_csv(filepath: Path) -> pd.DataFrame:
    df = pd.read_csv(filepath, encoding=SOURCE_CSV_ENCODING)
    require_columns(df, REQUIRED_SOURCE_COLUMNS, "레시피 CSV")
    return df


def parse_servings(text) -> int | None:
    if not isinstance(text, str):
        return None
    match = _SERVINGS_PATTERN.search(text)
    return int(match.group(1)) if match else None


def parse_cooking_time_minutes(text) -> int | None:
    if not isinstance(text, str):
        return None
    hours_match = _HOURS_PATTERN.search(text)
    minutes_match = _MINUTES_PATTERN.search(text)
    if not hours_match and not minutes_match:
        return None
    hours = int(hours_match.group(1)) if hours_match else 0
    minutes = int(minutes_match.group(1)) if minutes_match else 0
    return hours * 60 + minutes


def parse_registered_at(value) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip()
    if len(text) != 14 or not text.isdigit():
        return None
    return datetime.strptime(text, "%Y%m%d%H%M%S").isoformat()


def build_recipes(df: pd.DataFrame) -> pd.DataFrame:
    # cooking_time/servings는 pandas Series.apply()를 거치면 int+None 혼합이
    # float64(NaN)로 업캐스트되어 Postgres INTEGER 컬럼에 "15.0" 형태로 들어가 실패한다.
    # 리스트 컴프리헨션 + dtype="object"로 만들어 원본 int/None 타입을 그대로 유지한다.
    cooking_time = pd.Series(
        [_fill_number(parse_cooking_time_minutes(v)) for v in df["CKG_TIME_NM"]], dtype="object"
    )
    servings = pd.Series(
        [_fill_number(parse_servings(v)) for v in df["CKG_INBUN_NM"]], dtype="object"
    )

    return pd.DataFrame(
        {
            "id": [str(uuid.uuid4()) for _ in range(len(df))],
            "source_recipe_no": df["RCP_SNO"],
            "name": df["CKG_NM"].apply(_fill_text),
            "cooking_time": cooking_time,
            "difficulty": df["CKG_DODF_NM"].apply(_fill_text),
            "servings": servings,
            "category": df["CKG_KND_ACTO_NM"].apply(_fill_text),
            "cooking_method": df["CKG_MTH_ACTO_NM"].apply(_fill_text),
            "created_at": df["FIRST_REG_DT"].apply(parse_registered_at),
        }
    )


def build_ingredient_tables(
    df: pd.DataFrame, recipe_ids: pd.Series
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for recipe_id, raw_ingredients in zip(recipe_ids, df["CKG_MTRL_CN"]):
        for item in parse_ingredient_text(raw_ingredients):
            name = _fill_text(item["name"])
            standard_name = SYNONYM_TO_STANDARD.get(name, name)
            rows.append(
                {
                    "recipe_id": recipe_id,
                    "ingredient_name": standard_name,
                    "amount": _fill_number(item["amount"]),
                    "unit": _fill_text(item["unit"]),
                }
            )
    recipe_ingredients = pd.DataFrame(
        rows, columns=["recipe_id", "ingredient_name", "amount", "unit"]
    )

    unique_names = recipe_ingredients["ingredient_name"].unique()
    ingredients_master = pd.DataFrame(
        {
            "id": [str(uuid.uuid4()) for _ in range(len(unique_names))],
            "name": unique_names,
            "ingredient_category": [get_ingredient_category(name) for name in unique_names],
            "allergen_group": [ALLERGEN_MAPPING.get(name) for name in unique_names],
        }
    )

    ingredient_id_by_name = dict(zip(ingredients_master["name"], ingredients_master["id"]))
    recipe_ingredients = recipe_ingredients.assign(
        id=[str(uuid.uuid4()) for _ in range(len(recipe_ingredients))],
        ingredient_id=recipe_ingredients["ingredient_name"].map(ingredient_id_by_name),
        is_required=True,
    )[["id", "recipe_id", "ingredient_id", "amount", "unit", "is_required"]]

    return recipe_ingredients, ingredients_master
