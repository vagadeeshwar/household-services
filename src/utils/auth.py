from functools import wraps
from flask import jsonify, request, current_app
import jwt
from datetime import datetime, timedelta
from src.models import User
from src import db


def generate_token(user_id: int, role: str) -> str:
    """Generate JWT token for user"""
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=1),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def token_required(f):
    """Decorator to protect routes with JWT"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"message": "Invalid token format"}), 401

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            data = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            current_user = User.query.get(data["user_id"])
            if not current_user or not current_user.is_active:
                return jsonify({"message": "Invalid or inactive user"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


def role_required(*roles):
    """Decorator to restrict routes based on user role"""

    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if current_user.role not in roles:
                return jsonify({"message": "Permission denied"}), 403
            return f(current_user, *args, **kwargs)

        return decorated_function

    return decorator


def handle_api_error(e):
    """Generic error handler for API exceptions"""
    db.session.rollback()
    return jsonify({"error": str(e), "type": e.__class__.__name__}), getattr(
        e, "code", 500
    )


class APIError(Exception):
    """Base exception for API errors"""

    def __init__(self, message, code=400):
        super().__init__(message)
        self.code = code
