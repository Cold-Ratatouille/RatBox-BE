"""react_agent(Phase A, 후보 검색)에 bind할 Tool 목록.

classify_missing_ingredients/find_substitutes는 Phase B(선택 후 상세)에서 에이전트의
자율 선택 없이 결정론적으로 직접 호출하므로 여기 포함하지 않는다.
"""

from app.agent.tools.recipe_tools import execute_sql, generate_sql

ALL_TOOLS = [generate_sql, execute_sql]
