from datetime import datetime, timezone
from http import HTTPStatus

from flask import Blueprint, request
from marshmallow import ValidationError

from src import db
from src.constants import (
    ActivityLogActions,
)
from src.models import (
    ActivityLog,
    User,
)
from src.schemas.auth import (
    login_schema,
    token_schema,
)
from src.utils.auth import APIResponse, generate_token
from src.utils.cache import cache_invalidate

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login route for all user types"""
    try:
        data = login_schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(str(err.messages))

    user = User.query.filter_by(username=data["username"]).first()

    if not user or not user.check_password(data["password"]):
        return APIResponse.error(
            "Invalid credentials", HTTPStatus.UNAUTHORIZED, "InvalidCredentials"
        )

    if not user.is_active:
        return APIResponse.error(
            "Account is deactivated", HTTPStatus.FORBIDDEN, "InactiveAccount"
        )
    if user.role == "professional" and not user.professional_profile.is_verified:
        return APIResponse.error(
            "Professional profile is not verified",
            HTTPStatus.FORBIDDEN,
            "UnverifiedProfessional",
        )

    try:
        user.last_login = datetime.now(timezone.utc)

        log = ActivityLog(
            user_id=user.id,
            action=ActivityLogActions.USER_LOGIN,
            description=f"User {user.username} logged in successfully",
        )
        db.session.add(log)
        db.session.commit()
        cache_invalidate()

        token = generate_token(user.id, user.role)
        return APIResponse.success(
            data=token_schema.dump({"token": token}), message="Login successful"
        )
    except Exception as e:
        return APIResponse.error(
            f"Error during login: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )
