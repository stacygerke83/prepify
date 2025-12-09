import os
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# --- Load .env from backend directory or repo root ---
# Attempt to load backend/.env first
backend_env = Path(__file__).parent / ".env"
root_env = Path(__file__).resolve().parents[1] / ".env"  # one level up from backend/

if backend_env.exists():
    load_dotenv(backend_env)
elif root_env.exists():
    load_dotenv(root_env)
else:
    # Fallback: no .env file found; rely on OS environment variables
    pass

# Now you can access env vars via os.getenv(...)
# e.g., SPOONACULAR_API_KEY will be available if set in .env or in the OS

from services.recipe_api import get_recipes_with_links, SpoonacularError
from services.weekly_menu import generate_weekly_menu

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/recipes/suggest", methods=["POST"])
def suggest_recipes():
    data = request.get_json(force=True) or {}
    ingredients = data.get("ingredients", [])
    count = int(data.get("count", 5))
    ranking = int(data.get("ranking", 1))

    if not isinstance(ingredients, list) or not ingredients:
        return jsonify({"error": "Provide non-empty 'ingredients' list."}), 400

    try:
        recipes = get_recipes_with_links(ingredients, number=count, ranking=ranking)
        return jsonify({"recipes": recipes}), 200
    except SpoonacularError as e:
        return jsonify({"error": str(e)}), 502

@app.route("/weekly-menu", methods=["POST"])
def weekly_menu():
    data = request.get_json(force=True) or {}
    ingredients = data.get("ingredients", [])
    days = int(data.get("days", 7))
    count = int(data.get("count", max(days * 2, 10)))
    ranking = int(data.get("ranking", 1))

    if not isinstance(ingredients, list) or not ingredients:
        return jsonify({"error": "Provide non-empty 'ingredients' list."}), 400

    try:
        candidates = get_recipes_with_links(ingredients, number=count, ranking=ranking)
        menu = generate_weekly_menu(candidates, days=days)
        return jsonify({"menu": menu}), 200
    except SpoonacularError as e:
        return jsonify({"error": str(e)}), 502

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
