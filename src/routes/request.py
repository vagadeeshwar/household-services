from flask import Blueprint, request
from marshmallow import ValidationError
from http import HTTPStatus
from datetime import datetime

from src import db

from src.models import (
    ServiceRequest,
    CustomerProfile,
    ProfessionalProfile,
    Review,
    ActivityLog,
)

from src.constants import (
    ActivityLogActions,
    REQUEST_STATUS_CREATED,
    REQUEST_STATUS_ASSIGNED,
    REQUEST_STATUS_COMPLETED,
    REQUEST_STATUS_IN_PROGRESS,
)

from src.schemas.request import (
    service_request_input_schema,
    service_request_output_schema,
    service_requests_output_schema,
    review_output_schema,
    ReviewInputSchema,
)

from src.utils.auth import token_required, role_required
from src.utils.api import APIResponse

request_bp = Blueprint("request", __name__)


@request_bp.route("/requests", methods=["POST"])
@token_required
@role_required("customer")
def create_service_request(current_user):
    """Create a new service request"""
    try:
        data = service_request_input_schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(str(err.messages))

    try:
        # Get customer profile
        customer_profile = CustomerProfile.query.filter_by(
            user_id=current_user.id
        ).first()
        if not customer_profile:
            return APIResponse.error(
                "Customer profile not found", HTTPStatus.NOT_FOUND, "ProfileNotFound"
            )

        # Create service request
        service_request = ServiceRequest(
            service_id=data["service_id"],
            customer_id=customer_profile.id,
            date_of_request=datetime.utcnow(),
            preferred_time=data.get("preferred_time"),
            description=data.get("description"),
            status=REQUEST_STATUS_CREATED,
        )
        db.session.add(service_request)
        db.session.flush()

        # Log activity
        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.REQUEST_CREATE,
            entity_id=service_request.id,
            description=f"Created service request for service {service_request.service_id}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(
            data=service_request_output_schema.dump(service_request),
            message="Service request created successfully",
            status_code=HTTPStatus.CREATED,
        )
    except Exception as e:
        return APIResponse.error(
            f"Error creating service request: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@request_bp.route("/requests/customer", methods=["GET"])
@token_required
@role_required("customer")
def list_customer_requests(current_user):
    """List all service requests for the current customer"""
    try:
        customer_profile = CustomerProfile.query.filter_by(
            user_id=current_user.id
        ).first()
        if not customer_profile:
            return APIResponse.error(
                "Customer profile not found", HTTPStatus.NOT_FOUND, "ProfileNotFound"
            )

        # Get query parameters
        status = request.args.get("status")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        # Build query
        query = ServiceRequest.query.filter_by(customer_id=customer_profile.id)
        if status:
            query = query.filter_by(status=status)

        # Apply pagination
        try:
            paginated = query.order_by(ServiceRequest.date_of_request.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
        except Exception as e:
            return APIResponse.error(
                f"Pagination error: {str(e)}", HTTPStatus.BAD_REQUEST, "PaginationError"
            )

        return APIResponse.success(
            data=service_requests_output_schema.dump(paginated.items),
            message="Requests retrieved successfully",
            pagination={
                "total": paginated.total,
                "pages": paginated.pages,
                "current_page": paginated.page,
                "per_page": paginated.per_page,
                "has_next": paginated.has_next,
                "has_prev": paginated.has_prev,
            },
        )
    except Exception as e:
        return APIResponse.error(
            f"Error retrieving requests: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@request_bp.route("/requests/<int:request_id>/cancel", methods=["POST"])
@token_required
@role_required("customer")
def cancel_request(current_user, request_id):
    """Cancel a service request"""
    try:
        customer_profile = CustomerProfile.query.filter_by(
            user_id=current_user.id
        ).first()
        if not customer_profile:
            return APIResponse.error(
                "Customer profile not found", HTTPStatus.NOT_FOUND, "ProfileNotFound"
            )

        service_request = ServiceRequest.query.get_or_404(request_id)

        if service_request.customer_id != customer_profile.id:
            return APIResponse.error(
                "Unauthorized access", HTTPStatus.FORBIDDEN, "UnauthorizedAccess"
            )

        if service_request.status not in [
            REQUEST_STATUS_CREATED,
            REQUEST_STATUS_ASSIGNED,
        ]:
            return APIResponse.error(
                "Cannot cancel request in current status",
                HTTPStatus.BAD_REQUEST,
                "InvalidStatus",
            )

        service_request.status = "cancelled"

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.REQUEST_CANCEL,
            entity_id=request_id,
            description=f"Cancelled service request {request_id}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(message="Service request cancelled successfully")
    except Exception as e:
        return APIResponse.error(
            f"Error cancelling request: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@request_bp.route("/requests/<int:request_id>/review", methods=["POST"])
@token_required
@role_required("customer")
def submit_review(current_user, request_id):
    """Submit a review for a completed service request"""
    try:
        data = ReviewInputSchema().load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(str(err.messages))

    try:
        customer_profile = CustomerProfile.query.filter_by(
            user_id=current_user.id
        ).first()
        if not customer_profile:
            return APIResponse.error(
                "Customer profile not found", HTTPStatus.NOT_FOUND, "ProfileNotFound"
            )

        service_request = ServiceRequest.query.get_or_404(request_id)

        if service_request.customer_id != customer_profile.id:
            return APIResponse.error(
                "Unauthorized access", HTTPStatus.FORBIDDEN, "UnauthorizedAccess"
            )

        if service_request.status != REQUEST_STATUS_COMPLETED:
            return APIResponse.error(
                "Can only review completed services",
                HTTPStatus.BAD_REQUEST,
                "InvalidStatus",
            )

        if Review.query.filter_by(service_request_id=request_id).first():
            return APIResponse.error(
                "Review already exists for this service request",
                HTTPStatus.CONFLICT,
                "DuplicateReview",
            )

        review = Review(
            service_request_id=request_id,
            rating=data["rating"],
            comment=data.get("comment"),
        )
        db.session.add(review)

        # Update professional's average rating
        professional = service_request.professional
        reviews = (
            Review.query.join(ServiceRequest)
            .filter(ServiceRequest.professional_id == professional.id)
            .all()
        )
        total_ratings = sum(r.rating for r in reviews) + review.rating
        professional.average_rating = round(total_ratings / (len(reviews) + 1), 1)

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.REVIEW_SUBMIT,
            entity_id=review.id,
            description=f"Submitted review for service request {request_id}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(
            data=review_output_schema.dump(review),
            message="Review submitted successfully",
            status_code=HTTPStatus.CREATED,
        )
    except Exception as e:
        return APIResponse.error(
            f"Error submitting review: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


# Professional endpoints
@request_bp.route("/requests/available", methods=["GET"])
@token_required
@role_required("professional")
def list_available_requests(current_user):
    """List service requests available for assignment"""
    try:
        professional = ProfessionalProfile.query.filter_by(
            user_id=current_user.id
        ).first()
        if not professional:
            return APIResponse.error(
                "Professional profile not found",
                HTTPStatus.NOT_FOUND,
                "ProfileNotFound",
            )

        if not professional.is_verified:
            return APIResponse.error(
                "Account not verified yet", HTTPStatus.FORBIDDEN, "UnverifiedAccount"
            )

        # Get pagination parameters
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        # Build query
        query = ServiceRequest.query.filter_by(
            service_id=professional.service_type_id,
            status=REQUEST_STATUS_CREATED,
        ).order_by(ServiceRequest.date_of_request.asc())

        # Apply pagination
        try:
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        except Exception as e:
            return APIResponse.error(
                f"Pagination error: {str(e)}", HTTPStatus.BAD_REQUEST, "PaginationError"
            )

        return APIResponse.success(
            data=service_requests_output_schema.dump(paginated.items),
            message="Available requests retrieved successfully",
            pagination={
                "total": paginated.total,
                "pages": paginated.pages,
                "current_page": paginated.page,
                "per_page": paginated.per_page,
                "has_next": paginated.has_next,
                "has_prev": paginated.has_prev,
            },
        )
    except Exception as e:
        return APIResponse.error(
            f"Error retrieving available requests: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@request_bp.route("/requests/professional", methods=["GET"])
@token_required
@role_required("professional")
def list_professional_assignments(current_user):
    """List all assigned service requests for the professional"""
    try:
        professional = ProfessionalProfile.query.filter_by(
            user_id=current_user.id
        ).first()
        if not professional:
            return APIResponse.error(
                "Professional profile not found",
                HTTPStatus.NOT_FOUND,
                "ProfileNotFound",
            )

        # Get query parameters
        status = request.args.get("status")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        # Build query
        query = ServiceRequest.query.filter_by(professional_id=professional.id)
        if status:
            query = query.filter_by(status=status)

        # Apply pagination
        try:
            paginated = query.order_by(ServiceRequest.date_of_request.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
        except Exception as e:
            return APIResponse.error(
                f"Pagination error: {str(e)}", HTTPStatus.BAD_REQUEST, "PaginationError"
            )

        return APIResponse.success(
            data=service_requests_output_schema.dump(paginated.items),
            message="Assignments retrieved successfully",
            pagination={
                "total": paginated.total,
                "pages": paginated.pages,
                "current_page": paginated.page,
                "per_page": paginated.per_page,
                "has_next": paginated.has_next,
                "has_prev": paginated.has_prev,
            },
        )
    except Exception as e:
        return APIResponse.error(
            f"Error retrieving assignments: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@request_bp.route("/requests/<int:request_id>/accept", methods=["POST"])
@token_required
@role_required("professional")
def accept_request(current_user, request_id):
    """Accept a service request"""
    try:
        professional = ProfessionalProfile.query.filter_by(
            user_id=current_user.id
        ).first()
        if not professional:
            return APIResponse.error(
                "Professional profile not found",
                HTTPStatus.NOT_FOUND,
                "ProfileNotFound",
            )

        if not professional.is_verified:
            return APIResponse.error(
                "Account not verified yet", HTTPStatus.FORBIDDEN, "UnverifiedAccount"
            )

        service_request = ServiceRequest.query.get_or_404(request_id)

        if service_request.status != REQUEST_STATUS_CREATED:
            return APIResponse.error(
                "Request is not available for acceptance",
                HTTPStatus.BAD_REQUEST,
                "InvalidStatus",
            )

        if service_request.service_id != professional.service_type_id:
            return APIResponse.error(
                "Service type mismatch", HTTPStatus.BAD_REQUEST, "ServiceMismatch"
            )

        service_request.professional_id = professional.id
        service_request.status = REQUEST_STATUS_ASSIGNED
        service_request.date_of_assignment = datetime.utcnow()

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.REQUEST_ASSIGN,
            entity_id=request_id,
            description=f"Accepted service request {request_id}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(
            data=service_request_output_schema.dump(service_request),
            message="Service request accepted successfully",
        )
    except Exception as e:
        return APIResponse.error(
            f"Error accepting request: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@request_bp.route("/requests/<int:request_id>/start", methods=["POST"])
@token_required
@role_required("professional")
def start_service(current_user, request_id):
    """Mark a service request as started"""
    try:
        professional = ProfessionalProfile.query.filter_by(
            user_id=current_user.id
        ).first()
        if not professional:
            return APIResponse.error(
                "Professional profile not found",
                HTTPStatus.NOT_FOUND,
                "ProfileNotFound",
            )

        service_request = ServiceRequest.query.get_or_404(request_id)

        if service_request.professional_id != professional.id:
            return APIResponse.error(
                "Unauthorized access", HTTPStatus.FORBIDDEN, "UnauthorizedAccess"
            )

        if service_request.status != REQUEST_STATUS_ASSIGNED:
            return APIResponse.error(
                "Cannot start service in current status",
                HTTPStatus.BAD_REQUEST,
                "InvalidStatus",
            )

        service_request.status = "in_progress"

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.REQUEST_START,
            entity_id=request_id,
            description=f"Started service for request {request_id}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(
            data=service_request_output_schema.dump(service_request),
            message="Service started successfully",
        )
    except Exception as e:
        return APIResponse.error(
            f"Error starting service: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@request_bp.route("/requests/<int:request_id>/complete", methods=["POST"])
@token_required
@role_required("professional")
def complete_service(current_user, request_id):
    """Mark a service request as completed"""
    try:
        professional = ProfessionalProfile.query.filter_by(
            user_id=current_user.id
        ).first()
        if not professional:
            return APIResponse.error(
                "Professional profile not found",
                HTTPStatus.NOT_FOUND,
                "ProfileNotFound",
            )

        service_request = ServiceRequest.query.get_or_404(request_id)

        if service_request.professional_id != professional.id:
            return APIResponse.error(
                "Unauthorized access", HTTPStatus.FORBIDDEN, "UnauthorizedAccess"
            )

        if service_request.status != "in_progress":
            return APIResponse.error(
                "Cannot complete service in current status",
                HTTPStatus.BAD_REQUEST,
                "InvalidStatus",
            )

        remarks = request.get_json().get("remarks")
        if not remarks:
            return APIResponse.error(
                "Remarks are required for completion",
                HTTPStatus.BAD_REQUEST,
                "MissingRemarks",
            )

        service_request.status = REQUEST_STATUS_COMPLETED
        service_request.date_of_completion = datetime.utcnow()
        service_request.remarks = remarks

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.REQUEST_COMPLETE,
            entity_id=request_id,
            description=f"Completed service for request {request_id}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(
            data=service_request_output_schema.dump(service_request),
            message="Service marked as completed successfully",
        )
    except Exception as e:
        return APIResponse.error(
            f"Error completing service: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )
