from flask import Blueprint, request
from datetime import datetime
from src.models import (
    User,
    ProfessionalProfile,
    CustomerProfile,
    USER_ROLE_CUSTOMER,
    USER_ROLE_PROFESSIONAL,
)
from src.schemas import (
    login_input_schema,
    customer_register_input_schema,
    professional_register_input_schema,
    password_update_input_schema,
    token_output_schema,
    error_output_schema,
    customer_output_schema,
    professional_output_schema,
)
from src.utils.auth import generate_token, token_required
from marshmallow import ValidationError
from src import db
from http import HTTPStatus

auth_bp = Blueprint("auth", __name__)


def create_error_response(
    message, status_code=HTTPStatus.BAD_REQUEST, error_type="ValidationError"
):
    return error_output_schema.dump(
        {
            "status": "failure",
            "status_code": status_code,
            "detail": message,
            "error_type": error_type,
        }
    ), status_code


def create_success_response(data, message=None, status_code=HTTPStatus.OK):
    response = {"status": "success", "status_code": status_code, "data": data}
    if message:
        response["detail"] = message
    return response, status_code


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login route for all user types"""
    try:
        # Validate input data
        data = login_input_schema.load(request.get_json())
    except ValidationError as err:
        return create_error_response(str(err.messages))

    # Check user exists
    user = User.query.filter_by(username=data["username"]).first()
    if not user or not user.check_password(data["password"]):
        return create_error_response(
            "Invalid credentials", HTTPStatus.UNAUTHORIZED, "InvalidCredentials"
        )

    if not user.is_active:
        return create_error_response(
            "Account is deactivated", HTTPStatus.FORBIDDEN, "InactiveAccount"
        )

    # Update last login and generate token
    user.last_login = datetime.utcnow()
    db.session.commit()

    token = generate_token(user.id, user.role)
    return create_success_response(
        token_output_schema.dump({"token": token}), "Login successful"
    )


@auth_bp.route("/register/customer", methods=["POST"])
def register_customer():
    """Register a new customer"""
    try:
        # Validate input data
        data = customer_register_input_schema.load(request.get_json())
    except ValidationError as err:
        return create_error_response(str(err.messages))

    # Check for existing username/email
    if User.query.filter_by(username=data["username"]).first():
        return create_error_response(
            "Username already exists", HTTPStatus.CONFLICT, "DuplicateUsername"
        )

    if User.query.filter_by(email=data["email"]).first():
        return create_error_response(
            "Email already exists", HTTPStatus.CONFLICT, "DuplicateEmail"
        )

    try:
        # Create user
        user = User(
            username=data["username"],
            email=data["email"],
            full_name=data["full_name"],
            phone=data["phone"],
            address=data["address"],
            pin_code=data["pin_code"],
            role=USER_ROLE_CUSTOMER,
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.flush()

        # Create customer profile
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
    try:
        # Validate input data
        data = professional_register_input_schema.load(request.get_json())
    except ValidationError as err:
        return create_error_response(str(err.messages))

    # Check for existing username/email
    if User.query.filter_by(username=data["username"]).first():
        return create_error_response(
            "Username already exists", HTTPStatus.CONFLICT, "DuplicateUsername"
        )

    if User.query.filter_by(email=data["email"]).first():
        return create_error_response(
            "Email already exists", HTTPStatus.CONFLICT, "DuplicateEmail"
        )

    try:
        # Create user
        user = User(
            username=data["username"],
            email=data["email"],
            full_name=data["full_name"],
            phone=data["phone"],
            address=data["address"],
            pin_code=data["pin_code"],
            role=USER_ROLE_PROFESSIONAL,
            is_active=False,  # Professional needs verification
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.flush()

        # Create professional profile
        profile = ProfessionalProfile(
            user_id=user.id,
            service_type_id=data["service_type_id"],
            experience_years=data["experience_years"],
            description=data["description"],
            verification_documents=data.get("verification_documents"),
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
            return create_success_response(
                professional_output_schema.dump(current_user),
                "Professional profile retrieved successfully",
            )
        elif current_user.role == USER_ROLE_CUSTOMER:
            return create_success_response(
                customer_output_schema.dump(current_user),
                "Customer profile retrieved successfully",
            )
        else:  # admin
            return create_success_response(
                customer_output_schema.dump(current_user),
                "Admin profile retrieved successfully",
            )
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
        data = password_update_input_schema.load(request.get_json())
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
