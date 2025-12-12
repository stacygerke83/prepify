import os
from pathlib import Path
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

def create_app():
    """Application factory that returns a configured Flask app."""
    # Load .env from project root
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

    # If you use a blueprint or registrar for recipes, register it here:
    try:
        from app.routes.recipes import register_recipes_routes
        register_recipes_routes(app)
    except ImportError:
        # If you’re using a blueprint instead, uncomment the next two lines:
        # from app.routes.recipes import recipes_bp
        # app.register_blueprint(recipes_bp)
        pass

    return app
