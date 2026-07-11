from app.agent.services import classification_service
from app.agent.tools.schemas import ClassifyMissingOutput


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


def test_classify_uses_recipe_ingredients_and_llm(monkeypatch):
    expected = ClassifyMissingOutput(
        required=["소고기"], optional=["대파"], reason="핵심 단백질 없음"
    )
    monkeypatch.setattr(
        classification_service,
        "get_recipe_ingredient_names",
        lambda recipe_id: [
            {"name": "소고기", "is_required": True},
            {"name": "대파", "is_required": False},
            {"name": "밥", "is_required": True},
        ],
    )
    monkeypatch.setattr(classification_service, "get_llm", lambda: _FakeLLM(expected))

    result = classification_service.classify("recipe-1", available_ingredients=["밥"])

    assert result == expected
