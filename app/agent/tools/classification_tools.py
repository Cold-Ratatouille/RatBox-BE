"""필수/생략 재료 분류 Tool. LLM 구조화 출력 연동은 'LangGraph Agent 핵심구현' 이슈에서 구현."""

from app.agent.tools.schemas import ClassifyMissingInput, ClassifyMissingOutput


def classify_missing_ingredients(payload: ClassifyMissingInput) -> ClassifyMissingOutput:
    raise NotImplementedError("LangGraph Agent 핵심 구현 이슈에서 연동")
