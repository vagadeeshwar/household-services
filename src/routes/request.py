from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from flask import Blueprint, request
from marshmallow import ValidationError

from src import db
from src.constants import (
    REQUEST_STATUS_ASSIGNED,
    REQUEST_STATUS_COMPLETED,
    REQUEST_STATUS_CREATED,
    REQUEST_STATUSES,
    ActivityLogActions,
)
from src.models import (
    ActivityLog,
    CustomerProfile,
    ProfessionalProfile,
    Review,
    Service,
    ServiceRequest,
)
from src.schemas.request import (
    calendar_view_schema,
    customer_requests_output_schema,
    professional_requests_output_schema,
    report_review_schema,
    review_input_schema,
    review_output_schema,
    service_request_input_schema,
    service_request_output_schema,
)
from src.utils.api import APIResponse
from src.utils.auth import role_required, token_required
from src.utils.cache import cache_, cache_invalidate
from src.utils.notification import EmailTemplate, NotificationService
from src.utils.request import check_booking_availability, get_professional_schedule

request_bp = Blueprint("request", __name__)


@request_bp.route("/requests", methods=["POST"])
@token_required
@role_required("customer")
def create_service_request(current_user):
    """Create a new service request"""
    try:
        # Get the request JSON data
        request_data = request.get_json()

        # Validate request body without context parameter
        data = service_request_input_schema.load(request_data)

        # Verify service exists and is active
        service = Service.query.get(data["service_id"])
        if not service or not service.is_active:
            return APIResponse.error(
                "Selected service wasn't found or is not currently available",
                HTTPStatus.BAD_REQUEST,
                "InactiveService",
            )

        # Ensure preferred_time is timezone-aware
        preferred_time = data["preferred_time"]
        if preferred_time.tzinfo is None:
            # Convert to timezone-aware datetime if it's naive
            preferred_time = preferred_time.replace(tzinfo=timezone.utc)

        # Check if service can be completed by 6 PM
        service_end_time = preferred_time + timedelta(minutes=service.estimated_time)

        # Create a timezone-aware end time limit
        end_time_date = preferred_time.date()
        end_time_limit = datetime.combine(
            end_time_date,
            datetime.strptime("18:00", "%H:%M").time(),
            tzinfo=timezone.utc,
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
        # Create service request
        service_request = ServiceRequest(
            service_id=data["service_id"],
            customer_id=current_user.customer_profile.id,
            preferred_time=preferred_time,
            description=data.get("description", ""),
            status=REQUEST_STATUS_CREATED,
            date_of_request=datetime.now(timezone.utc),
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
        cache_invalidate()
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


@request_bp.route("/requests/<int:request_id>", methods=["PUT"])
@token_required
@role_required("customer")
def edit_service_request(current_user, request_id):
    """Edit an existing service request"""
    try:
        # Get the request JSON data
        request_data = request.get_json()

        # Validate request body WITH context parameter to ensure proper validation
        data = service_request_input_schema.load(request_data)

        # Verify customer profile and request
        customer_profile = CustomerProfile.query.filter_by(
            user_id=current_user.id
        ).first()

        if not customer_profile:
            return APIResponse.error(
                "Customer profile not found", HTTPStatus.NOT_FOUND, "ProfileNotFound"
            )

        service_request = ServiceRequest.query.get(request_id)
        if not service_request:
            return APIResponse.error(
                f"Service request with ID {request_id} not found",
                HTTPStatus.NOT_FOUND,
                "RequestNotFound",
            )

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
        service = Service.query.get(data["service_id"])
        if not service or not service.is_active:
            return APIResponse.error(
                "Selected service wasn't found or is not currently available",
                HTTPStatus.BAD_REQUEST,
                "InactiveService",
            )

        # Ensure preferred_time is timezone-aware
        preferred_time = data["preferred_time"]
        if preferred_time.tzinfo is None:
            # Convert to timezone-aware datetime if it's naive
            preferred_time = preferred_time.replace(tzinfo=timezone.utc)

        # Check if service can be completed by 6 PM
        service_end_time = preferred_time + timedelta(minutes=service.estimated_time)

        # Create a timezone-aware end time limit - ensure consistent timezone handling
        end_time_date = preferred_time.date()
        end_time_hour = datetime.strptime("18:00", "%H:%M").time()
        end_time_limit = datetime.combine(end_time_date, end_time_hour)

        # Ensure end_time_limit is timezone-aware
        if end_time_limit.tzinfo is None:
            end_time_limit = end_time_limit.replace(tzinfo=timezone.utc)

        if service_end_time > end_time_limit:
            return APIResponse.error(
                "Service cannot be completed by 6 PM with the selected start time",
                HTTPStatus.BAD_REQUEST,
                "InvalidTimeSlot",
            )

        # Update request fields
        service_request.service_id = data["service_id"]
        service_request.preferred_time = preferred_time
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
        cache_invalidate()

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
        service_request = ServiceRequest.query.get(request_id)
        if not service_request:
            return APIResponse.error(
                f"Service request with ID {request_id} not found",
                HTTPStatus.NOT_FOUND,
                "RequestNotFound",
            )

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
        service_request.date_of_assignment = datetime.now(timezone.utc)
        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.REQUEST_ASSIGN,
            entity_id=request_id,
            description=f"Accepted service request {request_id}",
        )
        db.session.add(log)
        db.session.commit()
        cache_invalidate()
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
        service_request = ServiceRequest.query.get(request_id)

        if not service_request:
            return APIResponse.error(
                f"Service request with ID {request_id} not found",
                HTTPStatus.NOT_FOUND,
                "RequestNotFound",
            )

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

        # preferred_time = service_request.preferred_time
        # if preferred_time.tzinfo is None:
        #     # Add UTC timezone information
        #     preferred_time = preferred_time.replace(tzinfo=timezone.utc)

        # # Calculate estimated completion time using the timezone-aware preferred_time
        # estimated_completion_time = preferred_time + timedelta(
        #     minutes=service_request.service.estimated_time
        # )
        current_time = datetime.now(timezone.utc)

        # if current_time < estimated_completion_time:
        #     remaining_minutes = int(
        #         (estimated_completion_time - current_time).total_seconds() / 60
        #     )
        #     return APIResponse.error(
        #         f"Service cannot be completed yet. {remaining_minutes} minutes remaining based on estimated duration.",
        #         HTTPStatus.BAD_REQUEST,
        #         "EarlyCompletion",
        #     )
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
        cache_invalidate()
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
        service_request = ServiceRequest.query.get(request_id)
        if not service_request:
            return APIResponse.error(
                f"Service request with ID {request_id} not found",
                HTTPStatus.NOT_FOUND,
                "RequestNotFound",
            )

        if service_request.customer_id != customer_profile.id:
            return APIResponse.error(
                "Cannot access others requests",
                HTTPStatus.FORBIDDEN,
                "UnauthorizedAccess",
            )
        # Only allow cancellation of created requests
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
        cache_invalidate()
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
        data = review_input_schema.load(request.get_json())
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
        service_request = ServiceRequest.query.get(request_id)
        if not service_request:
            return APIResponse.error(
                f"Service request with ID {request_id} not found",
                HTTPStatus.NOT_FOUND,
                "RequestNotFound",
            )

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
        cache_invalidate()
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


@request_bp.route("/customers/requests", methods=["GET"])
@token_required
@role_required("customer")
@cache_(timeout=120)
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
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        summary = request.args.get("summary", "false").lower() == "true"

        # Build query
        query = ServiceRequest.query.filter_by(customer_id=customer_profile.id)

        if status:
            query = query.filter_by(status=status)

        # Apply date filters
        if start_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(ServiceRequest.date_of_request >= start_date)
            except ValueError:
                return APIResponse.error(
                    "Invalid start_date format. Use YYYY-MM-DD",
                    HTTPStatus.BAD_REQUEST,
                    "InvalidDateFormat",
                )

        if end_date:
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
                # Include the entire end date
                end_date = end_date.replace(hour=23, minute=59, second=59)
                query = query.filter(ServiceRequest.date_of_request <= end_date)
            except ValueError:
                return APIResponse.error(
                    "Invalid end_date format. Use YYYY-MM-DD",
                    HTTPStatus.BAD_REQUEST,
                    "InvalidDateFormat",
                )

        # Apply pagination
        try:
            paginated = query.order_by(ServiceRequest.date_of_request.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
        except Exception as e:
            return APIResponse.error(
                f"Pagination error: {str(e)}", HTTPStatus.BAD_REQUEST, "PaginationError"
            )

        # Convert request items to serialized data
        serialized_requests = customer_requests_output_schema.dump(paginated.items)

        # Get summary counts if requested
        if summary:
            # Count total requests
            total_requests = ServiceRequest.query.filter_by(
                customer_id=customer_profile.id
            ).count()
            # Count active requests
            active_requests = ServiceRequest.query.filter(
                ServiceRequest.customer_id == customer_profile.id,
                ServiceRequest.status.in_(
                    [REQUEST_STATUS_CREATED, REQUEST_STATUS_ASSIGNED]
                ),
            ).count()
            # Count completed requests
            completed_requests = ServiceRequest.query.filter(
                ServiceRequest.customer_id == customer_profile.id,
                ServiceRequest.status == REQUEST_STATUS_COMPLETED,
            ).count()

            # Prepare summary data
            summary_data = {
                "requests": serialized_requests,
                "total_requests": total_requests,
                "active_requests": active_requests,
                "completed_requests": completed_requests,
            }

            return APIResponse.success(
                data=summary_data,
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
        else:
            # Return just the requests without summary
            return APIResponse.success(
                data=serialized_requests,
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


@request_bp.route("/professionals/requests", methods=["GET"])
@token_required
@role_required("professional")
@cache_(timeout=120)
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
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        summary = request.args.get("summary", "false").lower() == "true"

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

        # Apply date filters
        if start_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(ServiceRequest.date_of_request >= start_date)
            except ValueError:
                return APIResponse.error(
                    "Invalid start_date format. Use YYYY-MM-DD",
                    HTTPStatus.BAD_REQUEST,
                    "InvalidDateFormat",
                )

        if end_date:
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
                # Include the entire end date
                end_date = end_date.replace(hour=23, minute=59, second=59)
                query = query.filter(ServiceRequest.date_of_request <= end_date)
            except ValueError:
                return APIResponse.error(
                    "Invalid end_date format. Use YYYY-MM-DD",
                    HTTPStatus.BAD_REQUEST,
                    "InvalidDateFormat",
                )

        # Apply pagination
        try:
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        except Exception as e:
            return APIResponse.error(
                f"Pagination error: {str(e)}", HTTPStatus.BAD_REQUEST, "PaginationError"
            )

        # Convert request items to serialized data
        serialized_requests = professional_requests_output_schema.dump(paginated.items)

        # Get summary counts if requested
        if summary:
            # Total requests count for this professional
            total_requests = ServiceRequest.query.filter(
                (
                    (ServiceRequest.service_id == professional.service_type_id)
                    & (ServiceRequest.status == REQUEST_STATUS_CREATED)
                )
                | (ServiceRequest.professional_id == professional.id)
            ).count()
            # Active requests count (assigned to this professional)
            active_requests = ServiceRequest.query.filter(
                ServiceRequest.professional_id == professional.id,
                ServiceRequest.status == REQUEST_STATUS_ASSIGNED,
            ).count()
            # Completed requests count
            completed_requests = ServiceRequest.query.filter(
                ServiceRequest.professional_id == professional.id,
                ServiceRequest.status == REQUEST_STATUS_COMPLETED,
            ).count()

            # Prepare summary data
            summary_data = {
                "requests": serialized_requests,
                "total_requests": total_requests,
                "active_requests": active_requests,
                "completed_requests": completed_requests,
            }

            return APIResponse.success(
                data=summary_data,
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
        else:
            # Return just the requests without summary
            return APIResponse.success(
                data=serialized_requests,
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


@request_bp.route("/customers/<int:customer_id>/requests", methods=["GET"])
@token_required
@role_required("admin")
@cache_(timeout=120)
def admin_list_customer_requests(current_user, customer_id):
    """List all service requests for a specific customer (Admin only)"""
    try:
        # Check if customer exists
        customer_profile = CustomerProfile.query.get(customer_id)

        if not customer_profile:
            return APIResponse.error(
                "Customer not found", HTTPStatus.NOT_FOUND, "CustomerNotFound"
            )

        # Get query parameters
        status = request.args.get("status")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        summary = request.args.get("summary", "false").lower() == "true"
        # Build query
        query = ServiceRequest.query.filter_by(customer_id=customer_id)
        # Apply status filter
        if status and status in REQUEST_STATUSES:
            query = query.filter_by(status=status)
        # Apply date filters
        if start_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(ServiceRequest.date_of_request >= start_date)
            except ValueError:
                return APIResponse.error(
                    "Invalid start_date format. Use YYYY-MM-DD",
                    HTTPStatus.BAD_REQUEST,
                    "InvalidDateFormat",
                )
        if end_date:
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
                # Include the entire end date
                end_date = end_date.replace(hour=23, minute=59, second=59)
                query = query.filter(ServiceRequest.date_of_request <= end_date)
            except ValueError:
                return APIResponse.error(
                    "Invalid end_date format. Use YYYY-MM-DD",
                    HTTPStatus.BAD_REQUEST,
                    "InvalidDateFormat",
                )
        # Apply pagination
        try:
            paginated = query.order_by(ServiceRequest.date_of_request.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
        except Exception as e:
            return APIResponse.error(
                f"Pagination error: {str(e)}", HTTPStatus.BAD_REQUEST, "PaginationError"
            )

        # Convert request items to serialized data
        serialized_requests = customer_requests_output_schema.dump(paginated.items)

        # Get summary counts if requested
        if summary:
            # Count total requests
            total_requests = ServiceRequest.query.filter_by(
                customer_id=customer_id
            ).count()
            # Count active requests
            active_requests = ServiceRequest.query.filter(
                ServiceRequest.customer_id == customer_id,
                ServiceRequest.status.in_(
                    [REQUEST_STATUS_CREATED, REQUEST_STATUS_ASSIGNED]
                ),
            ).count()
            # Count completed requests
            completed_requests = ServiceRequest.query.filter(
                ServiceRequest.customer_id == customer_id,
                ServiceRequest.status == REQUEST_STATUS_COMPLETED,
            ).count()

            # Prepare summary data
            summary_data = {
                "requests": serialized_requests,
                "total_requests": total_requests,
                "active_requests": active_requests,
                "completed_requests": completed_requests,
            }

            return APIResponse.success(
                data=summary_data,
                message=f"Customer requests retrieved successfully (customer_id: {customer_id})",
                pagination={
                    "total": paginated.total,
                    "pages": paginated.pages,
                    "current_page": paginated.page,
                    "per_page": paginated.per_page,
                    "has_next": paginated.has_next,
                    "has_prev": paginated.has_prev,
                },
            )
        else:
            # Return just the requests without summary
            return APIResponse.success(
                data=serialized_requests,
                message=f"Customer requests retrieved successfully (customer_id: {customer_id})",
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
            f"Error retrieving customer requests: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@request_bp.route("/professionals/<int:professional_id>/requests", methods=["GET"])
@token_required
@role_required("admin")
@cache_(timeout=120)
def admin_list_professional_requests(current_user, professional_id):
    """List all service requests assigned to a specific professional (Admin only)"""
    try:
        # Check if professional exists
        professional_profile = ProfessionalProfile.query.get(professional_id)
        if not professional_profile:
            return APIResponse.error(
                "Professional not found", HTTPStatus.NOT_FOUND, "ProfessionalNotFound"
            )
        # Get query parameters
        status = request.args.get("status")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        summary = request.args.get("summary", "false").lower() == "true"

        # Build query - include both assigned and available requests for this professional's service type
        professional = ProfessionalProfile.query.get(professional_id)
        service_type_id = professional.service_type_id

        # This is the key fix: include both assigned requests AND available requests of the professional's service type
        query = ServiceRequest.query.filter(
            (
                ServiceRequest.professional_id == professional_id
            )  # Assigned to this professional
            | (
                (ServiceRequest.service_id == service_type_id)  # Matches service type
                & (
                    ServiceRequest.status == REQUEST_STATUS_CREATED
                )  # Is available/unassigned
            )
        )

        # Apply status filter if specified
        if status and status in REQUEST_STATUSES:
            query = query.filter_by(status=status)

        # Apply date filters
        if start_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(ServiceRequest.date_of_request >= start_date)
            except ValueError:
                return APIResponse.error(
                    "Invalid start_date format. Use YYYY-MM-DD",
                    HTTPStatus.BAD_REQUEST,
                    "InvalidDateFormat",
                )
        if end_date:
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
                # Include the entire end date
                end_date = end_date.replace(hour=23, minute=59, second=59)
                query = query.filter(ServiceRequest.date_of_request <= end_date)
            except ValueError:
                return APIResponse.error(
                    "Invalid end_date format. Use YYYY-MM-DD",
                    HTTPStatus.BAD_REQUEST,
                    "InvalidDateFormat",
                )

        # Apply pagination
        try:
            paginated = query.order_by(ServiceRequest.date_of_request.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
        except Exception as e:
            return APIResponse.error(
                f"Pagination error: {str(e)}", HTTPStatus.BAD_REQUEST, "PaginationError"
            )

        # Convert request items to serialized data
        serialized_requests = professional_requests_output_schema.dump(paginated.items)

        # Get summary counts if requested
        if summary:
            # Total requests count for this professional (assigned + available matching service type)
            total_requests_query = ServiceRequest.query.filter(
                (ServiceRequest.professional_id == professional_id)
                | (
                    (ServiceRequest.service_id == service_type_id)
                    & (ServiceRequest.status == REQUEST_STATUS_CREATED)
                )
            )
            total_requests = total_requests_query.count()

            # Active requests count (assigned to this professional)
            active_requests = ServiceRequest.query.filter(
                ServiceRequest.professional_id == professional_id,
                ServiceRequest.status == REQUEST_STATUS_ASSIGNED,
            ).count()

            # Completed requests count
            completed_requests = ServiceRequest.query.filter(
                ServiceRequest.professional_id == professional_id,
                ServiceRequest.status == REQUEST_STATUS_COMPLETED,
            ).count()

            # Prepare summary data
            summary_data = {
                "requests": serialized_requests,
                "total_requests": total_requests,
                "active_requests": active_requests,
                "completed_requests": completed_requests,
            }

            return APIResponse.success(
                data=summary_data,
                message=f"Professional requests retrieved successfully (professional_id: {professional_id})",
                pagination={
                    "total": paginated.total,
                    "pages": paginated.pages,
                    "current_page": paginated.page,
                    "per_page": paginated.per_page,
                    "has_next": paginated.has_next,
                    "has_prev": paginated.has_prev,
                },
            )
        else:
            # Return just the requests without summary
            return APIResponse.success(
                data=serialized_requests,
                message=f"Professional requests retrieved successfully (professional_id: {professional_id})",
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
            f"Error retrieving professional requests: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@request_bp.route("/professionals/<int:professional_id>/schedule", methods=["GET"])
@token_required
def get_schedule(current_user, professional_id):
    """Get professional's availability schedule"""
    try:
        # Verify professional exists
        professional_profile = ProfessionalProfile.query.get(professional_id)

        if not professional_profile:
            return APIResponse.error(
                "Professional not found", HTTPStatus.NOT_FOUND, "ProfessionalNotFound"
            )

        # Get query parameters
        start_date_str = request.args.get(
            "start_date", datetime.now().strftime("%Y-%m-%d")
        )
        end_date_str = request.args.get(
            "end_date", (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        )
        service_id = request.args.get("service_id", type=int)
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return APIResponse.error(
                "Invalid date format. Use YYYY-MM-DD",
                HTTPStatus.BAD_REQUEST,
                "InvalidDateFormat",
            )
        # Check date range validity
        if start_date > end_date:
            return APIResponse.error(
                "Start date must be before end date",
                HTTPStatus.BAD_REQUEST,
                "InvalidDateRange",
            )
        # Limit date range to 30 days maximum
        if (end_date - start_date).days > 30:
            return APIResponse.error(
                "Date range cannot exceed 30 days",
                HTTPStatus.BAD_REQUEST,
                "DateRangeTooLarge",
            )
        # Get schedule from utility function
        schedule = get_professional_schedule(
            professional_id, start_date, end_date, service_id
        )
        return APIResponse.success(
            data=calendar_view_schema.dump(schedule),
            message="Professional schedule retrieved successfully",
        )
    except Exception as e:
        return APIResponse.error(
            f"Error retrieving professional schedule: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@request_bp.route("/reviews/<int:review_id>/report", methods=["POST"])
@token_required
@role_required("professional")
def report_review(current_user, review_id):
    """Report a review for a professional's completed service request"""
    try:
        data = report_review_schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(str(err.messages))

    try:
        # Get the review
        review = Review.query.get(review_id)
        if not review:
            return APIResponse.error(
                f"Review with ID {review_id} not found",
                HTTPStatus.NOT_FOUND,
                "ReviewNotFound",
            )

        # Check if review is already reported
        if review.is_reported:
            return APIResponse.error(
                "Review is already reported", HTTPStatus.CONFLICT, "AlreadyReported"
            )

        # Verify ownership - check if the review belongs to a service request assigned to this professional
        if (
            not review.service_request
            or not review.service_request.professional_id
            or review.service_request.professional_id
            != current_user.professional_profile.id
        ):
            return APIResponse.error(
                "Cannot report reviews for other professionals' service requests",
                HTTPStatus.FORBIDDEN,
                "UnauthorizedAccess",
            )

        # Verify service was completed and has been reviewed
        if review.service_request.status != REQUEST_STATUS_COMPLETED:
            return APIResponse.error(
                "Service request must be completed to report a review",
                HTTPStatus.BAD_REQUEST,
                "InvalidStatus",
            )

        # Mark review as reported
        review.is_reported = True
        review.report_reason = data["report_reason"]

        # Create activity log
        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.REVIEW_REPORT,
            entity_id=review.id,
            description=f"Reported review for service request {review.service_request_id}",
        )
        db.session.add(log)
        db.session.commit()
        cache_invalidate()

        return APIResponse.success(
            message="Review reported successfully",
            data=review_output_schema.dump(review),
        )
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(
            f"Error reporting review: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )
