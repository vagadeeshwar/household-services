import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import src.models  # noqa Import models so tables are created
from src.setup_db import setup_database
from src.utils.auth import handle_api_error, APIError
from src import db, ma


def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS
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

    with app.app_context():
        # Import blueprints
        from src.routes.auth import auth_bp
        from src.routes.service import service_bp
        from src.routes.admin import admin_bp
        from src.routes.request import request_bp

        # Register blueprints
        app.register_blueprint(auth_bp, url_prefix="/api/auth")
        app.register_blueprint(service_bp, url_prefix="/api/services")
        app.register_blueprint(admin_bp, url_prefix="/api/admin")
        app.register_blueprint(request_bp, url_prefix="/api/requests")

        # Register error handlers
        app.register_error_handler(APIError, handle_api_error)

        # Drop all tables and recreate them
        setup_database()

    return app


app = create_app()


@app.route("/")
def serve_vue_app():
    index_path = os.path.join(app.static_folder, "index.html")
    if not os.path.exists(index_path):
        return "index.html not found", 404
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
