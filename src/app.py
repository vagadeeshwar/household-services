import os

from dotenv import load_dotenv
from flask import Flask, send_from_directory
from flask_cors import CORS

from src import db, ma
from src.setup_db import setup_database  # type: ignore # noqa
from src.utils.api import register_error_handlers
from src.utils.cache import init_cache
from src.utils.file import UPLOAD_FOLDER
from src.utils.notification import mail


def create_app():
    # Initialize Flask app
    app = Flask(
        __name__,
        static_folder="../build",
        static_url_path="",
        template_folder="../templates",
    )
    CORS(app)
    load_dotenv()

    # Configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///database.sqlite3"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your-secret-key-here")

    app.config.update(
        MAIL_SERVER="smtp.gmail.com",
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER=os.getenv(
            "MAIL_DEFAULT_SENDER", "noreply@householdservices.com"
        ),
        MAIL_DEBUG=True,  # Add this for debugging
    )

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    init_cache(app)
    mail.init_app(app)

    # with app.app_context():
    #     setup_database()

    # Register blueprints
    from src.routes.auth import auth_bp
    from src.routes.contact import contact_bp
    from src.routes.customer import customer_bp
    from src.routes.export import export_bp
    from src.routes.professional import professional_bp
    from src.routes.request import request_bp
    from src.routes.service import service_bp
    from src.routes.user import user_bp

    app.register_blueprint(user_bp, url_prefix="/api")
    app.register_blueprint(customer_bp, url_prefix="/api")
    app.register_blueprint(professional_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(service_bp, url_prefix="/api")
    app.register_blueprint(request_bp, url_prefix="/api")
    app.register_blueprint(export_bp, url_prefix="/api")
    app.register_blueprint(contact_bp, url_prefix="/api")

    # Register error handler
    register_error_handlers(app)

    @app.route("/static/uploads/verification_docs/<path:filename>")
    def serve_verification_document(filename):
        """Serve verification documents"""
        return send_from_directory(os.path.join(app.root_path, UPLOAD_FOLDER), filename)

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
