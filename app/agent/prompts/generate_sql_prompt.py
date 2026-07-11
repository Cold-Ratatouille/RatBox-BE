DB_SCHEMA_CONTEXT = """다음 3개 테이블만 조회할 수 있다:

- recipes(id uuid, name text, cooking_time integer, difficulty text, servings integer,
  category text, cooking_method text)
- recipe_ingredients(recipe_id uuid, ingredient_id uuid, amount numeric, unit text,
  is_required boolean)
- ingredients_master(id uuid, name text, ingredient_category text, allergen_id uuid)

규칙:
- SELECT 문만 작성한다. INSERT/UPDATE/DELETE/DDL은 절대 쓰지 않는다.
- 위 3개 테이블 외에는 참조하지 않는다.
- 재료명은 항상 ingredients_master.name과 정확히 일치하는 문자열로 매칭한다.
- 문자열 리터럴은 안전하게 작성하고, 세미콜론으로 여러 문장을 이어 쓰지 않는다.
- 후보를 넉넉히(최대 20개) 가져와야 이후 단계에서 부족 재료 개수로 다시 정렬할 수 있으니
  LIMIT 20을 반드시 붙인다."""

GENERATE_SQL_PROMPT = (
    DB_SCHEMA_CONTEXT
    + """

아래 보유 재료와 하나라도 겹치는 레시피를 찾는 단일 SELECT문을 작성하라.
- 보유 재료: {ingredients}

예시 (보유 재료 ["계란", "밥"]):
SELECT DISTINCT r.id, r.name, r.cooking_time
FROM recipes r
JOIN recipe_ingredients ri ON ri.recipe_id = r.id
JOIN ingredients_master im ON im.id = ri.ingredient_id
WHERE im.name IN ('계란', '밥')
LIMIT 20;

SQL 문 하나만 출력하라."""
)
