# import os
from flask import Flask, send_from_directory
from src.database import db, create_tables
import os
from dotenv import load_dotenv

# from .api.api import api_bp
import logging

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="../build", static_url_path="/")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")


# def register_blueprints(app):
#     app.register_blueprint(api_bp, url_prefix="/api")


# def configure_app(app):
#     # Load environment variables from .env file
#     basedir = os.path.abspath(os.path.dirname(__file__))
#     load_dotenv(os.path.join(basedir, ".env"))

#     # Update app configuration
#     app.config["DEBUG"] = os.getenv("DEBUG", "False").lower() == "true"
#     app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
#         "SQLALCHEMY_DATABASE_URI", "sqlite:///database.sqlite3"
#     )

#     logger.info("Configuration loaded from .env")


def init_db(app):
    db.init_app(app)

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


@app.route("/")
def serve_vue_app():
    # Check if index.html exists
    index_path = os.path.join(app.static_folder, "index.html")
    if not os.path.exists(index_path):
        logger.error(f"index.html not found at {index_path}")
        return "index.html not found", 404
    logger.info(f"Serving index.html from {index_path}")
    return send_from_directory(app.static_folder, "index.html")

# register_blueprints(app)
# setup_login_manager(app)

# configure_app(app)
init_db(app)
# create_dummy_data(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
