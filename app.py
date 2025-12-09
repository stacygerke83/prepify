import os
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Load .env from repo root
root_env = Path(__file__).parent / ".env"
if root_env.exists():
    load_dotenv(root_env)

# Create app if you're not using app_factory
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

from services.recipe_api import get_recipes_with_links, SpoonacularError
from services.weekly_menu import generate_weekly_menu

@app.route("/env-check", methods=["GET"])
def env_check():
    return {"hasKey": bool(os.getenv("SPOONACULAR_API_KEY"))}, 200

@app.route("/recipes/suggest", methods=["POST"])
def suggest_recipes():
    data = request.get_json(force=True) or {}
    ingredients = data.get("ingredients", [])
    count = int(data.get("count", 5))
    ranking = int(data.get("ranking", 1))
    if not isinstance(ingredients, list) or not ingredients:
        return {"error": "Provide non-empty 'ingredients' list."}, 400
    try:
        recipes = get_recipes_with_links(ingredients, number=count, ranking=ranking)
        return {"recipes": recipes}, 200
    except SpoonacularError as e:
        return {"error": str(e)}, 502

@app.route("/weekly-menu", methods=["POST"])
def weekly_menu():
    data = request.get_json(force=True) or {}
    ingredients = data.get("ingredients", [])
    days = int(data.get("days", 7))
    count = int(data.get("count", max(days * 2, 10)))
    ranking = int(data.get("ranking", 1))
    if not isinstance(ingredients, list) or not ingredients:
        return {"error": "Provide non-empty 'ingredients' list."}, 400
    try:
        candidates = get_recipes_with_links(ingredients, number=count, ranking=ranking)
        menu = generate_weekly_menu(candidates, days=days)
        return {"menu": menu}, 200
    except SpoonacularError as e:
        return {"error": str(e)}, 502

if __name__ == "__main__":
    print("[INFO] Env loaded:", "SET" if os.getenv("SPOONACULAR_API_KEY") else "NOT SET")
    app.run(host="0.0.0.0", port=5000, debug=True)
