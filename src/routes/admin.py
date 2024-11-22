from flask import Blueprint, request, jsonify
from src.models import (
    User,
    ProfessionalProfile,
    CustomerProfile,
    ServiceRequest,
    Review,
    ActivityLog,
)
from src.schemas import (
    professional_profiles_schema,
    professional_profile_schema,
    customer_profiles_schema,
    service_requests_schema,
    reviews_schema,
)
from src.utils.auth import token_required, role_required, APIError
from src import db
from datetime import datetime

admin_bp = Blueprint("admin", __name__)


# Professional management
@admin_bp.route("/professionals", methods=["GET"])
@token_required
@role_required("admin")
def list_professionals(current_user):
    """List all professionals with optional filters"""
    is_verified = request.args.get("verified", type=lambda v: v.lower() == "true")
    service_type = request.args.get("service_type", type=int)

    query = ProfessionalProfile.query

    if is_verified is not None:
        query = query.filter_by(is_verified=is_verified)
    if service_type:
        query = query.filter_by(service_type_id=service_type)

    professionals = query.all()
    return jsonify(professional_profiles_schema.dump(professionals)), 200


@admin_bp.route("/professionals/<int:profile_id>/verify", methods=["POST"])
@token_required
@role_required("admin")
def verify_professional(current_user, profile_id):
    """Verify a professional's profile"""
    profile = ProfessionalProfile.query.get_or_404(profile_id)

    if profile.is_verified:
        raise APIError("Professional is already verified", 400)

    profile.is_verified = True
    profile.user.is_active = True

    # Log the activity
    log = ActivityLog(
        user_id=current_user.id,
        action="verify_professional",
        entity_type="professional_profile",
        entity_id=profile_id,
        description=f"Verified professional profile for {profile.full_name}",
    )

    db.session.add(log)
    db.session.commit()

    return jsonify(
        {
            "message": "Professional verified successfully",
            "profile": professional_profile_schema.dump(profile),
        }
    ), 200


@admin_bp.route("/professionals/<int:profile_id>/block", methods=["POST"])
@token_required
@role_required("admin")
def block_professional(current_user, profile_id):
    """Block a professional's account"""
    profile = ProfessionalProfile.query.get_or_404(profile_id)
    reason = request.json.get("reason")

    if not reason:
        raise APIError("Block reason is required", 400)

    profile.user.is_active = False

    # Log the activity
    log = ActivityLog(
        user_id=current_user.id,
        action="block_professional",
        entity_type="professional_profile",
        entity_id=profile_id,
        description=f"Blocked professional {profile.full_name}. Reason: {reason}",
    )

    db.session.add(log)
    db.session.commit()

    return jsonify({"message": "Professional blocked successfully"}), 200


# Customer management
@admin_bp.route("/customers", methods=["GET"])
@token_required
@role_required("admin")
def list_customers(current_user):
    """List all customers with optional filters"""
    is_active = request.args.get("active", type=lambda v: v.lower() == "true")
    pin_code = request.args.get("pin_code")

    query = CustomerProfile.query

    if is_active is not None:
        query = query.join(User).filter(User.is_active == is_active)
    if pin_code:
        query = query.filter_by(pin_code=pin_code)

    customers = query.all()
    return jsonify(customer_profiles_schema.dump(customers)), 200


@admin_bp.route("/customers/<int:profile_id>/block", methods=["POST"])
@token_required
@role_required("admin")
def block_customer(current_user, profile_id):
    """Block a customer's account"""
    profile = CustomerProfile.query.get_or_404(profile_id)
    reason = request.json.get("reason")

    if not reason:
        raise APIError("Block reason is required", 400)

    profile.user.is_active = False

    # Log the activity
    log = ActivityLog(
        user_id=current_user.id,
        action="block_customer",
        entity_type="customer_profile",
        entity_id=profile_id,
        description=f"Blocked customer {profile.full_name}. Reason: {reason}",
    )

    db.session.add(log)
    db.session.commit()

    return jsonify({"message": "Customer blocked successfully"}), 200


# Review management
@admin_bp.route("/reviews/reported", methods=["GET"])
@token_required
@role_required("admin")
def list_reported_reviews(current_user):
    """List all reported reviews"""
    reviews = Review.query.filter_by(is_reported=True).all()
    return jsonify(reviews_schema.dump(reviews)), 200


@admin_bp.route("/reviews/<int:review_id>/handle-report", methods=["POST"])
@token_required
@role_required("admin")
def handle_review_report(current_user, review_id):
    """Handle a reported review"""
    review = Review.query.get_or_404(review_id)
    action = request.json.get("action")  # 'dismiss' or 'remove'

    if action not in ["dismiss", "remove"]:
        raise APIError("Invalid action specified", 400)

    if action == "dismiss":
        review.is_reported = False
        message = "Review report dismissed"
    else:  # remove
        db.session.delete(review)
        message = "Review removed"

    # Log the activity
    log = ActivityLog(
        user_id=current_user.id,
        action=f"review_{action}",
        entity_type="review",
        entity_id=review_id,
        description=f"{message} for service request {review.service_request_id}",
    )

    db.session.add(log)
    db.session.commit()

    return jsonify({"message": message}), 200


# Dashboard statistics
@admin_bp.route("/dashboard/stats", methods=["GET"])
@token_required
@role_required("admin")
def get_dashboard_stats(current_user):
    """Get statistics for admin dashboard"""
    stats = {
        "total_professionals": ProfessionalProfile.query.count(),
        "verified_professionals": ProfessionalProfile.query.filter_by(
            is_verified=True
        ).count(),
        "total_customers": CustomerProfile.query.count(),
        "active_customers": CustomerProfile.query.join(User)
        .filter(User.is_active == True)
        .count(),
        "pending_verifications": ProfessionalProfile.query.filter_by(
            is_verified=False
        ).count(),
        "reported_reviews": Review.query.filter_by(is_reported=True).count(),
        "service_requests": {
            "total": ServiceRequest.query.count(),
            "pending": ServiceRequest.query.filter_by(status="requested").count(),
            "in_progress": ServiceRequest.query.filter_by(status="in_progress").count(),
            "completed": ServiceRequest.query.filter_by(status="completed").count(),
        },
    }

    return jsonify(stats), 200
