from flask import Blueprint, request, jsonify
from src.models import (
    ServiceRequest,
    CustomerProfile,
    ProfessionalProfile,
    Review,
    ActivityLog,
)
from src.schemas import service_request_schema, service_requests_schema, review_schema
from src.utils.auth import token_required, role_required, APIError
from src import db
from datetime import datetime

request_bp = Blueprint("request", __name__)


# Customer endpoints
@request_bp.route("/", methods=["POST"])
@token_required
@role_required("customer")
def create_service_request(current_user):
    """Create a new service request"""
    data = request.get_json()

    # Get customer profile
    customer_profile = CustomerProfile.query.filter_by(user_id=current_user.id).first()
    if not customer_profile:
        raise APIError("Customer profile not found", 404)

    # Prepare request data
    request_data = {
        "service_id": data.get("service_id"),
        "customer_id": customer_profile.id,
        "date_of_request": datetime.fromisoformat(data.get("date_of_request")),
        "preferred_time": data.get("preferred_time"),
        "address": data.get("address", customer_profile.address),
        "pin_code": data.get("pin_code", customer_profile.pin_code),
        "description": data.get("description"),
        "status": "requested",
    }

    errors = service_request_schema.validate(request_data)
    if errors:
        raise APIError(f"Validation error: {errors}", 400)

    service_request = ServiceRequest(**request_data)
    db.session.add(service_request)

    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="create_service_request",
        entity_type="service_request",
        entity_id=service_request.id,
        description=f"Created service request for service {service_request.service_id}",
    )
    db.session.add(log)

    db.session.commit()

    return jsonify(
        {
            "message": "Service request created successfully",
            "service_request": service_request_schema.dump(service_request),
        }
    ), 201


@request_bp.route("/my-requests", methods=["GET"])
@token_required
@role_required("customer")
def list_my_requests(current_user):
    """List all service requests for the current customer"""
    customer_profile = CustomerProfile.query.filter_by(user_id=current_user.id).first()
    if not customer_profile:
        raise APIError("Customer profile not found", 404)

    status = request.args.get("status")
    query = ServiceRequest.query.filter_by(customer_id=customer_profile.id)

    if status:
        query = query.filter_by(status=status)

    requests = query.order_by(ServiceRequest.date_of_request.desc()).all()
    return jsonify(service_requests_schema.dump(requests)), 200


@request_bp.route("/<int:request_id>/cancel", methods=["POST"])
@token_required
@role_required("customer")
def cancel_request(current_user, request_id):
    """Cancel a service request"""
    customer_profile = CustomerProfile.query.filter_by(user_id=current_user.id).first()
    service_request = ServiceRequest.query.get_or_404(request_id)

    if service_request.customer_id != customer_profile.id:
        raise APIError("Unauthorized access", 403)

    if service_request.status not in ["requested", "assigned"]:
        raise APIError("Cannot cancel request in current status", 400)

    service_request.status = "cancelled"

    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="cancel_service_request",
        entity_type="service_request",
        entity_id=request_id,
        description=f"Cancelled service request {request_id}",
    )
    db.session.add(log)

    db.session.commit()

    return jsonify({"message": "Service request cancelled successfully"}), 200


@request_bp.route("/<int:request_id>/review", methods=["POST"])
@token_required
@role_required("customer")
def submit_review(current_user, request_id):
    """Submit a review for a completed service request"""
    customer_profile = CustomerProfile.query.filter_by(user_id=current_user.id).first()
    service_request = ServiceRequest.query.get_or_404(request_id)

    if service_request.customer_id != customer_profile.id:
        raise APIError("Unauthorized access", 403)

    if service_request.status != "completed":
        raise APIError("Can only review completed services", 400)

    if Review.query.filter_by(service_request_id=request_id).first():
        raise APIError("Review already exists for this service request", 400)

    data = request.get_json()
    review_data = {
        "service_request_id": request_id,
        "rating": data.get("rating"),
        "comment": data.get("comment"),
    }

    errors = review_schema.validate(review_data)
    if errors:
        raise APIError(f"Validation error: {errors}", 400)

    review = Review(**review_data)
    db.session.add(review)

    # Update professional's average rating
    professional = service_request.professional
    all_reviews = (
        Review.query.join(ServiceRequest)
        .filter(ServiceRequest.professional_id == professional.id)
        .all()
    )
    total_ratings = sum(r.rating for r in all_reviews) + review.rating
    professional.average_rating = total_ratings / (len(all_reviews) + 1)

    # Mark request as closed
    service_request.status = "closed"

    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="submit_review",
        entity_type="review",
        entity_id=review.id,
        description=f"Submitted review for service request {request_id}",
    )
    db.session.add(log)

    db.session.commit()

    return jsonify(
        {
            "message": "Review submitted successfully",
            "review": review_schema.dump(review),
        }
    ), 201


