from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy import func

from src import db
from src.constants import (
    REQUEST_STATUS_ASSIGNED,
    REQUEST_STATUS_COMPLETED,
    REQUEST_STATUS_CREATED,
    USER_ROLE_CUSTOMER,
    USER_ROLE_PROFESSIONAL,
    ActivityLogActions,
)
from src.models import (
    ActivityLog,
    CustomerProfile,
    ProfessionalProfile,
    Review,
    Service,
    ServiceRequest,
    User,
)
from src.schemas.customer import (
    customer_output_schema,
    customer_update_schema,
)
from src.schemas.professional import (
    professional_output_schema,
    professional_update_schema,
)
from src.schemas.user import (
    activity_log_query_schema,
    activity_logs_schema,
    admin_output_schema,
    delete_account_schema,
    password_update_schema,
)
from src.utils.api import APIResponse
from src.utils.auth import role_required, token_required
from src.utils.cache import cache_, cache_invalidate
from src.utils.file import delete_verification_document

user_bp = Blueprint("user", __name__)


@user_bp.route("/profile", methods=["GET"])
@token_required
@cache_(300)
def get_profile(current_user):
    """Get current user's profile"""
    try:
        if current_user.role == USER_ROLE_PROFESSIONAL:
            schema = professional_output_schema
            message = "Professional profile retrieved successfully"
        elif current_user.role == USER_ROLE_CUSTOMER:
            schema = customer_output_schema
            message = f"{current_user.role.capitalize()} profile retrieved successfully"
        else:
            schema = admin_output_schema
            message = f"{current_user.role.capitalize()} profile retrieved successfully"

        return APIResponse.success(data=schema.dump(current_user), message=message)
    except Exception as e:
        return APIResponse.error(
            f"Error retrieving profile: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@user_bp.route("/change-password", methods=["POST"])
@token_required
@role_required("customer", "professional")
def change_password(current_user):
    """Change user's password"""
    try:
        data = password_update_schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(str(err.messages))

    if not current_user.check_password(data["old_password"]):
        return APIResponse.error(
            "Current password is incorrect",
            HTTPStatus.UNPROCESSABLE_ENTITY,
            "InvalidPassword",
        )

    try:
        current_user.set_password(data["new_password"])

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.USER_PASSWORD_CHANGE,
            description=f"Password changed for user {current_user.username}",
        )
        db.session.add(log)
        db.session.commit()

        cache_invalidate()

        return APIResponse.success(message="Password changed successfully")
    except Exception as e:
        return APIResponse.error(
            f"Error changing password: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@user_bp.route("/profile", methods=["PUT"])
@token_required
@role_required("customer", "professional")
def update_profile(current_user):
    """Update user's profile information"""
    try:
        schema = (
            professional_update_schema
            if current_user.role == USER_ROLE_PROFESSIONAL
            else customer_update_schema
        )
        data = schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(str(err.messages))

    try:
        if "email" in data and data["email"] != current_user.email:
            if User.query.filter_by(email=data["email"]).first():
                return APIResponse.error(
                    "Email already in use", HTTPStatus.CONFLICT, "DuplicateEmail"
                )
            current_user.email = data["email"]

        for field in ["full_name", "phone", "address", "pin_code"]:
            if field in data:
                setattr(current_user, field, data[field])

        if current_user.role == USER_ROLE_PROFESSIONAL and "description" in data:
            current_user.professional_profile.description = data["description"]

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.USER_PROFILE_UPDATE,
            description=f"Profile updated for user {current_user.username}",
        )
        db.session.add(log)
        db.session.commit()

        cache_invalidate()

        schema = (
            professional_output_schema
            if current_user.role == USER_ROLE_PROFESSIONAL
            else customer_output_schema
        )
        return APIResponse.success(
            data=schema.dump(current_user), message="Profile updated successfully"
        )
    except Exception as e:
        return APIResponse.error(
            f"Error updating profile: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@user_bp.route("/delete-account", methods=["DELETE"])
@token_required
@role_required("customer", "professional")
def delete_account(current_user):
    """Hard delete user account"""
    try:
        data = delete_account_schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(str(err.messages))

    if not current_user.check_password(data["password"]):
        return APIResponse.error(
            "Incorrect password", HTTPStatus.UNPROCESSABLE_ENTITY, "InvalidPassword"
        )

    try:
        # Check for active requests based on user role
        if current_user.role == USER_ROLE_PROFESSIONAL:
            has_active_requests = (
                ServiceRequest.query.filter(
                    ServiceRequest.professional_id
                    == current_user.professional_profile.id,
                    ServiceRequest.status.in_([REQUEST_STATUS_ASSIGNED]),
                ).first()
                is not None
            )
            verification_doc = current_user.professional_profile.verification_documents
        else:
            has_active_requests = (
                ServiceRequest.query.filter(
                    ServiceRequest.customer_id == current_user.customer_profile.id,
                    ServiceRequest.status.in_(
                        [REQUEST_STATUS_CREATED, REQUEST_STATUS_ASSIGNED]
                    ),
                ).first()
                is not None
            )

        if has_active_requests:
            return APIResponse.error(
                "Cannot delete account while having active service requests",
                HTTPStatus.CONFLICT,
                "ActiveRequestsExist",
            )

        log = ActivityLog(
            user_id=None,  # Since user will be deleted
            action=ActivityLogActions.USER_DELETE,
            description=f"Account deleted for user {current_user.username} (role: {current_user.role})",
        )
        db.session.add(log)

        if current_user.role == USER_ROLE_PROFESSIONAL and verification_doc:
            delete_verification_document(verification_doc)

        db.session.delete(current_user)
        db.session.commit()

        cache_invalidate()

        return APIResponse.success(
            message="Account successfully deleted", status_code=HTTPStatus.OK
        )
    except Exception as e:
        return APIResponse.error(
            f"Error deleting account: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@user_bp.route("/activity-logs", methods=["GET"])
@token_required
@cache_(300)
def get_activity_logs(current_user):
    """Get role-specific paginated activity logs"""
    try:
        params = activity_log_query_schema.load(request.args)
        query = ActivityLog.query

        query = query.filter(ActivityLog.user_id == current_user.id)

        # Apply common filters
        if params.get("action") and params["action"] != "all":
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


@user_bp.route("/activity-logs/<int:user_id>", methods=["GET"])
@token_required
@role_required("admin")
@cache_(300)
def get_activity_logs_by_user(current_user, user_id):
    """Get role-specific paginated activity logs"""
    try:
        params = activity_log_query_schema.load(request.args)
        query = ActivityLog.query

        query = query.filter(ActivityLog.user_id == user_id)

        # Apply common filters
        if params.get("action") and params["action"] != "all":
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


@user_bp.route("/admin/dashboard", methods=["GET"])
@token_required
@role_required("admin")
@cache_(timeout=120)
def get_admin_dashboard(current_user):
    """Get admin dashboard statistics with enhanced metrics and filtering"""
    try:
        # Helper functions to fix problematic queries
        def fix_rating_distribution_query(
            service_type_id=None, pin_code=None, start_date=None
        ):
            """Helper function to create properly structured rating distribution query"""
            rating_distribution_query = db.session.query(
                Review.rating, func.count(Review.id).label("count")
            ).select_from(Review)

            if service_type_id or pin_code:
                rating_distribution_query = rating_distribution_query.join(
                    ServiceRequest, Review.service_request_id == ServiceRequest.id
                )

                if service_type_id:
                    rating_distribution_query = rating_distribution_query.filter(
                        ServiceRequest.service_id == service_type_id
                    )

                if pin_code:
                    rating_distribution_query = (
                        rating_distribution_query.join(
                            CustomerProfile,
                            ServiceRequest.customer_id == CustomerProfile.id,
                        )
                        .join(User, CustomerProfile.user_id == User.id)
                        .filter(User.pin_code == pin_code)
                    )

            if start_date:
                rating_distribution_query = rating_distribution_query.filter(
                    Review.created_at >= start_date
                )

            return rating_distribution_query.group_by(Review.rating).order_by(
                Review.rating
            )

        def fix_reported_reviews_query(service_type_id=None, pin_code=None):
            """Helper function to create properly structured reported reviews query"""
            reported_reviews_query = (
                db.session.query(Review)
                .select_from(Review)
                .filter(Review.is_reported == True)
            )

            if service_type_id or pin_code:
                reported_reviews_query = reported_reviews_query.join(
                    ServiceRequest, Review.service_request_id == ServiceRequest.id
                )

                if service_type_id:
                    reported_reviews_query = reported_reviews_query.filter(
                        ServiceRequest.service_id == service_type_id
                    )

                if pin_code:
                    reported_reviews_query = (
                        reported_reviews_query.join(
                            CustomerProfile,
                            ServiceRequest.customer_id == CustomerProfile.id,
                        )
                        .join(User, CustomerProfile.user_id == User.id)
                        .filter(User.pin_code == pin_code)
                    )

            return reported_reviews_query.order_by(Review.created_at.desc())

        # Get filtering parameters
        period = request.args.get("period", "30d")  # Options: 7d, 30d, 90d, all
        service_type_id = request.args.get("service_type_id", type=int)
        pin_code = request.args.get("pin_code")
        compare_to = request.args.get("compare_to")  # Options: prev_period

        # Calculate date ranges
        today = datetime.now(timezone.utc)
        if period == "7d":
            start_date = today - timedelta(days=7)
            prev_start_date = start_date - timedelta(days=7)  # Previous 7 days
        elif period == "30d":
            start_date = today - timedelta(days=30)
            prev_start_date = start_date - timedelta(days=30)  # Previous 30 days
        elif period == "90d":
            start_date = today - timedelta(days=90)
            prev_start_date = start_date - timedelta(days=90)  # Previous 90 days
        else:  # "all" - no date filtering
            start_date = None
            prev_start_date = None

        # Base query filters for service requests
        base_filters = []
        if service_type_id:
            base_filters.append(ServiceRequest.service_id == service_type_id)

        # Base user filters
        user_filters = []
        if pin_code:
            user_filters.append(User.pin_code == pin_code)
        stats = {
            # User statistics
            "total_users": User.query.filter(*user_filters).count(),
            "active_users": User.query.filter(
                User.is_active == True,
                *user_filters,
            ).count(),
            "customer_count": User.query.filter(
                User.role == "customer",
                User.is_active == True,
                *user_filters,
            ).count(),
            "professional_count": User.query.filter(
                User.role == "professional",
                User.is_active == True,
                *user_filters,
            ).count(),
            # ...
        }

        # Request statistics with filters
        request_query = ServiceRequest.query
        if service_type_id:
            request_query = request_query.filter(
                ServiceRequest.service_id == service_type_id
            )
        if pin_code:
            request_query = (
                request_query.join(
                    CustomerProfile, ServiceRequest.customer_id == CustomerProfile.id
                )
                .join(User, CustomerProfile.user_id == User.id)
                .filter(User.pin_code == pin_code)
            )
        if start_date:
            request_query = request_query.filter(
                ServiceRequest.date_of_request >= start_date
            )
        stats.update(
            {
                "total_requests": request_query.count(),
                "pending_requests": request_query.filter_by(
                    status=REQUEST_STATUS_CREATED
                ).count(),
                "active_requests": request_query.filter_by(
                    status=REQUEST_STATUS_ASSIGNED
                ).count(),
                "completed_requests": request_query.filter_by(
                    status=REQUEST_STATUS_COMPLETED
                ).count(),
            }
        )

        # Calculate service fulfillment rate
        if stats["total_requests"] > 0:
            stats["service_fulfillment_rate"] = round(
                (stats["completed_requests"] / stats["total_requests"]) * 100, 1
            )
        else:
            stats["service_fulfillment_rate"] = 0.0

        # Professional verifications
        prof_query = ProfessionalProfile.query
        if pin_code:
            prof_query = prof_query.join(User).filter(User.pin_code == pin_code)
        stats["pending_verifications"] = prof_query.filter(
            ProfessionalProfile.is_verified == False
        ).count()

        # Review statistics - Fixed query with explicit joins
        review_base_query = db.session.query(Review).select_from(Review)

        if service_type_id or pin_code:
            review_base_query = review_base_query.join(
                ServiceRequest, Review.service_request_id == ServiceRequest.id
            )
            if service_type_id:
                review_base_query = review_base_query.filter(
                    ServiceRequest.service_id == service_type_id
                )
            if pin_code:
                review_base_query = (
                    review_base_query.join(
                        CustomerProfile,
                        ServiceRequest.customer_id == CustomerProfile.id,
                    )
                    .join(User, CustomerProfile.user_id == User.id)
                    .filter(User.pin_code == pin_code)
                )
        if start_date:
            review_base_query = review_base_query.filter(
                Review.created_at >= start_date
            )

        # Count total reviews
        total_reviews = review_base_query.count()

        # Count reported reviews - create a new query with the same filters
        reported_reviews_count = review_base_query.filter(
            Review.is_reported == True
        ).count()

        # Get average rating - need to create a new query to get average
        avg_rating_query = db.session.query(func.avg(Review.rating)).select_from(
            review_base_query.subquery()
        )
        avg_rating = avg_rating_query.scalar() or 0.0

        stats.update(
            {
                "total_reviews": total_reviews,
                "reported_reviews": reported_reviews_count,
                "average_rating": avg_rating,
            }
        )

        # Revenue statistics
        revenue_query = (
            db.session.query(
                func.sum(Service.base_price).label("total_revenue"),
                func.avg(Service.base_price).label("avg_revenue_per_request"),
                func.count().label("request_count"),
            )
            .select_from(Service)
            .join(ServiceRequest, ServiceRequest.service_id == Service.id)
            .filter(ServiceRequest.status == REQUEST_STATUS_COMPLETED, *base_filters)
        )
        if start_date:
            revenue_query = revenue_query.filter(
                ServiceRequest.date_of_completion >= start_date
            )
        if pin_code:
            revenue_query = (
                revenue_query.join(
                    CustomerProfile, ServiceRequest.customer_id == CustomerProfile.id
                )
                .join(User, CustomerProfile.user_id == User.id)
                .filter(User.pin_code == pin_code)
            )
        revenue_stats = revenue_query.first()
        stats.update(
            {
                "total_revenue": float(revenue_stats.total_revenue or 0),
                "avg_revenue_per_request": float(
                    revenue_stats.avg_revenue_per_request or 0
                ),
            }
        )

        # Customer retention rate - percentage of customers who have made more than 1 request
        from sqlalchemy import distinct

        # Fixed query with explicit join
        customer_query = (
            db.session.query(
                CustomerProfile.id, func.count(ServiceRequest.id).label("request_count")
            )
            .select_from(CustomerProfile)
            .join(ServiceRequest, ServiceRequest.customer_id == CustomerProfile.id)
        )

        if base_filters:
            customer_query = customer_query.filter(*base_filters)

        if start_date:
            customer_query = customer_query.filter(
                ServiceRequest.date_of_request >= start_date
            )

        if service_type_id:
            customer_query = customer_query.filter(
                ServiceRequest.service_id == service_type_id
            )

        if pin_code:
            customer_query = customer_query.join(
                User, CustomerProfile.user_id == User.id
            ).filter(User.pin_code == pin_code)

        customer_query = customer_query.group_by(CustomerProfile.id)

        # Get total active customers and returning customers
        total_active_customers = customer_query.count()
        returning_customers = customer_query.having(
            func.count(ServiceRequest.id) > 1
        ).count()

        if total_active_customers > 0:
            stats["customer_retention_rate"] = round(
                (returning_customers / total_active_customers) * 100, 1
            )
        else:
            stats["customer_retention_rate"] = 0.0

        # PERIOD COMPARISONS #
        if compare_to == "prev_period" and prev_start_date:
            # Previous period request stats
            prev_request_query = ServiceRequest.query.filter(
                ServiceRequest.date_of_request >= prev_start_date,
                ServiceRequest.date_of_request < start_date,
                *base_filters,
            )
            if pin_code:
                prev_request_query = (
                    prev_request_query.join(
                        CustomerProfile,
                        ServiceRequest.customer_id == CustomerProfile.id,
                    )
                    .join(User, CustomerProfile.user_id == User.id)
                    .filter(User.pin_code == pin_code)
                )
            prev_stats = {
                "prev_total_requests": prev_request_query.count(),
                "prev_completed_requests": prev_request_query.filter_by(
                    status=REQUEST_STATUS_COMPLETED
                ).count(),
            }
            # Calculate period-over-period changes
            if prev_stats["prev_total_requests"] > 0:
                prev_stats["total_requests_change_pct"] = round(
                    (
                        (stats["total_requests"] - prev_stats["prev_total_requests"])
                        / prev_stats["prev_total_requests"]
                    )
                    * 100,
                    1,
                )
            else:
                prev_stats["total_requests_change_pct"] = (
                    100 if stats["total_requests"] > 0 else 0
                )
            if prev_stats["prev_completed_requests"] > 0:
                prev_stats["completed_requests_change_pct"] = round(
                    (
                        (
                            stats["completed_requests"]
                            - prev_stats["prev_completed_requests"]
                        )
                        / prev_stats["prev_completed_requests"]
                    )
                    * 100,
                    1,
                )
            else:
                prev_stats["completed_requests_change_pct"] = (
                    100 if stats["completed_requests"] > 0 else 0
                )

            # Previous period revenue stats
            prev_revenue_query = (
                db.session.query(func.sum(Service.base_price).label("total_revenue"))
                .select_from(Service)
                .join(ServiceRequest, ServiceRequest.service_id == Service.id)
                .filter(
                    ServiceRequest.status == REQUEST_STATUS_COMPLETED,
                    ServiceRequest.date_of_completion >= prev_start_date,
                    ServiceRequest.date_of_completion < start_date,
                    *base_filters,
                )
            )
            if pin_code:
                prev_revenue_query = (
                    prev_revenue_query.join(
                        CustomerProfile,
                        ServiceRequest.customer_id == CustomerProfile.id,
                    )
                    .join(User, CustomerProfile.user_id == User.id)
                    .filter(User.pin_code == pin_code)
                )
            prev_revenue = prev_revenue_query.scalar() or 0
            if prev_revenue > 0:
                prev_stats["revenue_change_pct"] = round(
                    ((stats["total_revenue"] - prev_revenue) / prev_revenue) * 100, 1
                )
            else:
                prev_stats["revenue_change_pct"] = (
                    100 if stats["total_revenue"] > 0 else 0
                )

            # Previous period rating stats - Fixed with proper explicit joins
            prev_review_query = (
                db.session.query(Review)
                .select_from(Review)
                .filter(
                    Review.created_at >= prev_start_date, Review.created_at < start_date
                )
            )

            if service_type_id or pin_code:
                prev_review_query = prev_review_query.join(
                    ServiceRequest, Review.service_request_id == ServiceRequest.id
                )

                if service_type_id:
                    prev_review_query = prev_review_query.filter(
                        ServiceRequest.service_id == service_type_id
                    )

                if pin_code:
                    prev_review_query = (
                        prev_review_query.join(
                            CustomerProfile,
                            ServiceRequest.customer_id == CustomerProfile.id,
                        )
                        .join(User, CustomerProfile.user_id == User.id)
                        .filter(User.pin_code == pin_code)
                    )

            # Now get the average rating from the filtered query
            prev_avg_rating_query = db.session.query(
                func.avg(Review.rating)
            ).select_from(prev_review_query.subquery())
            prev_avg_rating = prev_avg_rating_query.scalar() or 0.0

            prev_stats["prev_avg_rating"] = round(float(prev_avg_rating), 1)
            if prev_avg_rating > 0:
                prev_stats["rating_change_pct"] = round(
                    ((stats["average_rating"] - prev_avg_rating) / prev_avg_rating)
                    * 100,
                    1,
                )
            else:
                prev_stats["rating_change_pct"] = 0

            # Add previous period stats to main stats
            stats["period_comparison"] = prev_stats

        # Recent user registrations
        recent_registrations_query = User.query.filter(*user_filters).order_by(
            User.created_at.desc()
        )
        recent_registrations = [
            {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role,
                "created_at": user.created_at.strftime("%Y-%m-%d %H:%M"),
                "is_active": user.is_active,
                "profile_id": user.professional_profile.id
                if user.role == "professional" and user.professional_profile
                else (
                    user.customer_profile.id
                    if user.role == "customer" and user.customer_profile
                    else None
                ),
            }
            for user in recent_registrations_query.limit(5).all()
        ]
        stats["recent_registrations"] = recent_registrations

        # Pending professional verifications
        pending_verifications_query = (
            ProfessionalProfile.query.join(User)
            .filter(
                ProfessionalProfile.is_verified == False,
                User.is_active == True,
            )
            .order_by(ProfessionalProfile.created_at.asc())
        )

        if pin_code:
            pending_verifications_query = pending_verifications_query.filter(
                User.pin_code == pin_code
            )

        pending_verifications = [
            {
                "id": profile.id,
                "user_id": profile.user_id,
                "full_name": profile.user.full_name,
                "service_type": profile.service_type.name,
                "experience_years": profile.experience_years,
                "created_at": profile.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            for profile in pending_verifications_query.limit(5).all()
        ]
        stats["pending_verifications"] = pending_verifications

        # Recent service requests (with filters)
        recent_requests_query = ServiceRequest.query

        if base_filters:
            for filter_condition in base_filters:
                recent_requests_query = recent_requests_query.filter(filter_condition)

        if pin_code:
            recent_requests_query = (
                recent_requests_query.join(
                    CustomerProfile, ServiceRequest.customer_id == CustomerProfile.id
                )
                .join(User, CustomerProfile.user_id == User.id)
                .filter(User.pin_code == pin_code)
            )

        recent_requests_query = recent_requests_query.order_by(
            ServiceRequest.date_of_request.desc()
        )

        recent_requests = [
            {
                "id": req.id,
                "service_name": req.service.name,
                "customer_name": req.customer.user.full_name,
                "professional_name": req.professional.user.full_name
                if req.professional
                else "Not assigned",
                "date_of_request": req.date_of_request.strftime("%Y-%m-%d %H:%M"),
                "status": req.status,
                "preferred_time": req.preferred_time.strftime("%Y-%m-%d %H:%M"),
            }
            for req in recent_requests_query.limit(5).all()
        ]
        stats["recent_requests"] = recent_requests

        # Popular services (most requested) with filters - Fixed with proper joins
        popular_services_query = (
            db.session.query(
                Service.id,
                Service.name,
                func.count(ServiceRequest.id).label("request_count"),
            )
            .select_from(Service)
            .join(ServiceRequest, ServiceRequest.service_id == Service.id)
        )

        if base_filters:
            for filter_condition in base_filters:
                popular_services_query = popular_services_query.filter(filter_condition)

        if start_date:
            popular_services_query = popular_services_query.filter(
                ServiceRequest.date_of_request >= start_date
            )

        if pin_code:
            popular_services_query = (
                popular_services_query.join(
                    CustomerProfile, ServiceRequest.customer_id == CustomerProfile.id
                )
                .join(User, CustomerProfile.user_id == User.id)
                .filter(User.pin_code == pin_code)
            )

        # Apply group by and order by before limit
        popular_services_query = popular_services_query.group_by(
            Service.id, Service.name
        ).order_by(func.count(ServiceRequest.id).desc())

        popular_services = [
            {"id": row.id, "name": row.name, "request_count": row.request_count}
            for row in popular_services_query.limit(5).all()
        ]
        stats["popular_services"] = popular_services

        # Reported reviews that need attention (with filters) - Fixed with helper function
        reported_reviews_query = fix_reported_reviews_query(service_type_id, pin_code)
        reported_reviews = [
            {
                "id": review.id,
                "service_request_id": review.service_request_id,
                "service_name": review.service_request.service.name,
                "professional_name": review.service_request.professional.user.full_name
                if review.service_request.professional
                else "Unknown",
                "rating": review.rating,
                "comment": review.comment,
                "report_reason": review.report_reason,
                "created_at": review.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            for review in reported_reviews_query.limit(5).all()
        ]
        stats["reported_reviews"] = reported_reviews

        # Weekly registration trend (with filters)
        weekly_registration_trend = []
        if period == "all" or period == "90d":
            # For longer periods, show weekly data for past 12 weeks
            num_weeks = 12
        else:
            # For shorter periods, show daily data
            num_weeks = int(period[:-1]) // 7 or 1
        for i in range(num_weeks):
            end_date = today - timedelta(days=i * 7)
            start_date_week = end_date - timedelta(days=7)
            # Base query with pin_code filter if applicable
            customer_query = User.query.filter(
                User.role == "customer",
                User.created_at >= start_date_week,
                User.created_at < end_date,
            )
            professional_query = User.query.filter(
                User.role == "professional",
                User.created_at >= start_date_week,
                User.created_at < end_date,
            )
            if pin_code:
                customer_query = customer_query.filter(User.pin_code == pin_code)
                professional_query = professional_query.filter(
                    User.pin_code == pin_code
                )
            customers = customer_query.count()
            professionals = professional_query.count()
            weekly_registration_trend.insert(
                0,
                {
                    "period": start_date_week.strftime("%Y-%m-%d"),
                    "customers": customers,
                    "professionals": professionals,
                    "total": customers + professionals,
                },
            )
        stats["weekly_registration_trend"] = weekly_registration_trend

        # Service requests by status trend (with filters)
        request_status_trend = []
        for i in range(num_weeks):
            end_date = today - timedelta(days=i * 7)
            start_date_week = end_date - timedelta(days=7)
            # Base query with service_type_id filter if applicable
            created_query = ServiceRequest.query.filter(
                ServiceRequest.status == REQUEST_STATUS_CREATED,
                ServiceRequest.date_of_request >= start_date_week,
                ServiceRequest.date_of_request < end_date,
            )
            assigned_query = ServiceRequest.query.filter(
                ServiceRequest.status == REQUEST_STATUS_ASSIGNED,
                ServiceRequest.date_of_request >= start_date_week,
                ServiceRequest.date_of_request < end_date,
            )
            completed_query = ServiceRequest.query.filter(
                ServiceRequest.status == REQUEST_STATUS_COMPLETED,
                ServiceRequest.date_of_request >= start_date_week,
                ServiceRequest.date_of_request < end_date,
            )
            if service_type_id:
                created_query = created_query.filter(
                    ServiceRequest.service_id == service_type_id
                )
                assigned_query = assigned_query.filter(
                    ServiceRequest.service_id == service_type_id
                )
                completed_query = completed_query.filter(
                    ServiceRequest.service_id == service_type_id
                )
            if pin_code:
                # Apply proper joins for all three queries
                created_query = (
                    created_query.join(
                        CustomerProfile,
                        ServiceRequest.customer_id == CustomerProfile.id,
                    )
                    .join(User, CustomerProfile.user_id == User.id)
                    .filter(User.pin_code == pin_code)
                )
                assigned_query = (
                    assigned_query.join(
                        CustomerProfile,
                        ServiceRequest.customer_id == CustomerProfile.id,
                    )
                    .join(User, CustomerProfile.user_id == User.id)
                    .filter(User.pin_code == pin_code)
                )
                completed_query = (
                    completed_query.join(
                        CustomerProfile,
                        ServiceRequest.customer_id == CustomerProfile.id,
                    )
                    .join(User, CustomerProfile.user_id == User.id)
                    .filter(User.pin_code == pin_code)
                )
            created_count = created_query.count()
            assigned_count = assigned_query.count()
            completed_count = completed_query.count()
            request_status_trend.insert(
                0,
                {
                    "period": start_date_week.strftime("%Y-%m-%d"),
                    "created": created_count,
                    "assigned": assigned_count,
                    "completed": completed_count,
                    "total": created_count + assigned_count + completed_count,
                },
            )
        stats["request_status_trend"] = request_status_trend

        # Add geographic distribution by pin code (with service_type filter)
        if service_type_id:
            geo_distribution_query = (
                db.session.query(
                    User.pin_code, func.count(distinct(User.id)).label("user_count")
                )
                .select_from(User)
                .join(CustomerProfile, User.id == CustomerProfile.user_id)
                .join(ServiceRequest, CustomerProfile.id == ServiceRequest.customer_id)
                .filter(ServiceRequest.service_id == service_type_id)
                .group_by(User.pin_code)
                .order_by(func.count(distinct(User.id)).desc())
            )
        else:
            geo_distribution_query = (
                db.session.query(User.pin_code, func.count(User.id).label("user_count"))
                .group_by(User.pin_code)
                .order_by(func.count(User.id).desc())
            )

        geo_distribution = [
            {"pin_code": row.pin_code, "user_count": row.user_count}
            for row in geo_distribution_query.limit(10).all()
        ]
        stats["geographic_distribution"] = geo_distribution

        # Add rating distribution (with filters)
        rating_distribution_query = fix_rating_distribution_query(
            service_type_id, pin_code, start_date
        )
        rating_distribution = [
            {"rating": row.rating, "count": row.count}
            for row in rating_distribution_query.all()
        ]

        # Ensure all ratings 1-5 are represented
        existing_ratings = {item["rating"] for item in rating_distribution}
        for rating in range(1, 6):
            if rating not in existing_ratings:
                rating_distribution.append({"rating": rating, "count": 0})
        # Sort by rating
        rating_distribution.sort(key=lambda x: x["rating"])
        stats["rating_distribution"] = rating_distribution

        # Add system activity (recent activity logs) - with user filtering
        recent_activities_query = ActivityLog.query

        if pin_code:
            # Filter logs by users with matching pin_code
            user_ids_query = User.query.filter(User.pin_code == pin_code).with_entities(
                User.id
            )
            user_ids = [user.id for user in user_ids_query.all()]
            if user_ids:
                recent_activities_query = recent_activities_query.filter(
                    ActivityLog.user_id.in_(user_ids)
                )

        # Apply order by before limit
        recent_activities_query = recent_activities_query.order_by(
            ActivityLog.created_at.desc()
        )

        recent_activities = [
            {
                "id": log.id,
                "action": log.action,
                "description": log.description,
                "user_id": log.user_id,
                "created_at": log.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            for log in recent_activities_query.limit(10).all()
        ]
        stats["recent_activities"] = recent_activities

        # NEW: Monthly revenue trend
        if period != "7d":  # Only show for 30d, 90d, all
            num_months = 12 if period == "all" or period == "90d" else 6
            monthly_revenue_trend = []
            for i in range(num_months):
                end_date = today.replace(day=1) - timedelta(days=i * 30)
                start_date_month = end_date - timedelta(days=30)
                revenue_query = (
                    db.session.query(
                        func.sum(Service.base_price).label("monthly_revenue")
                    )
                    .select_from(Service)
                    .join(ServiceRequest, ServiceRequest.service_id == Service.id)
                    .filter(
                        ServiceRequest.status == REQUEST_STATUS_COMPLETED,
                        ServiceRequest.date_of_completion >= start_date_month,
                        ServiceRequest.date_of_completion < end_date,
                    )
                )

                if base_filters:
                    for filter_condition in base_filters:
                        revenue_query = revenue_query.filter(filter_condition)

                if pin_code:
                    revenue_query = (
                        revenue_query.join(
                            CustomerProfile,
                            ServiceRequest.customer_id == CustomerProfile.id,
                        )
                        .join(User, CustomerProfile.user_id == User.id)
                        .filter(User.pin_code == pin_code)
                    )

                monthly_revenue = revenue_query.scalar() or 0
                monthly_revenue_trend.insert(
                    0,
                    {
                        "month": start_date_month.strftime("%Y-%m"),
                        "revenue": float(monthly_revenue),
                    },
                )
            stats["monthly_revenue_trend"] = monthly_revenue_trend

        return APIResponse.success(
            data=stats, message="Admin dashboard statistics retrieved successfully"
        )
    except Exception as e:
        return APIResponse.error(
            f"Error retrieving dashboard stats: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )
