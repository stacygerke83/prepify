import os
import services.spoonacular_client as sc
from unittest.mock import patch

def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("SPOONACULAR_API_KEY", raising=False)
    try:
        sc.find_by_ingredients(["apple"])
        assert False, "Expected SpoonacularClientError"
    except sc.SpoonacularClientError:
        assert True

@patch("services.spoonacular_client.requests.get")
def test_find_by_ingredients_happy_path(mock_get, monkeypatch):
    monkeypatch.setenv("SPOONACULAR_API_KEY", "fake-key")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [
        {"id": 123, "title": "Apple Pie", "image": "http://img", "usedIngredientCount": 2, "missedIngredientCount": 1}
    ]
    result = sc.find_by_ingredients(["apples", "flour"], number=3, ranking=1)
    assert len(result) == 1
    assert result[0]["title"] == "Apple Pie"
    assert "link" in result[0]

def test_no_ingredients_raises(monkeypatch):
    monkeypatch.setenv("SPOONACULAR_API_KEY", "fake-key")
    try:
        sc.find_by_ingredients([], number=3)
        assert False, "Expected SpoonacularClientError"
    except sc.SpoonacularClientError:
        assert True
