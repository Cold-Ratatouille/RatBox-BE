from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from app.agent import graph as graph_module
from app.agent.nodes import classify_and_substitute as classify_module
from app.agent.nodes import react_agent as react_agent_module
from app.agent.nodes import resolve_inputs as resolve_inputs_module
from app.agent.services import recipe_service, recipe_sql_service
from app.agent.tools.schemas import (
    ClassifyMissingOutput,
    FindSubstitutesOutput,
    GenerateSQLOutput,
)
from app.domain.models import SubstituteCandidate
from app.main import app

FIXED_SQL = "SELECT id, name, cooking_time FROM recipes LIMIT 20"
client = TestClient(app)


class _FakeStructured:
    def __init__(self, output):
        self._output = output

    def invoke(self, prompt):
        return self._output


class _FakeGenerateSQLLLM:
    def __init__(self, sql: str):
        self._output = GenerateSQLOutput(sql=sql)

    def with_structured_output(self, schema):
        return _FakeStructured(self._output)


class _ScriptedBoundLLM:
    def __init__(self, responses):
        self._responses = list(responses)

    def invoke(self, conversation):
        return self._responses.pop(0)


class _ScriptedReactLLM:
    def __init__(self, responses):
        self._bound = _ScriptedBoundLLM(responses)

    def bind_tools(self, tools):
        return self._bound


def _script_two_tool_calls(sql: str):
    return [
        AIMessage(
            content="",
            tool_calls=[{"name": "generate_sql", "args": {"ingredients": []}, "id": "c1"}],
        ),
        AIMessage(
            content="", tool_calls=[{"name": "execute_sql", "args": {"sql": sql}, "id": "c2"}]
        ),
        AIMessage(content="done", tool_calls=[]),
    ]


def _patch_search_phase(
    monkeypatch, *, sql=FIXED_SQL, allergies=None, ingredients_by_recipe=None
):
    # ingredient_id/allergen_id -> 이름 변환은 테스트에서 굳이 실제 id를 쓸 필요가 없어
    # id를 그대로 이름처럼 사용하는 identity mock으로 대체한다.
    monkeypatch.setattr(resolve_inputs_module, "get_ingredient_names_by_ids", lambda ids: ids)
    monkeypatch.setattr(
        resolve_inputs_module, "get_allergen_names_by_ids", lambda ids: allergies or []
    )
    scripted_llm = _ScriptedReactLLM(_script_two_tool_calls(sql))
    monkeypatch.setattr(react_agent_module, "get_llm", lambda: scripted_llm)
    monkeypatch.setattr(recipe_sql_service, "get_llm", lambda: _FakeGenerateSQLLLM(sql))
    if ingredients_by_recipe is not None:
        monkeypatch.setattr(
            recipe_service,
            "get_recipe_ingredient_names",
            lambda recipe_id: ingredients_by_recipe[recipe_id],
        )


def test_normal_flow_returns_top_recipes(monkeypatch):
    _patch_search_phase(
        monkeypatch,
        ingredients_by_recipe={
            "1": [{"name": "계란", "is_required": True}],
            "2": [{"name": "계란", "is_required": True}, {"name": "대파", "is_required": True}],
        },
    )
    monkeypatch.setattr(
        recipe_sql_service,
        "execute_readonly_sql",
        lambda sql: [
            {"id": "1", "name": "계란밥", "cooking_time": 10},
            {"id": "2", "name": "대파계란찜", "cooking_time": 20},
        ],
    )

    response = client.post("/recommend", json={"ingredient_ids": ["계란"]})

    assert response.status_code == 200
    body = response.json()
    assert [r["name"] for r in body["recipes"]] == ["계란밥", "대파계란찜"]
    assert body["recipes"][1]["missing_ingredients"] == ["대파"]


