from app.agent.nodes.ask_clarification import ask_clarification
from app.agent.nodes.best_effort_response import best_effort_response
from app.agent.nodes.broaden_search import broaden_search
from app.agent.nodes.search_recipes import search_recipes
from app.agent.nodes.verify_relevance import verify_relevance
from app.agent.services import relevance_service, search_service
from app.agent.state import AgentState
from app.domain.models import RecipeCandidate


def test_search_recipes_node_calls_service_with_state_params(monkeypatch):
    captured = {}

    def _fake_search(selected_ingredients, min_match, limit):
        captured["args"] = (selected_ingredients, min_match, limit)
        return [RecipeCandidate(id="1", name="계란밥")]

    monkeypatch.setattr(search_service, "search_recipes", _fake_search)

    state = AgentState(selected_ingredients=["계란"], min_match=2, search_limit=20)
    result = search_recipes(state)

    assert captured["args"] == (["계란"], 2, 20)
    assert [c.id for c in result["candidate_recipes"]] == ["1"]


def test_verify_relevance_node_reflects_service_result(monkeypatch):
    class _FakeResult:
        passed = True
        reason = "재료 활용도가 좋아요"

    monkeypatch.setattr(relevance_service, "verify", lambda ingredients, candidates: _FakeResult())

    state = AgentState(
        selected_ingredients=["계란"], candidate_recipes=[RecipeCandidate(id="1", name="계란밥")]
    )
    result = verify_relevance(state)

    assert result == {"relevance_passed": True, "relevance_reason": "재료 활용도가 좋아요"}


def test_broaden_search_lowers_min_match_and_raises_limit():
    state = AgentState(min_match=2, search_limit=20, retry_count=0)

    result = broaden_search(state)

    assert result == {"min_match": 1, "search_limit": 40, "retry_count": 1}


def test_broaden_search_floors_and_caps():
    state = AgentState(min_match=1, search_limit=40, retry_count=1)

    result = broaden_search(state)

    assert result == {"min_match": 1, "search_limit": 40, "retry_count": 2}


def test_best_effort_response_includes_reason_and_candidates():
    state = AgentState(
        candidate_recipes=[
            RecipeCandidate(id="1", name="계란밥", missing_ingredients=["대파"])
        ],
        relevance_reason="재료 활용도가 낮아 보여요",
    )

    result = best_effort_response(state)

    assert "계란밥" in result["final_message"]
    assert "재료 활용도가 낮아 보여요" in result["final_message"]
    assert result["low_confidence"] is True


def test_ask_clarification_returns_fixed_message():
    result = ask_clarification(AgentState())

    assert "재료를 몇 가지 더 알려주시면" in result["final_message"]
