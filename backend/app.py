import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path

# Load .env file (backend/.env or root .env)
backend_env = Path(__file__).parent / ".env"
root_env = Path(__file__).resolve().parents[1] / ".env"
if backend_env.exists():
    load_dotenv(backend_env)
elif root_env.exists():
    load_dotenv(root_env)

app = Flask(__name__)
CORS(app)

# ✅ Add this route anywhere after app = Flask(...) and before app.run()
@app.route("/env-check", methods=["GET"])
def env_check():
    value = os.getenv("SPOONACULAR_API_KEY")
    # Don't return the actual secret—just whether it exists
    return {"hasKey": bool(value)}, 200

# Example: your other routes (recipes, weekly menu) go here
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
