from src.models import User
from src.utils.api import APIResponse
from http import HTTPStatus


def check_existing_user(username: str, email: str) -> tuple[bool, tuple]:
    """Check if username or email already exists"""
    if User.query.filter_by(username=username).first():
        return True, APIResponse.error(
            "Username already exists", HTTPStatus.CONFLICT, "DuplicateUsername"
        )

    if User.query.filter_by(email=email).first():
        return True, APIResponse.error(
            "Email already exists", HTTPStatus.CONFLICT, "DuplicateEmail"
        )

    return False, None
