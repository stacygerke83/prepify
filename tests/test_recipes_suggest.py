import os
import json
import types
import pytest

from backend.app import app as flask_app


@pytest.fixture(scope="module")
def client():
    """
    Flask test client. Uses the app defined in backend/app.py.
    """
    flask_app.testing = True
    with flask_app.test_client() as c:
        yield c

def test_recipes_suggest_mocked_requests(monkeypatch, client):
    """
    Unit test that mocks requests.get to avoid external API calls.
    Verifies:
      - 200 response
      - JSON structure contains 'recipes' list with expected fields
    """

    fake_response_data = [
        {
            "id": 12345,
            "title": "Chicken Tomato Rice",
            "image": "https://spoonacular.com/recipeImages/12345-312x231.jpg",
            "usedIngredientCount": 3,
            "missedIngredientCount": 0,
        },
        {
            "id": 67890,
            "title": "Tomato Rice with Chicken",
            "image": "https://spoonacular.com/recipeImages/67890-312x231.jpg",
            "usedIngredientCount": 2,
            "missedIngredientCount": 1,
        },
    ]

    class FakeResp:
        def __init__(self, json_data, status_code=200):
            self._json_data = json_data
            self.status_code = status_code
            self.text = json.dumps(json_data)

        def raise_for_status(self):
            if not (200 <= self.status_code < 300):
                raise Exception(f"HTTP {self.status_code}")

        def json(self):
            return self._json_data

    def fake_requests_get(url, params=None, timeout=15):
        # You can assert the URL or params if desired
        assert "findByIngredients" in url
        assert "ingredients" in params
        assert "apiKey" in params  # your code always sends apiKey
        return FakeResp(fake_response_data, 200)

    import backend.app as app_module
    monkeypatch.setattr(app_module.requests, "get", fake_requests_get)

    resp = client.get("/recipes/suggest?ingredients=chicken,tomato,rice&number=5")
    assert resp.status_code == 200

    payload = resp.get_json()
    assert "recipes" in payload
    assert isinstance(payload["recipes"], list)
