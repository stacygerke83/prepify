# /Users/sgerke/Desktop/prepify/prepify/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///prepify.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')
    db.init_app(app)

    from .routes import pantry_bp
    app.register_blueprint(pantry_bp)

    @app.route('/__whoami')
    def whoami():
        # This will return the path to THIS file (the module where this function is defined)
        return __file__, 200

    with app.app_context():
        db.create_all()

    return app
