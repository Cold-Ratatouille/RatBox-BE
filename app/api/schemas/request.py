from uuid import UUID

from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    message: str = Field(..., description="사용자 자연어 입력 (재료, 알레르기 등)")
    thread_id: str = Field(..., description="멀티턴 세션을 식별하는 대화 ID")


class SignupRequest(BaseModel):
    username: str = Field(..., min_length=4, max_length=20, description="로그인 아이디")
    password: str = Field(..., min_length=8, description="비밀번호")
    name: str = Field(..., min_length=1, description="사용자 이름")


class LoginRequest(BaseModel):
    username: str = Field(..., description="로그인 아이디")
    password: str = Field(..., description="비밀번호")


class RegisterAllergensRequest(BaseModel):
    allergen_ids: list[UUID] = Field(
        default_factory=list,
        description="사용자가 선택한 알레르기 id 목록 (0개, 1개, 여러 개 모두 가능)",
    )
