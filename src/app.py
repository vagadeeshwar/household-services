import os
import logging
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask-SQLAlchemy
db = SQLAlchemy()


def create_app():
    app = Flask(__name__, static_folder="../build", static_url_path="/")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///database.sqlite3"
    )

    # Initialize the database with the Flask app context
    db.init_app(app)

    @app.route("/")
    def serve_vue_app():
        index_path = os.path.join(app.static_folder, "index.html")
        if not os.path.exists(index_path):
            logger.error(f"index.html not found at {index_path}")
            return "index.html not found", 404
        logger.info(f"Serving index.html from {index_path}")
        return send_from_directory(app.static_folder, "index.html")

    # Add more routes and configurations as needed

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8080, debug=True)
