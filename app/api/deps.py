"""요청 검증/의존성 주입. Data Layer는 Business Logic Layer를 통해서만 접근한다."""

from fastapi import Header


def get_request_id(x_request_id: str | None = Header(default=None)) -> str | None:
    return x_request_id
