from fastapi import APIRouter

from app.agent.voice_graph import run_voice_query
from app.api.schemas.request import VoiceQueryRequest
from app.api.schemas.response import VoiceQueryResponse

router = APIRouter(prefix="/cooking", tags=["voice-query"])


@router.post("/voice-query", response_model=VoiceQueryResponse)
def voice_query(payload: VoiceQueryRequest) -> VoiceQueryResponse:
    """동기 함수로 둬서 FastAPI가 워커 스레드에서 실행하게 한다 (LangGraph invoke가 동기 호출)."""
    state = run_voice_query(
        recipe_id=payload.recipe_id,
        allergen_ids=payload.allergen_ids,
        question=payload.question,
    )
    return VoiceQueryResponse(answer=state.final_answer or "")
