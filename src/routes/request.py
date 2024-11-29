from flask import Blueprint, request
from marshmallow import ValidationError
from http import HTTPStatus
from datetime import datetime, timedelta

from src import db

from src.models import (
    ServiceRequest,
    CustomerProfile,
    ProfessionalProfile,
    Review,
    Service,
    ActivityLog,
)

from src.constants import (
    ActivityLogActions,
    REQUEST_STATUS_CREATED,
    REQUEST_STATUS_ASSIGNED,
    REQUEST_STATUS_COMPLETED,
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
from src.utils.request import check_booking_availability
from src.utils.notification import NotificationService, EmailTemplate

request_bp = Blueprint("request", __name__)


@request_bp.route("/requests", methods=["POST"])
@token_required
@role_required("customer")
def create_service_request(current_user):
    """Create a new service request"""
    try:
        data = service_request_input_schema.load(request.get_json())

        # Verify service exists and is active
        service = Service.query.get_or_404(data["service_id"])
        if not service.is_active:
            return APIResponse.error(
                "Selected service is not currently available",
                HTTPStatus.BAD_REQUEST,
                "InactiveService",
            )

        # Check if service can be completed by 6 PM
        service_end_time = data["preferred_time"] + timedelta(
            minutes=service.estimated_time
        )
        end_time_limit = datetime.combine(
            data["preferred_time"].date(), datetime.strptime("18:00", "%H:%M").time()
        )
        if service_end_time > end_time_limit:
            return APIResponse.error(
                "Service cannot be completed by 6 PM with the selected start time",
                HTTPStatus.BAD_REQUEST,
                "InvalidTimeSlot",
            )

        # Verify customer profile exists
        if not current_user.customer_profile:
            return APIResponse.error(
                "Customer profile not found", HTTPStatus.NOT_FOUND, "ProfileNotFound"
            )

        # Check if customer has any pending payments (if implementing payments)
        # if has_pending_payments(current_user.customer_profile.id):
        #     return APIResponse.error(
        #         "Cannot create new request with pending payments",
        #         HTTPStatus.FORBIDDEN,
        #         "PendingPayments"
        #     )

        # Create service request
        service_request = ServiceRequest(
            service_id=data["service_id"],
            customer_id=current_user.customer_profile.id,
            preferred_time=data["preferred_time"],
            description=data.get("description", ""),
            status=REQUEST_STATUS_CREATED,
            date_of_request=datetime.utcnow(),
        )

        db.session.add(service_request)
        db.session.flush()

        # Create activity log
        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.REQUEST_CREATE,
            entity_id=service_request.id,
            description=f"Created service request for {service.name}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(
            data=service_request_output_schema.dump(service_request),
            message="Service request created successfully",
            status_code=HTTPStatus.CREATED,
        )
    except ValidationError as err:
        return APIResponse.error(
            str(err.messages), HTTPStatus.BAD_REQUEST, "ValidationError"
        )
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(
            f"Error creating service request: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@request_bp.route("/customer/requests", methods=["GET"])
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
    """Cancel a service request by deleting it"""
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
                "Cannot access others requests",
                HTTPStatus.FORBIDDEN,
                "UnauthorizedAccess",
            )

        # Only allow cancellation of created or assigned requests
        if service_request.status not in [REQUEST_STATUS_CREATED]:
            return APIResponse.error(
                "Cannot cancel completed or assigned requests",
                HTTPStatus.BAD_REQUEST,
                "InvalidStatus",
            )

        # Create activity log before deletion
        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.REQUEST_CANCEL,
            entity_id=request_id,
            description=(f"Cancelled service request {request_id}"),
        )
        db.session.add(log)

        # Delete the service request
        db.session.delete(service_request)
        db.session.commit()

        return APIResponse.success(
            message="Service request cancelled successfully",
            data={},
        )
    except Exception as e:
        db.session.rollback()
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
                "Cannot access others requests",
                HTTPStatus.FORBIDDEN,
                "UnauthorizedAccess",
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


