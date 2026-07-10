from fastapi.testclient import TestClient

from app.agent.tools import recipe_tools
from app.main import app

client = TestClient(app)


def test_recommend_returns_matching_recipes(monkeypatch):
    monkeypatch.setattr(recipe_tools, "resolve_ingredient_id", lambda name: 1)
    monkeypatch.setattr(
        recipe_tools,
        "find_recipes_by_ingredient_ids",
        lambda ids: [
            {"recipe_id": 1, "recipes": {"name": "계란밥", "cooking_time": 10}, "ingredient_id": 1}
        ],
    )

    response = client.post("/recommend", json={"message": "계란, 밥", "thread_id": "t1"})

    assert response.status_code == 200
    assert response.json()["recipes"][0]["name"] == "계란밥"
