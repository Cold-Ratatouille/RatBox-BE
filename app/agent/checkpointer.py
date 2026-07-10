"""세션(thread_id)별 상태 유지.

LangGraph Checkpointer 연동은 '멀티턴 & FastAPI 통합' 이슈에서 구현한다.
"""


def get_checkpointer():
    raise NotImplementedError("멀티턴 & FastAPI 통합 이슈에서 연동")
