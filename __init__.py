import os
from pathlib import Path
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from dotenv import load_dotenv


def create_app():
    """
    Application factory that returns a configured Flask app.
    All routes are registered directly on this app instance (no blueprints).
    """
    # Load environment variables from project root .env (if present)
    root_env = Path(__file__).resolve().parent.parent / ".env"
    if root_env.exists():
        load_dotenv(root_env)

    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.get("/")
    def home():
        return "Prepify API is running! Try GET /health or GET /debug/routes", 200

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    @app.get("/debug/routes")
    def debug_routes():
        routes = sorted([str(rule) for rule in app.url_map.iter_rules()])
        return jsonify({"routes": routes}), 200

    pantry = []

    @app.get("/pantry")
    def get_pantry():
        return jsonify(pantry), 200

    @app.post("/pantry")
    def add_item():
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        quantity = data.get("quantity")
        if not name:
            return jsonify({"error": "name is required"}), 400
        pantry.append({"name": name, "quantity": quantity})
        return jsonify({"name": name, "quantity": quantity}), 201

    @app.put("/pantry/<int:item_id>")
    def update_item(item_id):
        if item_id < 0 or item_id >= len(pantry):
            return jsonify({"error": "Item not found"}), 404
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        quantity = data.get("quantity")
        if not name:
            return jsonify({"error": "name is required"}), 400
        pantry[item_id] = {"name": name, "quantity": quantity}
        return jsonify(pantry[item_id]), 200

    @app.delete("/pantry/<int:item_id>")
    def delete_item(item_id):
        if item_id < 0 or item_id >= len(pantry):
            return jsonify({"error": "Item not found"}), 404
        pantry.pop(item_id)
        return Response(status=204)

    @app.post("/recipes/suggest")
    def suggest_recipes():
        """
        Suggest recipes based on provided ingredients.
        Replace the placeholder logic with your real implementation.
        Expected JSON:
        {
            "ingredients": ["tomato", "basil"],
            "count": 5,
            "ranking": 1
        }
        """
        data = request.get_json(silent=True) or {}
        ingredients = data.get("ingredients", [])
        count = int(data.get("count", 5))
        ranking = int(data.get("ranking", 1))

        if not isinstance(ingredients, list) or not ingredients:
            return jsonify({"error": "Provide non-empty 'ingredients' list."}), 400

        recipes = [{"title": "Sample Recipe", "link": "https://example.com"}] * count
        return jsonify({"recipes": recipes}), 200

    @app.get("/env-check")
    def env_check():
        return {"hasKey": bool(os.getenv("SPOONACULAR_API_KEY"))}, 200
