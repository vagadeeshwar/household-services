from flask import Blueprint, request
from datetime import datetime
from src.models import (
    User,
    ProfessionalProfile,
    CustomerProfile,
    USER_ROLE_CUSTOMER,
    USER_ROLE_PROFESSIONAL,
    ServiceRequest,
)
from src.schemas import (
    login_schema,
    customer_register_schema,
    professional_register_schema,
    password_update_schema,
    token_schema,
    error_schema,
    customer_output_schema,
    professional_output_schema,
    delete_account_schema,
    customer_profile_update_schema,
    professional_profile_update_schema,
)
from src.utils.auth import generate_token, token_required
from src.utils.file import save_verification_document, delete_verification_document
from marshmallow import ValidationError
from src import db
from http import HTTPStatus

auth_bp = Blueprint("auth", __name__)


def create_error_response(
    message: str,
    status_code: int = HTTPStatus.BAD_REQUEST,
    error_type: str = "ValidationError",
) -> tuple:
    return error_schema.dump(
        {
            "status": "failure",
            "status_code": status_code,
            "detail": message,
            "error_type": error_type,
        }
    ), status_code


def create_success_response(
    data: dict = None, message: str = None, status_code: int = HTTPStatus.OK
) -> tuple:
    response = {"status": "success", "status_code": status_code, "data": data}
    if message:
        response["detail"] = message
    return response, status_code


def check_existing_user(username: str, email: str) -> tuple[bool, tuple]:
    """Check if username or email already exists"""
    if User.query.filter_by(username=username).first():
        return True, create_error_response(
            "Username already exists", HTTPStatus.CONFLICT, "DuplicateUsername"
        )

    if User.query.filter_by(email=email).first():
        return True, create_error_response(
            "Email already exists", HTTPStatus.CONFLICT, "DuplicateEmail"
        )

    return False, None


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login route for all user types"""
    try:
        data = login_schema.load(request.get_json())
    except ValidationError as err:
        return create_error_response(str(err.messages))

    user = User.query.filter_by(username=data["username"]).first()

    if not user or not user.check_password(data["password"]):
        return create_error_response(
            "Invalid credentials", HTTPStatus.UNAUTHORIZED, "InvalidCredentials"
        )

    if not user.is_active:
        return create_error_response(
            "Account is deactivated", HTTPStatus.FORBIDDEN, "InactiveAccount"
        )

    try:
        user.last_login = datetime.utcnow()
        db.session.commit()

        token = generate_token(user.id, user.role)
        return create_success_response(
            token_schema.dump({"token": token}), "Login successful"
        )
    except Exception as e:
        db.session.rollback()
        return create_error_response(
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
        return create_error_response(str(err.messages))

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
        db.session.commit()

        return create_success_response(
            customer_output_schema.dump(user),
            "Customer registered successfully",
            HTTPStatus.CREATED,
        )
    except Exception as e:
        db.session.rollback()
        return create_error_response(
            f"Error creating customer: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@auth_bp.route("/register/professional", methods=["POST"])
def register_professional():
    """Register a new professional"""
    if "verification_document" not in request.files:
        return create_error_response(
            "Verification document is required",
            HTTPStatus.BAD_REQUEST,
            "MissingDocument",
        )

    try:
        # Parse and validate form data
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
        return create_error_response(
            "Invalid service_type_id or experience_years",
            HTTPStatus.BAD_REQUEST,
            "ValidationError",
        )

    try:
        data = professional_register_schema.load(form_data)
    except ValidationError as err:
        return create_error_response(str(err.messages))

    exists, error_response = check_existing_user(data["username"], data["email"])
    if exists:
        return error_response

    filename, error = save_verification_document(request.files["verification_document"])
    if error:
        return create_error_response(error, HTTPStatus.BAD_REQUEST, "FileUploadError")

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
        db.session.commit()

        return create_success_response(
            professional_output_schema.dump(user),
            "Professional registered successfully. Account will be activated after verification.",
            HTTPStatus.CREATED,
        )
    except Exception as e:
        if filename:
            delete_verification_document(filename)
        db.session.rollback()
        return create_error_response(
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

        return create_success_response(schema.dump(current_user), message)
    except Exception as e:
        return create_error_response(
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
        return create_error_response(str(err.messages))

    if not current_user.check_password(data["old_password"]):
        return create_error_response(
            "Current password is incorrect", HTTPStatus.UNAUTHORIZED, "InvalidPassword"
        )

    try:
        current_user.set_password(data["new_password"])
        db.session.commit()
        return create_success_response(None, "Password changed successfully")
    except Exception as e:
        db.session.rollback()
        return create_error_response(
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
        return create_error_response(str(err.messages))

    try:
        if "email" in data and data["email"] != current_user.email:
            if User.query.filter_by(email=data["email"]).first():
                return create_error_response(
                    "Email already in use", HTTPStatus.CONFLICT, "DuplicateEmail"
                )
            current_user.email = data["email"]

        for field in ["full_name", "phone", "address", "pin_code"]:
            if field in data:
                setattr(current_user, field, data[field])

        if current_user.role == USER_ROLE_PROFESSIONAL and "description" in data:
            current_user.professional_profile.description = data["description"]

        db.session.commit()

        schema = (
            professional_output_schema
            if current_user.role == USER_ROLE_PROFESSIONAL
            else customer_output_schema
        )
        return create_success_response(
            schema.dump(current_user), "Profile updated successfully"
        )
    except Exception as e:
        db.session.rollback()
        return create_error_response(
            f"Error updating profile: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@auth_bp.route("/delete-account", methods=["DELETE"])
@token_required
def delete_account(current_user):
    """Hard delete user account"""
    try:
        data = delete_account_schema.load(request.get_json())
    except ValidationError as err:
        return create_error_response(str(err.messages))

    if not current_user.check_password(data["password"]):
        return create_error_response(
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

            # Store verification document filename for later deletion
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
            return create_error_response(
                "Cannot delete account while having active service requests",
                HTTPStatus.CONFLICT,
                "ActiveRequestsExist",
            )

        # Delete verification document if professional
        if current_user.role == USER_ROLE_PROFESSIONAL and verification_doc:
            delete_verification_document(verification_doc)

        db.session.delete(current_user)
        db.session.commit()

        return create_success_response(
            None, "Account successfully deleted", HTTPStatus.OK
        )
    except Exception as e:
        db.session.rollback()
        return create_error_response(
            f"Error deleting account: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )
