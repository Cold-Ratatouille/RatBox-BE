from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    message: str = Field(..., description="사용자 자연어 입력 (재료, 알레르기 등)")
    thread_id: str = Field(..., description="멀티턴 세션을 식별하는 대화 ID")


class SignupRequest(BaseModel):
    username: str = Field(..., min_length=4, max_length=20, description="로그인 아이디")
    password: str = Field(..., min_length=8, description="비밀번호")
    name: str = Field(..., min_length=1, description="사용자 이름")
