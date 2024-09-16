import os
from flask import send_from_directory
from flask import Flask
from dotenv import load_dotenv
import src.models  # Import models so tables are created
from src.setup_db import setup_database  # Import setup_database to handle table creation and dummy data
from . import db


def create_app():
    app = Flask(__name__)
    load_dotenv()

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///database.sqlite3"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
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
