from flask import Blueprint, request
from datetime import datetime
from marshmallow import ValidationError
from http import HTTPStatus

from src.models import (
    User,
    ProfessionalProfile,
    CustomerProfile,
    ServiceRequest,
    ActivityLog,
)
from src.constants import (
    USER_ROLE_CUSTOMER,
    USER_ROLE_PROFESSIONAL,
    ActivityLogActions,
    USER_ROLE_ADMIN,
)
from src.schemas import (
    login_schema,
    customer_register_schema,
    professional_register_schema,
    password_update_schema,
    token_schema,
    customer_output_schema,
    professional_output_schema,
    delete_account_schema,
    customer_profile_update_schema,
    professional_profile_update_schema,
    combine_professional_data,
)
from src.utils.auth import generate_token, token_required, APIResponse
from src.utils.file import save_verification_document, delete_verification_document
from src.utils.user import check_existing_user
from src import db

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

    try:
        user.last_login = datetime.utcnow()

        log = ActivityLog(
            user_id=user.id,
            action=ActivityLogActions.USER_LOGIN,
            description=f"User {user.username} logged in successfully",
        )
        db.session.add(log)
        db.session.commit()

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


@auth_bp.route("/register/customer", methods=["POST"])
def register_customer():
    """Register a new customer"""
    try:
        data = customer_register_schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(str(err.messages))

    exists, error_response = check_existing_user(data["username"], data["email"])
    if exists:
        return error_response

    try:
        user = User(
            username=data["username"],
            email=data["email"],
            full_name=data["full_name"],
            phone=data["phone"],
            address=data["address"],
            pin_code=data["pin_code"],
            role=USER_ROLE_CUSTOMER,
            is_active=True,
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.flush()

        profile = CustomerProfile(user_id=user.id)
        db.session.add(profile)

        log = ActivityLog(
            user_id=user.id,
            action=ActivityLogActions.USER_REGISTER,
            description=f"New customer account created for {user.username}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(
            data=customer_output_schema.dump(user),
            message="Customer registered successfully",
            status_code=HTTPStatus.CREATED,
        )
    except Exception as e:
        return APIResponse.error(
            f"Error creating customer: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@auth_bp.route("/register/professional", methods=["POST"])
def register_professional():
    """Register a new professional"""
    if "verification_document" not in request.files:
        return APIResponse.error(
            "Verification document is required",
            HTTPStatus.BAD_REQUEST,
            "MissingDocument",
        )

    try:
        form_data = {
            "username": request.form.get("username"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
            "full_name": request.form.get("full_name"),
            "phone": request.form.get("phone"),
            "address": request.form.get("address"),
            "pin_code": request.form.get("pin_code"),
            "service_type_id": int(request.form.get("service_type_id")),
            "experience_years": int(request.form.get("experience_years")),
            "description": request.form.get("description"),
        }
    except (TypeError, ValueError):
        return APIResponse.error(
            "Invalid service_type_id or experience_years",
            HTTPStatus.BAD_REQUEST,
            "ValidationError",
        )

    try:
        data = professional_register_schema.load(form_data)
    except ValidationError as err:
        return APIResponse.error(str(err.messages))

    exists, error_response = check_existing_user(data["username"], data["email"])
    if exists:
        return error_response

    filename, error = save_verification_document(request.files["verification_document"])
    if error:
        return APIResponse.error(error, HTTPStatus.BAD_REQUEST, "FileUploadError")

    try:
        user = User(
            username=data["username"],
            email=data["email"],
            full_name=data["full_name"],
            phone=data["phone"],
            address=data["address"],
            pin_code=data["pin_code"],
            role=USER_ROLE_PROFESSIONAL,
            is_active=False,
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.flush()

        profile = ProfessionalProfile(
            user_id=user.id,
            service_type_id=data["service_type_id"],
            experience_years=data["experience_years"],
            description=data["description"],
            verification_documents=filename,
            is_verified=False,
        )
        db.session.add(profile)

        log = ActivityLog(
            user_id=user.id,
            action=ActivityLogActions.USER_REGISTER,
            description=f"New professional account created for {user.username}, pending verification",
        )
        db.session.add(log)
        db.session.commit()

        response_data = combine_professional_data(user, profile)

        return APIResponse.success(
            data=response_data,
            message="Professional registered successfully. Account will be activated after verification.",
            status_code=HTTPStatus.CREATED,
        )
    except Exception as e:
        if filename:
            delete_verification_document(filename)
        return APIResponse.error(
            f"Error creating professional: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@auth_bp.route("/profile", methods=["GET"])
@token_required
def get_profile(current_user):
    """Get current user's profile"""
    try:
        if current_user.role == USER_ROLE_PROFESSIONAL:
            schema = professional_output_schema
            message = "Professional profile retrieved successfully"
        else:
            schema = customer_output_schema
            message = f"{current_user.role.capitalize()} profile retrieved successfully"

        return APIResponse.success(data=schema.dump(current_user), message=message)
    except Exception as e:
        return APIResponse.error(
            f"Error retrieving profile: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@auth_bp.route("/change-password", methods=["POST"])
@token_required
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


@auth_bp.route("/profile", methods=["PUT"])
@token_required
def update_profile(current_user):
    """Update user's profile information"""
    try:
        schema = (
            professional_profile_update_schema
            if current_user.role == USER_ROLE_PROFESSIONAL
            else customer_profile_update_schema
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


@auth_bp.route("/delete-account", methods=["DELETE"])
@token_required
def delete_account(current_user):
    """Hard delete user account"""
    try:
        if current_user.role == USER_ROLE_ADMIN:
            return APIResponse.error(
                "Admin accounts cannot be deleted",
                HTTPStatus.UNAUTHORIZED,
                "DeletionError",
            )
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
                    ServiceRequest.status.in_(["assigned", "in_progress"]),
                ).first()
                is not None
            )
            verification_doc = current_user.professional_profile.verification_documents
        else:
            has_active_requests = (
                ServiceRequest.query.filter(
                    ServiceRequest.customer_id == current_user.customer_profile.id,
                    ServiceRequest.status.in_(["requested", "assigned", "in_progress"]),
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
