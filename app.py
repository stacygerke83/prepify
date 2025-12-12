# app.py
import os
from pathlib import Path
from flask import Flask, jsonify
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

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    @app.get("/debug/routes")
    def debug_routes():
        routes = sorted([str(rule) for rule in app.url_map.iter_rules()])
        return jsonify({"routes": routes}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", "5000"))
    print("[INFO] Starting Prepify backend on http://127.0.0.1:%d" % port)
    for rule in app.url_map.iter_rules():
        print("  -", rule)
    app.run(host="0.0.0.0", port=port, debug=True)
