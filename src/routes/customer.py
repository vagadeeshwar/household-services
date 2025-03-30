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
    ActivityLogActions,
)
from src.models import (
    ActivityLog,
    CustomerProfile,
    Review,
    Service,
    ServiceRequest,
    User,
)
from src.schemas.customer import (
    customer_output_schema,
    customer_query_schema,
    customer_register_schema,
    customers_output_schema,
)
from src.schemas.user import block_user_schema
from src.tasks import send_account_status_notification
from src.utils.api import APIResponse
from src.utils.auth import role_required, token_required
from src.utils.cache import cache_, cache_invalidate
from src.utils.user import check_existing_user

customer_bp = Blueprint("customer", __name__)


@customer_bp.route("/register/customer", methods=["POST"])
def register_customer():
    """Register a new customer"""
    try:
        data = customer_register_schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(str(err.messages))

    exists, error_response = check_existing_user(data["username"], data["email"])
    if exists:
        return error_response

    try:
        user = User(
            username=data["username"],
            email=data["email"],
            full_name=data["full_name"],
            phone=data["phone"],
            address=data["address"],
            pin_code=data["pin_code"],
            role=USER_ROLE_CUSTOMER,
            is_active=True,
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.flush()

        profile = CustomerProfile(user_id=user.id)
        db.session.add(profile)

        log = ActivityLog(
            user_id=user.id,
            action=ActivityLogActions.USER_REGISTER,
            description=f"New customer account created for {user.username}",
        )
        db.session.add(log)
        db.session.commit()

        cache_invalidate()

        return APIResponse.success(
            data=customer_output_schema.dump(user),
            message="Customer registered successfully",
            status_code=HTTPStatus.CREATED,
        )
    except Exception as e:
        return APIResponse.error(
            f"Error creating customer: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@customer_bp.route("/customers", methods=["GET"])
@customer_bp.route("/customers/<int:profile_id>", methods=["GET"])
@token_required
@role_required("admin")
@cache_(timeout=300)
def list_customers(current_user, profile_id=None):
    """List all customers or get a specific customer by ID"""
    try:
        if profile_id is not None:
            # Single customer retrieval
            profile = (
                CustomerProfile.query.join(User)
                .filter(CustomerProfile.id == profile_id)
                .first_or_404()
            )

            return APIResponse.success(
                data=customer_output_schema.dump(profile.user),  # Use the schema here
                message="Customer retrieved successfully",
            )

        # List all customers
        params = customer_query_schema.load(request.args)
        query = User.query.join(CustomerProfile).filter(User.role == USER_ROLE_CUSTOMER)

        if params.get("active") is not None:
            query = query.filter(User.is_active == params["active"])
        if params.get("pin_code"):
            query = query.filter(User.pin_code == params["pin_code"])

        try:
            paginated = query.paginate(
                page=params["page"], per_page=params["per_page"], error_out=False
            )
        except Exception as e:
            return APIResponse.error(
                f"Pagination error: {str(e)}", HTTPStatus.BAD_REQUEST, "PaginationError"
            )

        return APIResponse.success(
            data=customers_output_schema.dump(paginated.items),
            message="Customers retrieved successfully",
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
            f"Error retrieving customers: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@customer_bp.route("/customers/<int:profile_id>/block", methods=["POST"])
@token_required
@role_required("admin")
def block_customer(current_user, profile_id):
    """Block a customer's account"""
    try:
        data = block_user_schema.load(request.get_json())
        profile = CustomerProfile.query.get(profile_id)
        if not profile:
            return APIResponse.error(
                "Customer not found", HTTPStatus.NOT_FOUND, "CustomerNotFound"
            )

        if not profile.user.is_active:
            return APIResponse.error(
                "Customer is already blocked", HTTPStatus.CONFLICT, "AlreadyBlocked"
            )

        # Check for active service requests
        has_active_requests = (
            ServiceRequest.query.filter(
                ServiceRequest.customer_id == profile.id,
                ServiceRequest.status.in_(
                    [REQUEST_STATUS_CREATED, REQUEST_STATUS_ASSIGNED]
                ),
            ).first()
            is not None
        )

        if has_active_requests:
            return APIResponse.error(
                "Cannot block customer with active service requests",
                HTTPStatus.CONFLICT,
                "ActiveRequestsExist",
            )

        profile.user.is_active = False
        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.CUSTOMER_BLOCK,
            entity_id=profile.user.id,
            description=f"Blocked customer {profile.user.full_name}. Reason: {data['reason']}",
        )
        db.session.add(log)
        db.session.commit()
        cache_invalidate()

        return APIResponse.success(message="Customer blocked successfully")
    except ValidationError as err:
        return APIResponse.error(str(err.messages))
    except Exception as e:
        return APIResponse.error(
            f"Error blocking customer: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@customer_bp.route("/customers/<int:profile_id>/unblock", methods=["POST"])
@token_required
@role_required("admin")
def unblock_customer(current_user, profile_id):
    """Unblock a customer's account"""
    try:
        profile = CustomerProfile.query.get(profile_id)
        if not profile:
            return APIResponse.error(
                "Customer not found", HTTPStatus.NOT_FOUND, "CustomerNotFound"
            )

        if profile.user.is_active:
            return APIResponse.error(
                "Customer is already active", HTTPStatus.CONFLICT, "AlreadyActive"
            )

        profile.user.is_active = True
        log = ActivityLog(
            user_id=current_user.id,
            entity_id=profile.user.id,
            action=ActivityLogActions.CUSTOMER_UNBLOCK,
            description=f"Unblocked customer {profile.user.full_name}",
        )
        db.session.add(log)
        db.session.commit()
        cache_invalidate()

        # Send notification email via task
        send_account_status_notification.delay(
            profile.user.email,
            profile.user.full_name,
            "emails/account_unblocked.html",
            "Account Unblocked",
        )

        return APIResponse.success(message="Customer unblocked successfully")
    except Exception as e:
        return APIResponse.error(
            f"Error unblocking customer: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@customer_bp.route("/customers/dashboard", methods=["GET"])
@token_required
@role_required("customer")
@cache_(timeout=120)
def get_customer_dashboard(current_user):
    """Get customer's dashboard statistics with trend data"""
    try:
        customer_id = current_user.customer_profile.id
        # Get time period from query params (default: last 30 days)
        period = request.args.get("period", "30d")  # Options: 7d, 30d, 90d, all
        # Calculate date range based on period
        today = datetime.now(timezone.utc)
        if period == "7d":
            start_date = today - timedelta(days=7)
        elif period == "30d":
            start_date = today - timedelta(days=30)
        elif period == "90d":
            start_date = today - timedelta(days=90)
        else:  # "all" - find earliest date
            earliest_request = (
                ServiceRequest.query.filter(
                    ServiceRequest.customer_id == customer_id,
                    ServiceRequest.status == REQUEST_STATUS_COMPLETED,
                )
                .order_by(ServiceRequest.date_of_completion.asc())
                .first()
            )

            if earliest_request and earliest_request.date_of_completion:
                start_date = earliest_request.date_of_completion
            else:
                # Fallback if no completed requests
                start_date = today - timedelta(days=365)  # Default to 1 year

        # Base query with optional date filtering
        completed_requests_query = ServiceRequest.query.filter(
            ServiceRequest.customer_id == customer_id,
            ServiceRequest.status == REQUEST_STATUS_COMPLETED,
        )
        if start_date:
            completed_requests_query = completed_requests_query.filter(
                ServiceRequest.date_of_completion >= start_date
            )

        # Core statistics
        stats = {
            "total_requests": ServiceRequest.query.filter_by(
                customer_id=customer_id
            ).count(),
            "completed_requests": completed_requests_query.count(),
            "active_requests": ServiceRequest.query.filter(
                ServiceRequest.customer_id == customer_id,
                ServiceRequest.status.in_(
                    [REQUEST_STATUS_CREATED, REQUEST_STATUS_ASSIGNED]
                ),
            ).count(),
            "total_spent": db.session.query(func.sum(Service.base_price))
            .join(ServiceRequest, ServiceRequest.service_id == Service.id)
            .filter(
                ServiceRequest.customer_id == customer_id,
                ServiceRequest.status == REQUEST_STATUS_COMPLETED,
            )
            .scalar()
            or 0.0,
        }

        # Add services needing review
        pending_reviews_query = ServiceRequest.query.outerjoin(
            Review, ServiceRequest.id == Review.service_request_id
        ).filter(
            ServiceRequest.customer_id == customer_id,
            ServiceRequest.status == REQUEST_STATUS_COMPLETED,
            Review.id.is_(None),
        )
        stats["pending_reviews"] = pending_reviews_query.count()

        # Average rating given by customer
        avg_rating = (
            db.session.query(func.avg(Review.rating))
            .join(ServiceRequest)
            .filter(ServiceRequest.customer_id == customer_id)
            .scalar()
            or 0.0
        )
        stats["average_rating_given"] = round(float(avg_rating), 1)

        # Add upcoming services (next 7 days)
        upcoming_services = (
            ServiceRequest.query.filter(
                ServiceRequest.customer_id == customer_id,
                ServiceRequest.status.in_(
                    [REQUEST_STATUS_CREATED, REQUEST_STATUS_ASSIGNED]
                ),
                ServiceRequest.preferred_time >= today,
                ServiceRequest.preferred_time <= today + timedelta(days=7),
            )
            .order_by(ServiceRequest.preferred_time)
            .limit(5)
            .all()
        )
        stats["upcoming_services"] = [
            {
                "id": req.id,
                "service_name": req.service.name,
                "professional_name": req.professional.user.full_name
                if req.professional
                else "Not assigned yet",
                "preferred_time": req.preferred_time.strftime("%Y-%m-%d %H:%M"),
                "status": req.status,
                "price": req.service.base_price,
            }
            for req in upcoming_services
        ]

        # Add recent completed services
        recent_services = (
            ServiceRequest.query.filter(
                ServiceRequest.customer_id == customer_id,
                ServiceRequest.status == REQUEST_STATUS_COMPLETED,
            )
            .order_by(ServiceRequest.date_of_completion.desc())
            .limit(5)
            .all()
        )
        stats["recent_services"] = [
            {
                "id": req.id,
                "service_name": req.service.name,
                "professional_name": req.professional.user.full_name
                if req.professional
                else "N/A",
                "completion_date": req.date_of_completion.strftime("%Y-%m-%d %H:%M")
                if req.date_of_completion
                else "N/A",
                "price": req.service.base_price,
                "has_review": req.review is not None,
                "rating": req.review.rating if req.review else None,
            }
            for req in recent_services
        ]

        # Add weekly trend data - requests by week
        weekly_trend = []
        if period == "all" or period == "90d":
            # For longer periods, show weekly data for past 12 weeks
            num_weeks = 12
        else:
            # For shorter periods, show daily data
            num_weeks = int(period[:-1]) // 7 or 1

        for i in range(num_weeks):
            end_date = today - timedelta(days=i * 7)
            start_date = end_date - timedelta(days=7)
            created_count = ServiceRequest.query.filter(
                ServiceRequest.customer_id == customer_id,
                ServiceRequest.date_of_request >= start_date,
                ServiceRequest.date_of_request < end_date,
            ).count()
            completed_count = ServiceRequest.query.filter(
                ServiceRequest.customer_id == customer_id,
                ServiceRequest.status == REQUEST_STATUS_COMPLETED,
                ServiceRequest.date_of_completion >= start_date,
                ServiceRequest.date_of_completion < end_date,
            ).count()
            weekly_trend.insert(
                0,
                {
                    "period": start_date.strftime("%Y-%m-%d"),
                    "requested": created_count,
                    "completed": completed_count,
                },
            )
        stats["weekly_trend"] = weekly_trend

        # Add monthly spending trend
        monthly_spending = []
        for i in range(3):  # Last 3 months
            end_date = today.replace(day=1) - timedelta(days=i * 30)
            start_date = end_date - timedelta(days=30)
            total_spent = (
                db.session.query(func.sum(Service.base_price))
                .join(ServiceRequest, ServiceRequest.service_id == Service.id)
                .filter(
                    ServiceRequest.customer_id == customer_id,
                    ServiceRequest.status == REQUEST_STATUS_COMPLETED,
                    ServiceRequest.date_of_completion >= start_date,
                    ServiceRequest.date_of_completion < end_date,
                )
                .scalar()
                or 0.0
            )
            monthly_spending.insert(
                0,
                {
                    "month": start_date.strftime("%Y-%m"),
                    "amount": round(float(total_spent), 2),
                },
            )
        stats["monthly_spending"] = monthly_spending

        # Add month-over-month comparison for spending
        current_month_start = today.replace(day=1)
        prev_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        current_month_spending = (
            db.session.query(func.sum(Service.base_price))
            .join(ServiceRequest, ServiceRequest.service_id == Service.id)
            .filter(
                ServiceRequest.customer_id == customer_id,
                ServiceRequest.status == REQUEST_STATUS_COMPLETED,
                ServiceRequest.date_of_completion >= current_month_start,
            )
            .scalar()
            or 0.0
        )
        prev_month_spending = (
            db.session.query(func.sum(Service.base_price))
            .join(ServiceRequest, ServiceRequest.service_id == Service.id)
            .filter(
                ServiceRequest.customer_id == customer_id,
                ServiceRequest.status == REQUEST_STATUS_COMPLETED,
                ServiceRequest.date_of_completion >= prev_month_start,
                ServiceRequest.date_of_completion < current_month_start,
            )
            .scalar()
            or 0.0
        )

        # Calculate month-over-month changes for spending
        if prev_month_spending > 0:
            spending_change_percent = round(
                ((current_month_spending - prev_month_spending) / prev_month_spending)
                * 100,
                1,
            )
        else:
            spending_change_percent = 100 if current_month_spending > 0 else 0

        stats["monthly_comparison"] = {
            "current_month": current_month_start.strftime("%B %Y"),
            "current_month_spending": round(float(current_month_spending), 2),
            "prev_month_spending": round(float(prev_month_spending), 2),
            "change_percent": spending_change_percent,
        }

        # Get top 5 most used services
        if start_date:
            top_services_query = (
                db.session.query(
                    ServiceRequest.service_id,
                    Service.name.label("service_name"),
                    func.count().label("count"),
                    func.sum(Service.base_price).label("total_spent"),
                )
                .join(Service, ServiceRequest.service_id == Service.id)
                .filter(
                    ServiceRequest.customer_id == customer_id,
                    ServiceRequest.date_of_request >= start_date,
                )
                .group_by(ServiceRequest.service_id, Service.name)
                .order_by(func.count().desc())
                .limit(5)
            )
            stats["top_services"] = [
                {
                    "service_name": row.service_name,
                    "count": row.count,
                    "total_spent": round(float(row.total_spent), 2),
                }
                for row in top_services_query.all()
            ]

        # This query gets distribution of service requests by service types
        service_distribution_query = (
            db.session.query(
                Service.id,
                Service.name.label("service_name"),
                func.count().label("request_count"),
                func.sum(Service.base_price).label("total_spent"),
            )
            .join(ServiceRequest, ServiceRequest.service_id == Service.id)
            .filter(
                ServiceRequest.customer_id == customer_id,
                ServiceRequest.status == REQUEST_STATUS_COMPLETED,
            )
            .group_by(Service.id, Service.name)
            .order_by(func.count().desc())
        )

        if start_date:
            service_distribution_query = service_distribution_query.filter(
                ServiceRequest.date_of_completion >= start_date
            )

        service_distribution = [
            {
                "service_id": row.id,
                "service_name": row.service_name,
                "request_count": row.request_count,
                "total_spent": round(float(row.total_spent), 2),
                "percentage": 0,  # Will calculate after getting all data
            }
            for row in service_distribution_query.all()
        ]

        # Calculate percentages for the distribution
        total_requests_count = sum(
            item["request_count"] for item in service_distribution
        )
        if total_requests_count > 0:
            for item in service_distribution:
                item["percentage"] = round(
                    (item["request_count"] / total_requests_count) * 100, 1
                )

        stats["service_distribution"] = service_distribution

        # NEW: Add favorite services (based on frequency, ratings, and recency)
        # This combines usage frequency with ratings and recency to identify customer's favorites
        favorite_services_query = (
            db.session.query(
                Service.id,
                Service.name.label("service_name"),
                func.count(ServiceRequest.id).label("usage_count"),
                func.avg(Review.rating).label("avg_rating"),
                func.max(ServiceRequest.date_of_completion).label("last_used"),
            )
            .join(ServiceRequest, ServiceRequest.service_id == Service.id)
            .outerjoin(Review, ServiceRequest.id == Review.service_request_id)
            .filter(
                ServiceRequest.customer_id == customer_id,
                ServiceRequest.status == REQUEST_STATUS_COMPLETED,
            )
            .group_by(Service.id, Service.name)
        )

        if start_date:
            favorite_services_query = favorite_services_query.filter(
                ServiceRequest.date_of_completion >= start_date
            )

        favorite_services_raw = favorite_services_query.all()

        # Calculate favorite score for each service:
        # score = (avg_rating * 0.6) + (normalized_usage * 0.25) + (recency_bonus * 0.15)
        favorite_services = []

        if favorite_services_raw:
            # Find max usage count for normalization
            max_usage = (
                max([row.usage_count for row in favorite_services_raw])
                if favorite_services_raw
                else 1
            )

            for row in favorite_services_raw:
                # Handle rating (default to 3.0 if no ratings)
                avg_rating = (
                    float(row.avg_rating) if row.avg_rating is not None else 3.0
                )

                # Normalize usage (0-1 scale)
                normalized_usage = row.usage_count / max_usage

                # Calculate recency bonus
                last_used_date = row.last_used
                if last_used_date:
                    # Ensure the last_used_date is timezone-aware
                    if last_used_date.tzinfo is None:
                        last_used_date = last_used_date.replace(tzinfo=timezone.utc)
                    days_since_used = (today - last_used_date).days
                    # Recency bonus: 1.0 if used in last 7 days, declining to 0.0 if over 60 days
                    recency_bonus = (
                        max(0, 1 - (days_since_used / 60))
                        if days_since_used <= 60
                        else 0
                    )
                else:
                    recency_bonus = 0

                # Calculate favorite score (on 0-100 scale)
                favorite_score = (
                    (avg_rating / 5 * 0.6)
                    + (normalized_usage * 0.25)
                    + (recency_bonus * 0.15)
                ) * 100

                favorite_services.append(
                    {
                        "service_id": row.id,
                        "service_name": row.service_name,
                        "usage_count": row.usage_count,
                        "avg_rating": round(avg_rating, 1),
                        "last_used": last_used_date.strftime("%Y-%m-%d")
                        if last_used_date
                        else None,
                        "favorite_score": round(favorite_score, 1),
                    }
                )

            # Sort by favorite score (highest first) and limit to top 3
            favorite_services.sort(key=lambda x: x["favorite_score"], reverse=True)
            favorite_services = favorite_services[:3]

        stats["favorite_services"] = favorite_services

        return APIResponse.success(
            data=stats, message="Customer dashboard statistics retrieved successfully"
        )
    except Exception as e:
        return APIResponse.error(
            f"Error retrieving dashboard stats: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )
