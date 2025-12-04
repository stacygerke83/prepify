# prepify/app_factory.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:' if testing else 'sqlite:///prepify.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        TESTING=testing,
        SECRET_KEY='dev',
    )
    db.init_app(app)

    from . import models  # noqa: F401

    try:
        from .routes import register_routes
        register_routes(app)
    except ImportError:
        try:
            from .routes import bp as routes_bp
            app.register_blueprint(routes_bp)
        except Exception:
            pass

    if testing:
        with app.app_context():
            db.create_all()

    return app
