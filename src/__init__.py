import os
from flask import Flask, send_from_directory
from ..config import LocalDevelopmentConfig, ProductionConfig
from .database import db, create_tables
from .api.api import api_bp
from .utils import create_dummy_data


def register_blueprints(app):
    app.register_blueprint(api_bp, url_prefix="/api")


def configure_app(app):
    if os.getenv("ENV", "development") == "production":
        print("Starting Production Server")
        app.config.from_object(ProductionConfig)
    else:
        print("Starting Local Development")
        app.config.from_object(LocalDevelopmentConfig)


def init_db(app):
    db.init_app(app)

    app.app_context().push()
    with app.app_context():
        create_tables()


# def setup_login_manager(app):
#     login_manager = LoginManager()
#     login_manager.init_app(app)
#     login_manager.login_view = "user.login"

#     @login_manager.user_loader
#     def load_user(user_id):
#         return User.query.get(int(user_id))

#     def unauthorized_callback():
#         flash("Please log in to access this page.", "info")
#         return redirect(url_for("user.login"))

#     login_manager.unauthorized_handler(unauthorized_callback)


def create_app():
    app = Flask(__name__, static_folder="./dist", static_url_path="")

    @app.route("/")
    def serve_vue_app():
        return send_from_directory(app.static_folder, "index.html")

    register_blueprints(app)
    # setup_login_manager(app)

    configure_app(app)
    init_db(app)
    create_dummy_data(app)

    return app
