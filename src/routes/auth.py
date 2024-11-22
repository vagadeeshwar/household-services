from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from datetime import datetime
from src.models import User, ProfessionalProfile, CustomerProfile
from src.schemas import (
    user_schema,
    professional_profile_schema,
    customer_profile_schema,
)
from src.utils.auth import generate_token, token_required, role_required, APIError
from src import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login route for all user types"""
    data = request.get_json()

    if not data or not data.get("username") or not data.get("password"):
        raise APIError("Missing username or password", 400)

    user = User.query.filter_by(username=data["username"]).first()

    if not user or not user.check_password(data["password"]):
        raise APIError("Invalid credentials", 401)

    if not user.is_active:
        raise APIError("Account is deactivated", 403)

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Generate token
    token = generate_token(user.id, user.role)

    return jsonify({"token": token, "user": user_schema.dump(user)}), 200


@auth_bp.route("/register/customer", methods=["POST"])
def register_customer():
    """Register a new customer"""
    data = request.get_json()

    # Validate and create user
    user_data = {
        "username": data.get("username"),
        "email": data.get("email"),
        "password": data.get("password"),
        "role": "customer",
    }

    errors = user_schema.validate(user_data)
    if errors:
        raise APIError(f"Validation error: {errors}", 400)

    # Check if username or email already exists
    if User.query.filter_by(username=user_data["username"]).first():
        raise APIError("Username already exists", 400)
    if User.query.filter_by(email=user_data["email"]).first():
        raise APIError("Email already exists", 400)

    # Create user
    user = User(**user_data)
    user.set_password(user_data["password"])
    db.session.add(user)
    db.session.flush()  # Get user.id without committing

    # Create customer profile
    profile_data = {
        "user_id": user.id,
        "full_name": data.get("full_name"),
        "phone": data.get("phone"),
        "address": data.get("address"),
        "pin_code": data.get("pin_code"),
    }

    errors = customer_profile_schema.validate(profile_data)
    if errors:
        db.session.rollback()
        raise APIError(f"Validation error: {errors}", 400)

    profile = CustomerProfile(**profile_data)
    db.session.add(profile)
    db.session.commit()

    return jsonify(
        {
            "message": "Customer registered successfully",
            "user": user_schema.dump(user),
            "profile": customer_profile_schema.dump(profile),
        }
    ), 201


@auth_bp.route("/register/professional", methods=["POST"])
def register_professional():
    """Register a new service professional"""
    data = request.get_json()

    # Validate and create user
    user_data = {
        "username": data.get("username"),
        "email": data.get("email"),
        "password": data.get("password"),
        "role": "professional",
    }

    errors = user_schema.validate(user_data)
    if errors:
        raise APIError(f"Validation error: {errors}", 400)

    # Check if username or email already exists
    if User.query.filter_by(username=user_data["username"]).first():
        raise APIError("Username already exists", 400)
    if User.query.filter_by(email=user_data["email"]).first():
        raise APIError("Email already exists", 400)

    # Create user
    user = User(**user_data)
    user.set_password(user_data["password"])
    db.session.add(user)
    db.session.flush()  # Get user.id without committing

    # Create professional profile
    profile_data = {
        "user_id": user.id,
        "full_name": data.get("full_name"),
        "phone": data.get("phone"),
        "experience_years": data.get("experience_years"),
        "description": data.get("description"),
        "service_type_id": data.get("service_type_id"),
        "verification_documents": data.get("verification_documents"),
    }

    errors = professional_profile_schema.validate(profile_data)
    if errors:
        db.session.rollback()
        raise APIError(f"Validation error: {errors}", 400)

    profile = ProfessionalProfile(**profile_data)
    db.session.add(profile)
    db.session.commit()

    return jsonify(
        {
            "message": "Professional registered successfully. Account will be activated after verification.",
            "user": user_schema.dump(user),
            "profile": professional_profile_schema.dump(profile),
        }
    ), 201


@auth_bp.route("/profile", methods=["GET"])
@token_required
def get_profile(current_user):
    """Get current user's profile"""
    if current_user.role == "professional":
        profile = ProfessionalProfile.query.filter_by(user_id=current_user.id).first()
        return jsonify(
            {
                "user": user_schema.dump(current_user),
                "profile": professional_profile_schema.dump(profile),
            }
        ), 200
    elif current_user.role == "customer":
        profile = CustomerProfile.query.filter_by(user_id=current_user.id).first()
        return jsonify(
            {
                "user": user_schema.dump(current_user),
                "profile": customer_profile_schema.dump(profile),
            }
        ), 200
    else:  # admin
        return jsonify({"user": user_schema.dump(current_user)}), 200


@auth_bp.route("/profile", methods=["PUT"])
@token_required
def update_profile(current_user):
    """Update current user's profile"""
    data = request.get_json()

    # Update user fields
    user_fields = ["email"]
    user_updates = {k: v for k, v in data.items() if k in user_fields}

    if user_updates:
        errors = user_schema.validate(user_updates, partial=True)
        if errors:
            raise APIError(f"Validation error: {errors}", 400)

        for key, value in user_updates.items():
            setattr(current_user, key, value)

    # Update profile fields
    if current_user.role == "professional":
        profile = ProfessionalProfile.query.filter_by(user_id=current_user.id).first()
        profile_fields = ["full_name", "phone", "experience_years", "description"]
        schema = professional_profile_schema
    else:  # customer
        profile = CustomerProfile.query.filter_by(user_id=current_user.id).first()
        profile_fields = ["full_name", "phone", "address", "pin_code"]
        schema = customer_profile_schema

    profile_updates = {k: v for k, v in data.items() if k in profile_fields}

    if profile_updates:
        errors = schema.validate(profile_updates, partial=True)
        if errors:
            raise APIError(f"Validation error: {errors}", 400)

        for key, value in profile_updates.items():
            setattr(profile, key, value)

    db.session.commit()

    return jsonify(
        {
            "message": "Profile updated successfully",
            "user": user_schema.dump(current_user),
        }
    ), 200


@auth_bp.route("/change-password", methods=["POST"])
@token_required
def change_password(current_user):
    """Change user's password"""
    data = request.get_json()

    if not data or not data.get("old_password") or not data.get("new_password"):
        raise APIError("Missing required fields", 400)

    if not current_user.check_password(data["old_password"]):
        raise APIError("Current password is incorrect", 400)

    current_user.set_password(data["new_password"])
    db.session.commit()

    return jsonify({"message": "Password changed successfully"}), 200
