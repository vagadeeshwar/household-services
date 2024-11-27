from flask import Blueprint, request
from marshmallow import ValidationError
from http import HTTPStatus

from src import db

from src.models import (
    User,
    ServiceRequest,
    ActivityLog,
)

from src.constants import (
    USER_ROLE_PROFESSIONAL,
    USER_ROLE_CUSTOMER,
    ActivityLogActions,
    REQUEST_STATUS_ASSIGNED,
    REQUEST_STATUS_CREATED,
)

from src.schemas.user import (
    password_update_schema,
    delete_account_schema,
    admin_output_schema,
)
from src.schemas.customer import (
    customer_output_schema,
    customer_update_schema,
)
from src.schemas.professional import (
    professional_output_schema,
    professional_update_schema,
)


from src.utils.auth import token_required, APIResponse, role_required
from src.utils.file import delete_verification_document

user_bp = Blueprint("user", __name__)


@user_bp.route("/profile", methods=["GET"])
@token_required
def get_profile(current_user):
    """Get current user's profile"""
    try:
        if current_user.role == USER_ROLE_PROFESSIONAL:
            schema = professional_output_schema
            message = "Professional profile retrieved successfully"
        elif current_user.role == USER_ROLE_CUSTOMER:
            schema = customer_output_schema
            message = f"{current_user.role.capitalize()} profile retrieved successfully"
        else:
            schema = admin_output_schema
            message = f"{current_user.role.capitalize()} profile retrieved successfully"

        return APIResponse.success(data=schema.dump(current_user), message=message)
    except Exception as e:
        return APIResponse.error(
            f"Error retrieving profile: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@user_bp.route("/change-password", methods=["POST"])
@token_required
@role_required("customer", "professional")
def change_password(current_user):
    """Change user's password"""
    try:
        data = password_update_schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(str(err.messages))

    if not current_user.check_password(data["old_password"]):
        return APIResponse.error(
            "Current password is incorrect", HTTPStatus.UNAUTHORIZED, "InvalidPassword"
        )

    try:
        current_user.set_password(data["new_password"])

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.USER_PASSWORD_CHANGE,
            description=f"Password changed for user {current_user.username}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(message="Password changed successfully")
    except Exception as e:
        return APIResponse.error(
            f"Error changing password: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@user_bp.route("/profile", methods=["PUT"])
@token_required
@role_required("customer", "professional")
def update_profile(current_user):
    """Update user's profile information"""
    try:
        schema = (
            professional_update_schema
            if current_user.role == USER_ROLE_PROFESSIONAL
            else customer_update_schema
        )
        data = schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(str(err.messages))

    try:
        if "email" in data and data["email"] != current_user.email:
            if User.query.filter_by(email=data["email"]).first():
                return APIResponse.error(
                    "Email already in use", HTTPStatus.CONFLICT, "DuplicateEmail"
                )
            current_user.email = data["email"]

        for field in ["full_name", "phone", "address", "pin_code"]:
            if field in data:
                setattr(current_user, field, data[field])

        if current_user.role == USER_ROLE_PROFESSIONAL and "description" in data:
            current_user.professional_profile.description = data["description"]

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.USER_PROFILE_UPDATE,
            description=f"Profile updated for user {current_user.username}",
        )
        db.session.add(log)
        db.session.commit()

        schema = (
            professional_output_schema
            if current_user.role == USER_ROLE_PROFESSIONAL
            else customer_output_schema
        )
        return APIResponse.success(
            data=schema.dump(current_user), message="Profile updated successfully"
        )
    except Exception as e:
        return APIResponse.error(
            f"Error updating profile: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@user_bp.route("/delete-account", methods=["DELETE"])
@token_required
@role_required("customer", "professional")
def delete_account(current_user):
    """Hard delete user account"""
    try:
        data = delete_account_schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(str(err.messages))

    if not current_user.check_password(data["password"]):
        return APIResponse.error(
            "Incorrect password", HTTPStatus.UNAUTHORIZED, "InvalidPassword"
        )

    try:
        # Check for active requests based on user role
        if current_user.role == USER_ROLE_PROFESSIONAL:
            has_active_requests = (
                ServiceRequest.query.filter(
                    ServiceRequest.professional_id
                    == current_user.professional_profile.id,
                    ServiceRequest.status.in_([REQUEST_STATUS_ASSIGNED]),
                ).first()
                is not None
            )
            verification_doc = current_user.professional_profile.verification_documents
        else:
            has_active_requests = (
                ServiceRequest.query.filter(
                    ServiceRequest.customer_id == current_user.customer_profile.id,
                    ServiceRequest.status.in_(
                        [REQUEST_STATUS_CREATED, REQUEST_STATUS_ASSIGNED]
                    ),
                ).first()
                is not None
            )

        if has_active_requests:
            return APIResponse.error(
                "Cannot delete account while having active service requests",
                HTTPStatus.CONFLICT,
                "ActiveRequestsExist",
            )

        log = ActivityLog(
            user_id=None,  # Since user will be deleted
            action=ActivityLogActions.USER_DELETE,
            description=f"Account deleted for user {current_user.username} (role: {current_user.role})",
        )
        db.session.add(log)

        if current_user.role == USER_ROLE_PROFESSIONAL and verification_doc:
            delete_verification_document(verification_doc)

        db.session.delete(current_user)
        db.session.commit()

        return APIResponse.success(
            message="Account successfully deleted", status_code=HTTPStatus.OK
        )
    except Exception as e:
        return APIResponse.error(
            f"Error deleting account: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )
