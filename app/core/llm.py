"""LLM 클라이언트 팩토리.

Claude/GPT function calling 연동은 'LangGraph Agent 핵심구현' 이슈에서 구현한다.
"""

from functools import lru_cache


@lru_cache
def get_llm():
    raise NotImplementedError("LangGraph Agent 핵심 구현 이슈에서 연동")
