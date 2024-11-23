import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import src.models  # noqa
from src.utils.auth import handle_api_error, APIError
from src import db, ma
from src.setup_db import setup_database  # noqa


def create_app():
    # Get absolute path to the build directory
    build_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "build"))

    # Debug info
    print(f"Current working directory: {os.getcwd()}")
    print(f"Looking for build directory at: {build_path}")

    if not os.path.exists(build_path):
        print(
            "WARNING: Build directory not found! Please run 'npm run build' in the frontend directory"
        )
        os.makedirs(build_path, exist_ok=True)
        with open(os.path.join(build_path, "index.html"), "w") as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head><title>Development Mode</title></head>
            <body>
                <h1>Development Mode</h1>
                <p>Vue.js build not found. Please:</p>
                <ol>
                    <li>cd frontend</li>
                    <li>npm install (if you haven't already)</li>
                    <li>npm run build</li>
                </ol>
            </body>
            </html>
            """)

    app = Flask(__name__, static_folder=build_path, static_url_path="")
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

    # Initialize database within app context
    with app.app_context():
        setup_database()

    # Serve static files
    @app.route("/static/<path:path>")
    def serve_static(path):
        try:
            return send_from_directory(os.path.join(app.static_folder, "static"), path)
        except Exception as e:
            print(f"Error serving static file {path}: {str(e)}")
            return str(e), 404

    # Handle all other routes by serving index.html
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_vue_app(path):
        try:
            if path and os.path.exists(os.path.join(app.static_folder, path)):
                return send_from_directory(app.static_folder, path)
            return send_from_directory(app.static_folder, "index.html")
        except Exception as e:
            print(f"Error serving path {path}: {str(e)}")
            return send_from_directory(app.static_folder, "index.html")

    @app.after_request
    def add_header(response):
        # Prevent caching during development
        if app.debug:
            response.headers["Cache-Control"] = "no-store"
        return response

    return app


app = create_app()
