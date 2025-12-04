# prepify/__init__.py
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
import os
import sqlite3

db = SQLAlchemy()

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    try:
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()
    except Exception:
        # Don't crash app startup if pragma fails
        pass

def create_app():
    app = Flask(__name__)

    # ---- Config ----
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///prepify.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')

    # ---- Init DB ----
    db.init_app(app)

    with app.app_context():
        from .models import PantryItem  # noqa: F401
        db.create_all()

    from .routes import pantry_bp
    app.register_blueprint(pantry_bp)  # No prefix → URLs are /pantry, /pantry/<int:item_id>

    @app.route('/__whoami')
    def whoami():
        return __file__, 200

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        # Werkzeug HTTPException will be auto-handled; this catches others
        from sqlalchemy.exc import SQLAlchemyError
        if isinstance(e, SQLAlchemyError):
            # Return DB errors consistently
            return jsonify({'error': 'Database error', 'details': str(e)}), 500
        # Fallback
