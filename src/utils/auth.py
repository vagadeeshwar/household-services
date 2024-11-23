from functools import wraps
from flask import request, current_app, jsonify
from http import HTTPStatus
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
                return APIResponse.error(
                    message="Invalid token format",
                    status_code=HTTPStatus.UNAUTHORIZED,
                    error_type="InvalidTokenFormat",
                )

        if not token:
            return APIResponse.error(
                message="Token is missing",
                status_code=HTTPStatus.UNAUTHORIZED,
                error_type="MissingToken",
            )

        try:
            data = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            current_user = User.query.get(data["user_id"])
            if not current_user or not current_user.is_active:
                return APIResponse.error(
                    message="Invalid or inactive user",
                    status_code=HTTPStatus.UNAUTHORIZED,
                    error_type="InvalidUser",
                )
        except jwt.ExpiredSignatureError:
            return APIResponse.error(
                message="Token has expired",
                status_code=HTTPStatus.UNAUTHORIZED,
                error_type="TokenExpired",
            )
        except jwt.InvalidTokenError:
            return APIResponse.error(
                message="Invalid token",
                status_code=HTTPStatus.UNAUTHORIZED,
                error_type="InvalidToken",
            )

        return f(current_user, *args, **kwargs)

    return decorated


def role_required(*roles):
    """Decorator to restrict routes based on user role"""

    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if current_user.role not in roles:
                return APIResponse.error(
                    message="Permission denied",
                    status_code=HTTPStatus.FORBIDDEN,
                    error_type="InsufficientPermissions",
                )
            return f(current_user, *args, **kwargs)

        return decorated_function

    return decorator


class APIResponse:
    """Unified API Response Handler"""

    @staticmethod
    def success(data=None, message=None, status_code=HTTPStatus.OK):
        response = {
            "data": data,
            "status": "success",
            "status_code": status_code,
            "detail": message,
        }
        return jsonify(response), status_code

    @staticmethod
    def error(message, status_code=HTTPStatus.BAD_REQUEST, error_type=None):
        """
        Centralized error response method
        Also handles database rollback when needed
        """
        if status_code >= 500:  # Server errors
            db.session.rollback()

        response = {
            "data": None,
            "status": "failure",
            "status_code": status_code,
            "detail": message,
            "error_type": error_type,
        }
        return jsonify(response), status_code


# Register error handler with Flask app
def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle all unhandled exceptions"""
        app.logger.error(f"Unhandled exception: {str(e)}")
        return APIResponse.error(
            message="An unexpected error occurred",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    @app.errorhandler(HTTPStatus.NOT_FOUND)
    def handle_404(e):
        """Handle 404 errors"""
        return APIResponse.error(
            message="Resource not found",
            status_code=HTTPStatus.NOT_FOUND,
        )

    @app.errorhandler(HTTPStatus.METHOD_NOT_ALLOWED)
    def handle_405(e):
        """Handle 405 errors"""
        return APIResponse.error(
            message="Method not allowed",
            status_code=HTTPStatus.METHOD_NOT_ALLOWED,
        )
