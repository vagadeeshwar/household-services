# src/routes/dashboard/routes.py
from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy import func, desc
from http import HTTPStatus

from src.models import (
    User,
    ProfessionalProfile,
    CustomerProfile,
    ServiceRequest,
    Review,
    ActivityLog,
    Service,
    db,
)

from src.constants import (
    REQUEST_STATUS_CREATED,
    REQUEST_STATUS_COMPLETED,
    REQUEST_STATUS_ASSIGNED,
)

from src.schemas.dashboard import (
    activity_logs_schema,
    activity_log_query_schema,
    detailed_stats_query_schema,
    dashboard_stats_schema,
)
from src.schemas.professional import professionals_output_schema
from src.schemas.customer import customers_output_schema
from src.schemas.request import service_requests_output_schema, reviews_output_schema
from src.schemas.service import services_output_schema

from src.utils.auth import token_required
from src.utils.api import APIResponse
from src.utils.cache import cached_with_auth

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard-stats", methods=["GET"])
@token_required
@cached_with_auth(timeout=60)
def get_dashboard_stats(current_user):
    """Get role-specific dashboard statistics"""
    try:
        stats = {}

        if current_user.role == "admin":
            # Admin sees platform-wide statistics
            stats = {
                "total_professionals": ProfessionalProfile.query.count(),
                "verified_professionals": ProfessionalProfile.query.filter_by(
                    is_verified=True
                ).count(),
                "total_customers": CustomerProfile.query.count(),
                "active_customers": CustomerProfile.query.join(User)
                .filter(User.is_active)
                .count(),
                "pending_verifications": ProfessionalProfile.query.filter_by(
                    is_verified=False
                ).count(),
                "reported_reviews": Review.query.filter_by(is_reported=True).count(),
                "service_requests": {
                    "total": ServiceRequest.query.count(),
                    "pending": ServiceRequest.query.filter_by(
                        status=REQUEST_STATUS_CREATED
                    ).count(),
                    "completed": ServiceRequest.query.filter_by(
                        status=REQUEST_STATUS_COMPLETED
                    ).count(),
                },
            }

        elif current_user.role == "professional":
            # Professional sees their service-related statistics
            professional = current_user.professional_profile
            if not professional:
                return APIResponse.error(
                    "Professional profile not found", HTTPStatus.NOT_FOUND
                )

            total_requests = ServiceRequest.query.filter_by(
                professional_id=professional.id
            )
            stats = {
                "profile_status": {
                    "is_verified": professional.is_verified,
                    "is_active": current_user.is_active,
                    "average_rating": professional.average_rating or 0.0,
                },
                "service_requests": {
                    "total": total_requests.count(),
                    "active": total_requests.filter_by(
                        status=REQUEST_STATUS_ASSIGNED
                    ).count(),
                    "completed": total_requests.filter_by(
                        status=REQUEST_STATUS_COMPLETED
                    ).count(),
                    "pending_review": Review.query.join(ServiceRequest)
                    .filter(
                        ServiceRequest.professional_id == professional.id,
                        ServiceRequest.status == REQUEST_STATUS_COMPLETED,
                    )
                    .count(),
                },
                "reviews": {
                    "total": Review.query.join(ServiceRequest)
                    .filter(ServiceRequest.professional_id == professional.id)
                    .count(),
                    "average_rating": db.session.query(func.avg(Review.rating))
                    .join(ServiceRequest)
                    .filter(ServiceRequest.professional_id == professional.id)
                    .scalar()
                    or 0.0,
                    "reported": Review.query.join(ServiceRequest)
                    .filter(
                        ServiceRequest.professional_id == professional.id,
                        Review.is_reported == True,  # noqa: E712
                    )
                    .count(),
                },
            }

        elif current_user.role == "customer":
            # Customer sees their request-related statistics
            customer = current_user.customer_profile
            if not customer:
                return APIResponse.error(
                    "Customer profile not found", HTTPStatus.NOT_FOUND
                )

            customer_requests = ServiceRequest.query.filter_by(customer_id=customer.id)
            stats = {
                "service_requests": {
                    "total": customer_requests.count(),
                    "active": customer_requests.filter_by(
                        status=REQUEST_STATUS_ASSIGNED
                    ).count(),
                    "pending": customer_requests.filter_by(
                        status=REQUEST_STATUS_CREATED
                    ).count(),
                    "completed": customer_requests.filter_by(
                        status=REQUEST_STATUS_COMPLETED
                    ).count(),
                },
                "reviews_given": Review.query.join(ServiceRequest)
                .filter(ServiceRequest.customer_id == customer.id)
                .count(),
                "recent_services": Service.query.join(ServiceRequest)
                .filter(ServiceRequest.customer_id == customer.id)
                .group_by(Service.id)
                .count(),
            }

        return APIResponse.success(
            data=dashboard_stats_schema.dump(stats),
            message="Dashboard statistics retrieved successfully",
        )

    except Exception as e:
        return APIResponse.error(
            f"Error retrieving dashboard statistics: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@dashboard_bp.route("/activity-logs", methods=["GET"])
@token_required
def list_activity_logs(current_user):
    """Get role-specific paginated activity logs"""
    try:
        params = activity_log_query_schema.load(request.args)
        query = ActivityLog.query

        # Base query depends on user role
        if current_user.role == "admin":
            # Admin can see all activities
            pass
        else:
            # Others can only see their own activities
            query = query.filter(ActivityLog.user_id == current_user.id)

        # Apply common filters
        if params.get("action"):
            query = query.filter(ActivityLog.action == params["action"])
        if params.get("start_date"):
            query = query.filter(ActivityLog.created_at >= params["start_date"])
        if params.get("end_date"):
            query = query.filter(ActivityLog.created_at <= params["end_date"])

        # Always order by latest first
        query = query.order_by(ActivityLog.created_at.desc())

        # Apply pagination
        paginated = query.paginate(
            page=params["page"], per_page=params["per_page"], error_out=False
        )

        return APIResponse.success(
            data=activity_logs_schema.dump(paginated.items),
            message="Activity logs retrieved successfully",
            pagination={
                "total": paginated.total,
                "pages": paginated.pages,
                "current_page": paginated.page,
                "per_page": paginated.per_page,
                "has_next": paginated.has_next,
                "has_prev": paginated.has_prev,
            },
        )

    except ValidationError as err:
        return APIResponse.error(str(err.messages))
    except Exception as e:
        return APIResponse.error(
            f"Error retrieving activity logs: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@dashboard_bp.route("/detailed-stats", methods=["GET"])
@token_required
def get_detailed_stats(current_user):
    """Get role-specific detailed statistics with pagination"""
    try:
        params = detailed_stats_query_schema.load(request.args)

        # Define available stat types for each role
        stat_types = {
            "admin": {
                "pending_verifications": lambda: (
                    ProfessionalProfile.query.filter_by(is_verified=False)
                    .join(User)
                    .order_by(desc(ProfessionalProfile.created_at)),
                    professionals_output_schema,
                ),
                "reported_reviews": lambda: (
                    Review.query.filter_by(is_reported=True).order_by(
                        desc(Review.created_at)
                    ),
                    reviews_output_schema,
                ),
                "recent_professionals": lambda: (
                    User.query.filter_by(role="professional").order_by(
                        desc(User.created_at)
                    ),
                    professionals_output_schema,
                ),
                "recent_customers": lambda: (
                    User.query.filter_by(role="customer").order_by(
                        desc(User.created_at)
                    ),
                    customers_output_schema,
                ),
                "recent_requests": lambda: (
                    ServiceRequest.query.order_by(desc(ServiceRequest.date_of_request)),
                    service_requests_output_schema,
                ),
            },
            "professional": {
                "pending_requests": lambda: (
                    ServiceRequest.query.filter_by(
                        service_id=current_user.professional_profile.service_type_id,
                        status=REQUEST_STATUS_CREATED,
                    ).order_by(desc(ServiceRequest.date_of_request)),
                    service_requests_output_schema,
                ),
                "active_requests": lambda: (
                    ServiceRequest.query.filter_by(
                        professional_id=current_user.professional_profile.id,
                        status=REQUEST_STATUS_ASSIGNED,
                    ).order_by(desc(ServiceRequest.date_of_request)),
                    service_requests_output_schema,
                ),
                "completed_requests": lambda: (
                    ServiceRequest.query.filter_by(
                        professional_id=current_user.professional_profile.id,
                        status=REQUEST_STATUS_COMPLETED,
                    ).order_by(desc(ServiceRequest.date_of_request)),
                    service_requests_output_schema,
                ),
                "my_reviews": lambda: (
                    Review.query.join(ServiceRequest)
                    .filter(
                        ServiceRequest.professional_id
                        == current_user.professional_profile.id
                    )
                    .order_by(desc(Review.created_at)),
                    reviews_output_schema,
                ),
                "reported_reviews": lambda: (
                    Review.query.join(ServiceRequest)
                    .filter(
                        ServiceRequest.professional_id
                        == current_user.professional_profile.id,
                        Review.is_reported == True,  # noqa: E712
                    )
                    .order_by(desc(Review.created_at)),
                    reviews_output_schema,
                ),
            },
            "customer": {
                "pending_requests": lambda: (
                    ServiceRequest.query.filter_by(
                        customer_id=current_user.customer_profile.id,
                        status=REQUEST_STATUS_CREATED,
                    ).order_by(desc(ServiceRequest.date_of_request)),
                    service_requests_output_schema,
                ),
                "active_requests": lambda: (
                    ServiceRequest.query.filter_by(
                        customer_id=current_user.customer_profile.id,
                        status=REQUEST_STATUS_ASSIGNED,
                    ).order_by(desc(ServiceRequest.date_of_request)),
                    service_requests_output_schema,
                ),
                "completed_requests": lambda: (
                    ServiceRequest.query.filter_by(
                        customer_id=current_user.customer_profile.id,
                        status=REQUEST_STATUS_COMPLETED,
                    ).order_by(desc(ServiceRequest.date_of_request)),
                    service_requests_output_schema,
                ),
                "my_reviews": lambda: (
                    Review.query.join(ServiceRequest)
                    .filter(
                        ServiceRequest.customer_id == current_user.customer_profile.id
                    )
                    .order_by(desc(Review.created_at)),
                    reviews_output_schema,
                ),
                "available_services": lambda: (
                    Service.query.filter_by(is_active=True).order_by(Service.name),
                    services_output_schema,
                ),
            },
        }

        # Get available stat types for current user's role
        role_stat_types = stat_types.get(current_user.role, {})

        # Validate requested stat type
        if params["stat_type"] not in role_stat_types:
            return APIResponse.error(
                f"Invalid stat type for {current_user.role}. Available types: {', '.join(role_stat_types.keys())}",
                HTTPStatus.BAD_REQUEST,
                "InvalidStatType",
            )

        # Get query and schema for requested stat type
        query, schema = role_stat_types[params["stat_type"]]()

        # Apply date filters if applicable
        if hasattr(query.column_descriptions[0]["type"], "created_at"):
            if params.get("start_date"):
                query = query.filter(
                    query.column_descriptions[0]["type"].created_at
                    >= params["start_date"]
                )
            if params.get("end_date"):
                query = query.filter(
                    query.column_descriptions[0]["type"].created_at
                    <= params["end_date"]
                )

        # Apply pagination
        paginated = query.paginate(
            page=params["page"], per_page=params["per_page"], error_out=False
        )

        return APIResponse.success(
            data=schema.dump(paginated.items),
            message=f"Detailed {params['stat_type']} retrieved successfully",
            pagination={
                "total": paginated.total,
                "pages": paginated.pages,
                "current_page": paginated.page,
                "per_page": paginated.per_page,
                "has_next": paginated.has_next,
                "has_prev": paginated.has_prev,
            },
        )

    except ValidationError as err:
        return APIResponse.error(str(err.messages))
    except Exception as e:
        return APIResponse.error(
            f"Error retrieving detailed statistics: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )
