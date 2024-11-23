import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from src.utils.auth import handle_api_error, APIError
from src import db, ma
from src.setup_db import setup_database  # noqa


def create_app():
    # Initialize Flask app
    app = Flask(__name__, static_folder="../build", static_url_path="")
    CORS(app)
    load_dotenv()

    # Configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///database.sqlite3"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your-secret-key-here")

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)

    # with app.app_context():
    #     setup_database()

    # Register blueprints
    from src.routes.auth import auth_bp
    from src.routes.service import service_bp
    from src.routes.admin import admin_bp
    from src.routes.request import request_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(service_bp, url_prefix="/api/services")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(request_bp, url_prefix="/api/requests")

    # Register error handler
    app.register_error_handler(APIError, handle_api_error)

    # Serve SPA
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_vue_app(path):
        try:
            if path and os.path.exists(os.path.join(app.static_folder, path)):
                return send_from_directory(app.static_folder, path)
            return send_from_directory(app.static_folder, "index.html")
        except Exception:
            return send_from_directory(app.static_folder, "index.html")

    return app


app = create_app()
