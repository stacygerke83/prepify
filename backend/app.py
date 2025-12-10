import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path
import requests

backend_env = Path(__file__).parent / ".env"
root_env = Path(__file__).resolve().parents[1] / ".env"  # adjust if your repo root differs

if backend_env.exists():
    load_dotenv(backend_env)
elif root_env.exists():
    load_dotenv(root_env)
else:
    # Fallback: load from whichever current working directory you're running in
    load_dotenv()

app = Flask(__name__)
CORS(app)  # enable CORS for local dev; tighten later for production

API_KEY = os.getenv("SPOONACULAR_API_KEY")

# Optional: fail fast if key is missing
if not API_KEY:
    # You can change this to a warning if you prefer not to crash:
    # print("WARNING: SPOONACULAR_API_KEY missing. Set it in backend/.env")
    raise RuntimeError("SPOONACULAR_API_KEY is missing. Set it in your .env file.")

@app.route("/env-check", methods=["GET"])
def env_check():
    # Don't return the key itself—only whether it exists
    return jsonify({"hasKey": bool(API_KEY)}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.get("/recipes/suggest")
def recipe_suggest():
    """
    Usage:
      GET /recipes/suggest?ingredients=chicken,tomato,rice&number=5

    Returns:
      { "recipes": [ { id, title, image, sourceUrl, usedIngredientCount, missedIngredientCount }, ... ] }
    """
    ingredients = request.args.get("ingredients", "").strip()
    if not ingredients:
        return jsonify({"error": "No ingredients provided. Pass ?ingredients=comma,separated,list"}), 400

    number = int(request.args.get("number", 5))
    number = max(1, min(number, 10))  # safe bounds

    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "apiKey": API_KEY,
        "ingredients": ingredients,  # comma-separated values
        "number": number,
        "ranking": 1,                # prioritize more matches from pantry
        "ignorePantry": True
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()  # list of recipe dicts
    except requests.RequestException as e:
        status = getattr(e.response, "status_code", 502)
        body = getattr(e.response, "text", str(e))
        return jsonify({"error": "Spoonacular request failed", "status": status, "details": body}), 502

    # Normalize for UI
    recipes = [{
        "id": r.get("id"),
        "title": r.get("title"),
        "image": r.get("image"),
        "usedIngredientCount": r.get("usedIngredientCount"),
        "missedIngredientCount": r.get("missedIngredientCount"),
        "sourceUrl": f"https://spoonacular.com/recipes/{(r.get('title') or '').replace(' ', '-')}-{r.get('id')}"
    } for r in data]

    return jsonify({"recipes": recipes}), 200

if __name__ == "__main__":
    # Run directly: python app.py
