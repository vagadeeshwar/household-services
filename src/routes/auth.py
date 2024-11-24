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
    user_schema,
    professional_profile_schema,
    customer_profile_schema,
)
from src.utils.auth import generate_token, token_required, APIResponse
from src import db
from http import HTTPStatus

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login route for all user types"""
    data = request.get_json()

    if not data or not data.get("username") or not data.get("password"):
        return APIResponse.error(
            message="Missing username or password",
            status_code=HTTPStatus.BAD_REQUEST,
            error_type="ValidationError",
        )

    user = User.query.filter_by(username=data["username"]).first()

    if not user or not user.check_password(data["password"]):
        return APIResponse.error(
            message="Invalid credentials",
            status_code=HTTPStatus.UNAUTHORIZED,
            error_type="InvalidCredentials",
        )

    if not user.is_active:
        return APIResponse.error(
            message="Account is deactivated",
            status_code=HTTPStatus.FORBIDDEN,
            error_type="InactiveAccount",
        )

    user.last_login = datetime.utcnow()
    db.session.commit()

    token = generate_token(user.id, user.role.value)

    return APIResponse.success(
        data={"token": token, "user": user_schema.dump(user)},
        message="Login successful",
        status_code=HTTPStatus.OK,
    )


@auth_bp.route("/register/customer", methods=["POST"])
def register_customer():
    """Register a new customer with flattened data structure"""
    data = request.get_json()

    try:
        # Separate password from user data
        password = data.pop("password")

        # All data comes in a single object
        userData = {
            "username": data["username"],
            "email": data["email"],
            "full_name": data.get("full_name", data["username"]),
            "phone": data["phone"],
            "address": data["address"],
            "pin_code": data["pin_code"],
            "role": USER_ROLE_CUSTOMER,
        }
    except KeyError as e:
        return APIResponse.error(
            message=f"Missing required field: {str(e)}",
            status_code=HTTPStatus.BAD_REQUEST,
            error_type="MissingField",
        )

    errors = user_schema.validate(userData)
    if errors:
        return APIResponse.error(
            message=f"Validation error: {errors}",
            status_code=HTTPStatus.BAD_REQUEST,
            error_type="ValidationError",
        )

    if User.query.filter_by(username=userData["username"]).first():
        return APIResponse.error(
            message="Username already exists",
            status_code=HTTPStatus.CONFLICT,
            error_type="DuplicateUsername",
        )

    if User.query.filter_by(email=userData["email"]).first():
        return APIResponse.error(
            message="Email already exists",
            status_code=HTTPStatus.CONFLICT,
            error_type="DuplicateEmail",
        )

    # Create user and profile in a transaction
    user = User(**userData)
    user.set_password(password)  # Set password using the method
    db.session.add(user)
    db.session.flush()  # Flush to get user.id

    profile = CustomerProfile(user_id=user.id)
    db.session.add(profile)
    db.session.commit()

    # Query to get joined data for response
    customer_data = (
        db.session.query(CustomerProfile)
        .join(User)
        .filter(CustomerProfile.id == profile.id)
        .first()
    )

    return APIResponse.success(
        data=customer_profile_schema.dump(customer_data),
        message="Customer registered successfully",
        status_code=HTTPStatus.CREATED,
    )


@auth_bp.route("/register/professional", methods=["POST"])
def register_professional():
    """Register a new professional with flattened data structure"""
    data = request.get_json()

    try:
        # Separate password from user data
        password = data.pop("password")

        # All data comes in a single object
        userData = {
            "username": data["username"],
            "email": data["email"],
            "full_name": data.get("full_name", data["username"]),
            "phone": data["phone"],
            "address": data["address"],
            "pin_code": data["pin_code"],
            "role": USER_ROLE_PROFESSIONAL,
            # Professional specific fields are kept separate
            "description": data["description"],
            "service_type_id": data["service_type_id"],
            "experience_years": data["experience_years"],
            "verification_documents": data.get("verification_documents"),
        }
    except KeyError as e:
        return APIResponse.error(
            message=f"Missing required field: {str(e)}",
            status_code=HTTPStatus.BAD_REQUEST,
            error_type="MissingField",
        )

    # Validate user fields
    user_fields = {
        k: userData[k]
        for k in [
            "username",
            "email",
            "full_name",
            "phone",
            "address",
            "pin_code",
            "role",
        ]
    }

    errors = user_schema.validate(user_fields)
    if errors:
        return APIResponse.error(
            message=f"Validation error: {errors}",
            status_code=HTTPStatus.BAD_REQUEST,
            error_type="ValidationError",
        )

    if User.query.filter_by(username=userData["username"]).first():
        return APIResponse.error(
            message="Username already exists",
            status_code=HTTPStatus.CONFLICT,
            error_type="DuplicateUsername",
        )

    if User.query.filter_by(email=userData["email"]).first():
        return APIResponse.error(
            message="Email already exists",
            status_code=HTTPStatus.CONFLICT,
            error_type="DuplicateEmail",
        )

    # Create user and profile in a transaction
    user = User(**user_fields)
    user.set_password(password)  # Set password using the method
    user.is_active = False  # Professional needs verification
    db.session.add(user)
    db.session.flush()  # Flush to get user.id

    profile_data = {
        "user_id": user.id,
        "description": userData["description"],
        "service_type_id": userData["service_type_id"],
        "experience_years": userData["experience_years"],
        "verification_documents": userData.get("verification_documents"),
        "is_verified": False,
    }

    errors = professional_profile_schema.validate(profile_data)
    if errors:
        db.session.rollback()
        return APIResponse.error(
            message=f"Validation error in professional profile: {errors}",
            status_code=HTTPStatus.BAD_REQUEST,
            error_type="ValidationError",
        )

    profile = ProfessionalProfile(**profile_data)
    db.session.add(profile)
    db.session.commit()

    # Query to get joined data for response
    professional_data = (
        db.session.query(ProfessionalProfile)
        .join(User)
        .filter(ProfessionalProfile.id == profile.id)
        .first()
    )

    return APIResponse.success(
        data=professional_profile_schema.dump(professional_data),
        message="Professional registered successfully. Account will be activated after verification.",
        status_code=HTTPStatus.CREATED,
    )


@auth_bp.route("/profile", methods=["GET"])
@token_required
def get_profile(current_user):
    """Get current user's complete profile"""
    if current_user.role == USER_ROLE_PROFESSIONAL:
        profile = (
            db.session.query(ProfessionalProfile)
            .join(User)
            .filter(ProfessionalProfile.user_id == current_user.id)
            .first()
        )
        return APIResponse.success(
            data=professional_profile_schema.dump(profile),
            message="Professional profile retrieved successfully",
        )
    elif current_user.role == USER_ROLE_CUSTOMER:
        profile = (
            db.session.query(CustomerProfile)
            .join(User)
            .filter(CustomerProfile.user_id == current_user.id)
            .first()
        )
        return APIResponse.success(
            data=customer_profile_schema.dump(profile),
            message="Customer profile retrieved successfully",
        )
    else:  # admin
        return APIResponse.success(
            data=user_schema.dump(current_user),
            message="Admin profile retrieved successfully",
        )