def test_zero_matching_recipes(monkeypatch):
    _patch_search_phase(monkeypatch, ingredients_by_recipe={})
    monkeypatch.setattr(recipe_sql_service, "execute_readonly_sql", lambda sql: [])

    state = graph_module.run_agent(
        ingredient_ids=["없는재료"], allergen_ids=[], recipe_id=None
    )

    assert state.candidate_recipes == []
    assert "레시피가 없어요" in state.final_message


def test_allergy_violation_attempt_excludes_candidate(monkeypatch):
    _patch_search_phase(
        monkeypatch,
        allergies=["새우"],
        ingredients_by_recipe={
            "1": [{"name": "새우", "is_required": True}, {"name": "밥", "is_required": True}],
            "2": [{"name": "계란", "is_required": True}, {"name": "밥", "is_required": True}],
        },
    )
    monkeypatch.setattr(
        recipe_sql_service,
        "execute_readonly_sql",
        lambda sql: [
            {"id": "1", "name": "새우볶음밥", "cooking_time": 10},
            {"id": "2", "name": "계란밥", "cooking_time": 10},
        ],
    )

    state = graph_module.run_agent(
        ingredient_ids=["밥"], allergen_ids=["새우-allergen-id"], recipe_id=None
    )

    assert [c.id for c in state.candidate_recipes] == ["2"]


def test_sql_injection_attempt_is_blocked_before_execution(monkeypatch):
    calls = []
    monkeypatch.setattr(recipe_sql_service, "execute_readonly_sql", lambda sql: calls.append(sql))
    _patch_search_phase(
        monkeypatch, sql="SELECT * FROM recipes WHERE id = '1'; DROP TABLE recipes;"
    )

    state = graph_module.run_agent(ingredient_ids=["계란"], allergen_ids=[], recipe_id=None)

    assert calls == []  # 실행 계층까지 도달하지 않음
    assert state.sql_failure_count >= 1
    assert state.candidate_recipes == []


def test_ddl_dml_attempt_is_blocked(monkeypatch):
    calls = []
    monkeypatch.setattr(recipe_sql_service, "execute_readonly_sql", lambda sql: calls.append(sql))
    _patch_search_phase(monkeypatch, sql="DELETE FROM recipes WHERE 1=1")

    state = graph_module.run_agent(ingredient_ids=["계란"], allergen_ids=[], recipe_id=None)

    assert calls == []
    assert state.sql_failure_count >= 1


def test_substitute_allergy_conflict_is_flagged_not_auto_suggested(monkeypatch):
    monkeypatch.setattr(
        resolve_inputs_module, "get_allergen_names_by_ids", lambda ids: ["새우"]
    )
    monkeypatch.setattr(resolve_inputs_module, "get_ingredient_names_by_ids", lambda ids: ids)
    monkeypatch.setattr(
        classify_module,
        "get_recipe_by_id",
        lambda recipe_id: {
            "id": "2",
            "name": "대파계란찜",
            "cooking_time": 15,
            "difficulty": "초급",
            "category": "반찬",
            "cooking_method": "찜",
        },
    )
    monkeypatch.setattr(
        classify_module,
        "get_recipe_ingredient_names",
        lambda recipe_id: [
            {"name": "계란", "is_required": True},
            {"name": "대파", "is_required": True},
        ],
    )
    monkeypatch.setattr(
        classify_module.classification_service,
        "classify",
        lambda recipe_id, available: ClassifyMissingOutput(
            required=[], optional=["대파"], reason="향만 담당해서 생략 가능"
        ),
    )
    monkeypatch.setattr(
        classify_module.substitute_service,
        "find",
        lambda ingredient_name, recipe_name, recipe_context: FindSubstitutesOutput(
            substitutes=[SubstituteCandidate(ingredient_name="대파", substitute_name="새우")],
            reason="테스트",
        ),
    )

    state = graph_module.run_agent(
        ingredient_ids=["계란"], allergen_ids=["새우-allergen-id"], recipe_id="2"
    )

    assert len(state.substitutes) == 1
    assert state.substitutes[0].allergy_conflict is True
    assert "괜찮으실까요" in state.final_message
