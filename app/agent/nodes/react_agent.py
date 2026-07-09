"""도구 선택 ReAct 판단 노드. LangGraph StateGraph + bind_tools 연동은 별도 이슈에서 구현."""

from app.agent.state import AgentState


def react_agent(state: AgentState) -> AgentState:
    raise NotImplementedError("LangGraph Agent 핵심 구현 이슈에서 연동")
