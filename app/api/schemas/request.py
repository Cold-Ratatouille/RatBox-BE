from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    message: str = Field(..., description="사용자 자연어 입력 (재료, 알레르기 등)")
    thread_id: str = Field(..., description="멀티턴 세션을 식별하는 대화 ID")
