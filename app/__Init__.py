from flask import Flask
from app.routes.recipes import recipes_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(recipes_bp)
    return app