@request_bp.route("/professional/requests", methods=["GET"])
@token_required
@role_required("professional")
def list_professional_requests(current_user):
    """List service requests based on type (available/ongoing/completed/all)"""
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

        # Get query parameters
        request_type = request.args.get("type", "all").lower()
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        # Build base query
        if request_type == "available":
            # Available requests - matching service type and unassigned
            query = ServiceRequest.query.filter_by(
                service_id=professional.service_type_id, status=REQUEST_STATUS_CREATED
            ).order_by(ServiceRequest.preferred_time.asc())

        elif request_type == "ongoing":
            # Ongoing requests - assigned to this professional
            query = ServiceRequest.query.filter_by(
                professional_id=professional.id, status=REQUEST_STATUS_ASSIGNED
            ).order_by(ServiceRequest.date_of_assignment.desc())

        elif request_type == "completed":
            # Completed requests by this professional
            query = ServiceRequest.query.filter_by(
                professional_id=professional.id, status=REQUEST_STATUS_COMPLETED
            ).order_by(ServiceRequest.date_of_completion.desc())

        elif request_type == "all":
            # All requests - either available for their service type or assigned/completed by them
            query = ServiceRequest.query.filter(
                (
                    (ServiceRequest.service_id == professional.service_type_id)
                    & (ServiceRequest.status == REQUEST_STATUS_CREATED)
                )
                | (ServiceRequest.professional_id == professional.id)
            ).order_by(ServiceRequest.date_of_request.desc())

        else:
            return APIResponse.error(
                "Invalid request type. Must be one of: available, ongoing, completed, all",
                HTTPStatus.BAD_REQUEST,
                "InvalidRequestType",
            )

        # Apply pagination
        try:
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        except Exception as e:
            return APIResponse.error(
                f"Pagination error: {str(e)}", HTTPStatus.BAD_REQUEST, "PaginationError"
            )

        return APIResponse.success(
            data=service_requests_output_schema.dump(paginated.items),
            message=f"Requests retrieved successfully (type: {request_type})",
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

        # Get the service estimated time value
        service = Service.query.get(service_request.service_id)
        estimated_time = service.estimated_time if service else None

        if estimated_time is None:
            return APIResponse.error(
                "Invalid service configuration",
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "ServiceError",
            )

        # Check for booking availability using the integer value of estimated_time
        is_available, error_message = check_booking_availability(
            professional.id,
            service_request.preferred_time,
            estimated_time,  # Now passing the integer value
        )

        if not is_available:
            return APIResponse.error(
                error_message, HTTPStatus.CONFLICT, "BookingOverlap"
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

        NotificationService.send_service_request_notification(
            service_request,
            template=EmailTemplate.SERVICE_REQUEST_ASSIGNED,
            subject="Service Request Assigned",
        )

        return APIResponse.success(
            data=service_request_output_schema.dump(service_request),
            message="Service request accepted successfully",
        )
    except Exception as e:
        db.session.rollback()  # Added rollback in case of error
        return APIResponse.error(
            f"Error accepting request: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@request_bp.route("/requests/<int:request_id>/complete", methods=["POST"])
@token_required
@role_required("customer", "professional")
def complete_service(current_user, request_id):
    """Mark a service request as completed with permissions for both customer and professional"""
    try:
        # Get the service request
        service_request = ServiceRequest.query.get_or_404(request_id)

        # Verify authorization based on role
        if current_user.role == "customer":
            if (
                not current_user.customer_profile
                or service_request.customer_id != current_user.customer_profile.id
            ):
                return APIResponse.error(
                    "Cannot access others requests",
                    HTTPStatus.FORBIDDEN,
                    "UnauthorizedAccess",
                )
        else:  # Professional
            if (
                not current_user.professional_profile
                or service_request.professional_id
                != current_user.professional_profile.id
            ):
                return APIResponse.error(
                    "Cannot access others requests",
                    HTTPStatus.FORBIDDEN,
                    "UnauthorizedAccess",
                )

        # Validate request status
        if service_request.status != REQUEST_STATUS_ASSIGNED:
            return APIResponse.error(
                "Cannot complete already completed/unassigned service",
                HTTPStatus.BAD_REQUEST,
                "InvalidStatus",
            )

        # Check if enough time has passed based on estimated completion time
        estimated_completion_time = service_request.preferred_time + timedelta(
            minutes=service_request.service.estimated_time
        )
        current_time = datetime.utcnow()

        if current_time < estimated_completion_time:
            remaining_minutes = int(
                (estimated_completion_time - current_time).total_seconds() / 60
            )
            return APIResponse.error(
                f"Service cannot be completed yet. {remaining_minutes} minutes remaining based on estimated duration.",
                HTTPStatus.BAD_REQUEST,
                "EarlyCompletion",
            )

        # Validate request body
        data = request.get_json()
        if not data or not data.get("remarks"):
            return APIResponse.error(
                "Remarks are required for completion",
                HTTPStatus.BAD_REQUEST,
                "MissingRemarks",
            )

        # Update service request
        service_request.status = REQUEST_STATUS_COMPLETED
        service_request.date_of_completion = current_time
        service_request.remarks = data["remarks"]

        # Create activity log
        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.REQUEST_COMPLETE,
            entity_id=request_id,
            description=f"Service request {request_id} marked as completed by {current_user.role}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(
            data=service_request_output_schema.dump(service_request),
            message="Service marked as completed successfully",
        )
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(
            f"Error completing service: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@request_bp.route("/requests/<int:request_id>", methods=["PUT"])
@token_required
@role_required("customer")
def edit_service_request(current_user, request_id):
    """Edit an existing service request"""
    try:
        # Validate request body
        data = service_request_input_schema.load(request.get_json())

        # Verify customer profile and request
        customer_profile = CustomerProfile.query.filter_by(
            user_id=current_user.id
        ).first()
        if not customer_profile:
            return APIResponse.error(
                "Customer profile not found", HTTPStatus.NOT_FOUND, "ProfileNotFound"
            )

        service_request = ServiceRequest.query.get_or_404(request_id)

        # Check ownership
        if service_request.customer_id != customer_profile.id:
            return APIResponse.error(
                "Cannot access others requests",
                HTTPStatus.FORBIDDEN,
                "UnauthorizedAccess",
            )

        # Only allow editing of unassigned requests
        if service_request.status != REQUEST_STATUS_CREATED:
            return APIResponse.error(
                "Cannot edit requests that have been assigned or completed",
                HTTPStatus.BAD_REQUEST,
                "InvalidStatus",
            )

        # Verify service exists and is active
        service = Service.query.get_or_404(data["service_id"])
        if not service.is_active:
            return APIResponse.error(
                "Selected service is not currently available",
                HTTPStatus.BAD_REQUEST,
                "InactiveService",
            )

        # Check if service can be completed by 6 PM
        service_end_time = data["preferred_time"] + timedelta(
            minutes=service.estimated_time
        )
        end_time_limit = datetime.combine(
            data["preferred_time"].date(), datetime.strptime("18:00", "%H:%M").time()
        )
        if service_end_time > end_time_limit:
            return APIResponse.error(
                "Service cannot be completed by 6 PM with the selected start time",
                HTTPStatus.BAD_REQUEST,
                "InvalidTimeSlot",
            )

        # Update request fields
        service_request.service_id = data["service_id"]
        service_request.preferred_time = data["preferred_time"]
        service_request.description = data.get(
            "description", service_request.description
        )

        # Create activity log
        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.REQUEST_UPDATE,
            entity_id=request_id,
            description=f"Updated service request {request_id} details",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(
            data=service_request_output_schema.dump(service_request),
            message="Service request updated successfully",
        )
    except ValidationError as err:
        return APIResponse.error(
            str(err.messages), HTTPStatus.BAD_REQUEST, "ValidationError"
        )
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(
            f"Error updating service request: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )
