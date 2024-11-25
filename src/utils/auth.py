from functools import wraps
from flask import request, current_app
from http import HTTPStatus
import jwt
from datetime import datetime, timedelta
from src.models import User
from src.utils.api import APIResponse


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
