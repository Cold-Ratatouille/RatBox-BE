import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse

from app.agent.voice_graph import run_voice_query
from app.api.schemas.request import VoiceQueryRequest

router = APIRouter(prefix="/cooking", tags=["voice-query"])

_CHUNK_SIZE = 4
_CHUNK_DELAY_SECONDS = 0.03


def _sse_event(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


async def _stream_answer(answer: str) -> AsyncIterator[str]:
    if not answer:
        yield _sse_event({"answer": ""})
    else:
        for end in range(_CHUNK_SIZE, len(answer) + _CHUNK_SIZE, _CHUNK_SIZE):
            yield _sse_event({"answer": answer[:end]})
            await asyncio.sleep(_CHUNK_DELAY_SECONDS)
    yield "event: done\ndata: {}\n\n"


@router.post("/voice-query")
async def voice_query(payload: VoiceQueryRequest) -> StreamingResponse:
    """조리 중 음성 질의 응답을 SSE로 실시간 전송한다.

    LangGraph invoke 자체는 동기 호출이라 스레드풀에서 돌려 이벤트 루프를 막지 않고,
    완성된 답변을 청크 단위로 흘려보내 프론트가 실시간으로 받는 것처럼 렌더링하게 한다.
    """
    state = await run_in_threadpool(
        run_voice_query,
        recipe_id=payload.recipe_id,
        allergen_ids=payload.allergen_ids,
        question=payload.question,
    )
    return StreamingResponse(
        _stream_answer(state.final_answer or ""),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