@auth_bp.route("/profile", methods=["PUT"])
@token_required
def update_profile(current_user):
    """Update current user's profile"""
    data = request.get_json()
    if not data:
        return APIResponse.error(
            message="No update data provided",
            status_code=HTTPStatus.BAD_REQUEST,
            error_type="MissingData",
        )

    user_fields = ["email", "full_name", "phone", "address", "pin_code"]
    user_updates = {k: v for k, v in data.items() if k in user_fields}

    if user_updates:
        errors = user_schema.validate(user_updates, partial=True)
        if errors:
            return APIResponse.error(
                message=f"Validation error: {errors}",
                status_code=HTTPStatus.BAD_REQUEST,
                error_type="ValidationError",
            )

        for key, value in user_updates.items():
            setattr(current_user, key, value)

    if current_user.role == USER_ROLE_PROFESSIONAL:
        profile = ProfessionalProfile.query.filter_by(user_id=current_user.id).first()
        profile_fields = ["experience_years", "description"]
        schema = professional_profile_schema
    else:
        profile = CustomerProfile.query.filter_by(user_id=current_user.id).first()
        profile_fields = []
        schema = customer_profile_schema

    profile_updates = {k: v for k, v in data.items() if k in profile_fields}

    if profile_updates:
        errors = schema.validate(profile_updates, partial=True)
        if errors:
            return APIResponse.error(
                message=f"Validation error: {errors}",
                status_code=HTTPStatus.BAD_REQUEST,
                error_type="ValidationError",
            )

        for key, value in profile_updates.items():
            setattr(profile, key, value)

    db.session.commit()

    return APIResponse.success(
        data={"user": user_schema.dump(current_user)},
        message="Profile updated successfully",
    )


@auth_bp.route("/change-password", methods=["POST"])
@token_required
def change_password(current_user):
    """Change user's password"""
    data = request.get_json()

    if not data or not data.get("old_password") or not data.get("new_password"):
        return APIResponse.error(
            message="Missing required fields",
            status_code=HTTPStatus.BAD_REQUEST,
            error_type="MissingFields",
        )

    if not current_user.check_password(data["old_password"]):
        return APIResponse.error(
            message="Current password is incorrect",
            status_code=HTTPStatus.UNAUTHORIZED,
            error_type="InvalidPassword",
        )

    current_user.set_password(data["new_password"])
    db.session.commit()

    return APIResponse.success(message="Password changed successfully")
