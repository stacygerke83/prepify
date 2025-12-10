import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path

import requests as _requests
requests = _requests 

backend_env = Path(__file__).parent / ".env"
root_env = Path(__file__).resolve().parents[1] / ".env"

if backend_env.exists():
    load_dotenv(backend_env)
elif root_env.exists():
    load_dotenv(root_env)
else:
    load_dotenv()

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("SPOONACULAR_API_KEY", "")

@app.route("/env-check", methods=["GET"])
def env_check():
    # Return whether the key exists; do not expose the key value.
    return jsonify({"hasKey": bool(API_KEY)}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/recipes/suggest", methods=["GET"])
def recipes_suggest():
    """
    Usage:
      GET /recipes/suggest?ingredients=chicken,tomato,rice&number=5

    Returns:
      A JSON list of recipe dicts:
      [
        { id, title, image, usedIngredientCount, missedIngredientCount },
        ...
      ]
    """
    ingredients = (request.args.get("ingredients") or "").strip()
    if not ingredients:
        return jsonify({"error": "Missing required query parameter: ingredients"}), 400

    number_raw = request.args.get("number", "5")
    try:
        number = max(1, min(int(number_raw), 10))
    except ValueError:
        number = 5

    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "ingredients": ingredients,
        "number": number,
        "ranking": 1,
        "ignorePantry": True,
        # Always include apiKey for the mocked test assertion,
        # even if it's empty (integration test will skip if missing).
        "apiKey": API_KEY,
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()  # list of recipe dicts
    except requests.RequestException as e:
        status = getattr(e.response, "status_code", 502)
        body = getattr(e.response, "text", str(e))
        return jsonify({"error": "Spoonacular request failed", "status": status, "details": body}), 502

    # Return only fields the tests check
    results = [
        {
            "id": r.get("id"),
            "title": r.get("title"),
            "image": r.get("image"),
            "usedIngredientCount": r.get("usedIngredientCount"),
            "missedIngredientCount": r.get("missedIngredientCount"),
        }
        for r in data
    ]

    return jsonify(results), 200

if __name__ == "__main__":
    app.run(debug=True)
