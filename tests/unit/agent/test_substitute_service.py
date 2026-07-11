from app.agent.services import substitute_service
from app.agent.tools.schemas import FindSubstitutesOutput
from app.domain.models import SubstituteCandidate


class _FakeStructuredLLM:
    def __init__(self, output):
        self._output = output

    def invoke(self, prompt):
        return self._output


class _FakeLLM:
    def __init__(self, output):
        self._output = output

    def with_structured_output(self, schema):
        return _FakeStructuredLLM(self._output)


def test_find_returns_llm_structured_output(monkeypatch):
    expected = FindSubstitutesOutput(
        substitutes=[
            SubstituteCandidate(ingredient_name="간장", substitute_name="소금", note="비슷한 짠맛")
        ],
        reason="간장이 없으면 소금으로 짠맛을 대신할 수 있다",
    )
    monkeypatch.setattr(substitute_service, "get_llm", lambda: _FakeLLM(expected))

    result = substitute_service.find("간장", "김치볶음밥", "볶음 요리")

    assert result == expected
