from app.api.schemas.request import RecommendRequest


def test_recommend_request_requires_message_and_thread_id():
    request = RecommendRequest(message="계란 있어", thread_id="session-1")
    assert request.message == "계란 있어"
    assert request.thread_id == "session-1"
