# app.py
import os
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

def create_app():
    """Application factory that returns a configured Flask app."""
    # Load .env from repo root
    root_env = Path(__file__).resolve().parent / ".env"
    if root_env.exists():
        load_dotenv(root_env)

    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # --- Routes (inline) ---
    @app.route("/debug/routes", methods=["GET"])
    def list_routes():
        routes = sorted([str(rule) for rule in app.url_map.iter_rules()])
        return jsonify({"routes": routes}), 200

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

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
            return jsonify({"error": "Provide non-empty 'ingredients' list."}), 400

        # TODO: plug in your real logic here if you had services/* modules before
        recipes = [{"title": "Sample Recipe", "link": "https://example.com"}] * count
        return jsonify({"recipes": recipes}), 200

    @app.route("/weekly-menu", methods=["POST"])
    def weekly_menu():
        data = request.get_json(force=True) or {}
        days = int(data.get("days", 7))
        # TODO: plug in your real logic here
        menu = {f"day_{i+1}": {"breakfast": "oatmeal", "dinner": "salad"} for i in range(days)}
        return jsonify({"menu": menu}), 200

    return app


if __name__ == "__main__":
    # Allow `python app.py` to work, too.
    app = create_app()
    port = int(os.getenv("PORT", "5000"))
    print("[INFO] Env loaded:", "SET" if os.getenv("SPOONACULAR_API_KEY") else "NOT SET")
    print("[INFO] Starting Prepify backend on http://127.0.0.1:%d" % port)
    print("[INFO] Registered routes:")
    for rule in app.url_map.iter_rules():
        print("  -", rule)
    app.run(host="0.0.0.0", port=port, debug=True)
