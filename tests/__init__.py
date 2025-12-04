from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:' if testing else 'sqlite:///prepify.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        TESTING=testing,
        SECRET_KEY='dev',  # replace in production
    )

    db.init_app(app)

    try:
        from .routes import register_routes  # function that takes app
        register_routes(app)
    except ImportError:
        # If routes are defined with Blueprints instead:
        try:
            from .routes import bp as routes_bp  # Blueprint instance named 'bp'
            app.register_blueprint(routes_bp)
        except Exception:
            # No routes module yet; it's fine for tests that only check DB/model behavior
            pass

    if testing:
        with app.app_context():
            db.create_all()

    return app