# Professional endpoints
@request_bp.route("/available", methods=["GET"])
@token_required
@role_required("professional")
def list_available_requests(current_user):
    """List service requests available for assignment"""
    professional = ProfessionalProfile.query.filter_by(user_id=current_user.id).first()
    if not professional:
        raise APIError("Professional profile not found", 404)

    if not professional.is_verified:
        raise APIError("Account not verified yet", 403)

    requests = (
        ServiceRequest.query.filter_by(
            service_id=professional.service_type_id, status="requested"
        )
        .order_by(ServiceRequest.date_of_request.asc())
        .all()
    )

    return jsonify(service_requests_schema.dump(requests)), 200


@request_bp.route("/my-assignments", methods=["GET"])
@token_required
@role_required("professional")
def list_my_assignments(current_user):
    """List all assigned service requests for the professional"""
    professional = ProfessionalProfile.query.filter_by(user_id=current_user.id).first()
    if not professional:
        raise APIError("Professional profile not found", 404)

    status = request.args.get("status")
    query = ServiceRequest.query.filter_by(professional_id=professional.id)

    if status:
        query = query.filter_by(status=status)

    requests = query.order_by(ServiceRequest.date_of_request.desc()).all()
    return jsonify(service_requests_schema.dump(requests)), 200


@request_bp.route("/<int:request_id>/accept", methods=["POST"])
@token_required
@role_required("professional")
def accept_request(current_user, request_id):
    """Accept a service request"""
    professional = ProfessionalProfile.query.filter_by(user_id=current_user.id).first()
    if not professional or not professional.is_verified:
        raise APIError("Unauthorized or unverified professional", 403)

    service_request = ServiceRequest.query.get_or_404(request_id)

    if service_request.status != "requested":
        raise APIError("Request is not available for acceptance", 400)

    if service_request.service_id != professional.service_type_id:
        raise APIError("Service type mismatch", 400)

    service_request.professional_id = professional.id
    service_request.status = "assigned"
    service_request.date_of_assignment = datetime.utcnow()

    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="accept_service_request",
        entity_type="service_request",
        entity_id=request_id,
        description=f"Accepted service request {request_id}",
    )
    db.session.add(log)

    db.session.commit()

    return jsonify(
        {
            "message": "Service request accepted successfully",
            "service_request": service_request_schema.dump(service_request),
        }
    ), 200


@request_bp.route("/<int:request_id>/start", methods=["POST"])
@token_required
@role_required("professional")
def start_service(current_user, request_id):
    """Mark a service request as started"""
    professional = ProfessionalProfile.query.filter_by(user_id=current_user.id).first()
    service_request = ServiceRequest.query.get_or_404(request_id)

    if service_request.professional_id != professional.id:
        raise APIError("Unauthorized access", 403)

    if service_request.status != "assigned":
        raise APIError("Cannot start service in current status", 400)

    service_request.status = "in_progress"

    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="start_service",
        entity_type="service_request",
        entity_id=request_id,
        description=f"Started service for request {request_id}",
    )
    db.session.add(log)

    db.session.commit()

    return jsonify({"message": "Service started successfully"}), 200


@request_bp.route("/<int:request_id>/complete", methods=["POST"])
@token_required
@role_required("professional")
def complete_service(current_user, request_id):
    """Mark a service request as completed"""
    professional = ProfessionalProfile.query.filter_by(user_id=current_user.id).first()
    service_request = ServiceRequest.query.get_or_404(request_id)

    if service_request.professional_id != professional.id:
        raise APIError("Unauthorized access", 403)

    if service_request.status != "in_progress":
        raise APIError("Cannot complete service in current status", 400)

    service_request.status = "completed"
    service_request.date_of_completion = datetime.utcnow()
    service_request.remarks = request.json.get("remarks")

    # Log activity
    log = ActivityLog(
        user_id=current_user.id,
        action="complete_service",
        entity_type="service_request",
        entity_id=request_id,
        description=f"Completed service for request {request_id}",
    )
    db.session.add(log)

    db.session.commit()

    return jsonify({"message": "Service marked as completed successfully"}), 200
