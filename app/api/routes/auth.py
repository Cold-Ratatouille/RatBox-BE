from fastapi import APIRouter, HTTPException, status

from app.api.schemas.request import SignupRequest
from app.api.schemas.response import SignupResponse
from app.services.auth_service import UsernameTakenError, signup

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup_route(payload: SignupRequest) -> SignupResponse:
    try:
        user = signup(username=payload.username, password=payload.password, name=payload.name)
    except UsernameTakenError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return SignupResponse(id=user.id, username=user.username, name=user.name)
