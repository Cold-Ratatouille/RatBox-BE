"""stateless LangGraph StateGraph 조립.

Checkpointer가 없으므로 요청마다 새 AgentState로 그래프를 1회 invoke한다.
recipe_id가 없으면 Phase A(후보 3개 추천), 있으면 Phase B(선택된 레시피 상세)로 분기한다.
"""

from functools import lru_cache

from langfuse import observe
from langgraph.graph import END, START, StateGraph

from app.agent.nodes.classify_and_substitute import classify_and_substitute
from app.agent.nodes.input_guardrail import input_guardrail
from app.agent.nodes.output_guardrail import output_guardrail
from app.agent.nodes.rank_candidates import rank_candidates
from app.agent.nodes.react_agent import react_agent
from app.agent.nodes.resolve_inputs import resolve_inputs
from app.agent.nodes.respond import respond
from app.agent.nodes.tool_node import tool_node
from app.agent.nodes.validate import validate
from app.agent.state import AgentState

MAX_REACT_TURNS = 6
MAX_SQL_FAILURES = 2


def _route_after_input_guardrail(state: AgentState) -> str:
    if state.guardrail_blocked:
        return "respond"
    return "react_agent" if state.recipe_id is None else "classify_and_substitute"


def _route_after_react_agent(state: AgentState) -> str:
    tool_calls = getattr(state.messages[-1], "tool_calls", None)
    under_turn_limit = state.react_turns < MAX_REACT_TURNS
    under_failure_limit = state.sql_failure_count < MAX_SQL_FAILURES
    if tool_calls and under_turn_limit and under_failure_limit:
        return "tool_node"
    return "rank_candidates"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("resolve_inputs", resolve_inputs)
    graph.add_node("input_guardrail", input_guardrail)
    graph.add_node("react_agent", react_agent)
    graph.add_node("tool_node", tool_node)
    graph.add_node("rank_candidates", rank_candidates)
    graph.add_node("classify_and_substitute", classify_and_substitute)
    graph.add_node("validate", validate)
    graph.add_node("output_guardrail", output_guardrail)
    graph.add_node("respond", respond)

    graph.add_edge(START, "resolve_inputs")
    graph.add_edge("resolve_inputs", "input_guardrail")
    graph.add_conditional_edges(
        "input_guardrail",
        _route_after_input_guardrail,
        {
            "respond": "respond",
            "react_agent": "react_agent",
            "classify_and_substitute": "classify_and_substitute",
        },
    )
    graph.add_conditional_edges(
        "react_agent",
        _route_after_react_agent,
        {"tool_node": "tool_node", "rank_candidates": "rank_candidates"},
    )
    graph.add_edge("tool_node", "react_agent")
    graph.add_edge("rank_candidates", "respond")
    graph.add_edge("classify_and_substitute", "validate")
    graph.add_edge("validate", "output_guardrail")
    graph.add_edge("output_guardrail", "respond")
    graph.add_edge("respond", END)

    return graph.compile()


@lru_cache
def get_graph():
    return build_graph()


@observe(name="recommend_graph")
def run_agent(
    ingredient_ids: list[str], allergen_ids: list[str], recipe_id: str | None
) -> AgentState:
    initial_state = AgentState(
        ingredient_ids=ingredient_ids, allergen_ids=allergen_ids, recipe_id=recipe_id
    )
    result = get_graph().invoke(initial_state, config={"recursion_limit": 25})
    return AgentState(**result)
