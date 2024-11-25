from flask import Blueprint, request
from marshmallow import ValidationError
from http import HTTPStatus
from src.models import (
    User,
    ProfessionalProfile,
    CustomerProfile,
    ServiceRequest,
    Review,
    ActivityLog,
)
from src.schemas import (
    professionals_list_query_schema,
    customers_list_query_schema,
    block_user_schema,
    review_action_schema,
    dashboard_stats_schema,
    professional_profile_schema,
    combine_professional_data,
    customer_profiles_schema,
    reviews_schema,
)
from src.utils.auth import token_required, role_required
from src.utils.api import APIResponse
from src.constants import ActivityLogActions
from src import db

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/professionals", methods=["GET"])
@token_required
@role_required("admin")
def list_professionals(current_user):
    """List all professionals with optional filters and pagination"""
    try:
        params = professionals_list_query_schema.load(request.args)

        query = ProfessionalProfile.query

        if params.get("verified") is not None:
            query = query.filter_by(is_verified=params["verified"])
        if params.get("service_type"):
            query = query.filter_by(service_type_id=params["service_type"])

        paginated = query.paginate(
            page=params["page"], per_page=params["per_page"], error_out=False
        )

        professionals = []
        for profile in paginated.items:
            professionals.append(combine_professional_data(profile.user, profile))

        return APIResponse.success(
            data=professionals,
            message="Professionals retrieved successfully",
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
            f"Error retrieving professionals: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@admin_bp.route("/professionals/<int:profile_id>/verify", methods=["POST"])
@token_required
@role_required("admin")
def verify_professional(current_user, profile_id):
    """Verify a professional's profile"""
    try:
        profile = ProfessionalProfile.query.get_or_404(profile_id)

        if profile.is_verified:
            return APIResponse.error(
                "Professional is already verified",
                HTTPStatus.CONFLICT,
                "AlreadyVerified",
            )

        profile.is_verified = True
        profile.user.is_active = True

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.PROFESSIONAL_VERIFY,
            description=f"Verified professional profile for {profile.user.full_name}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(
            data=professional_profile_schema.dump(profile),
            message="Professional verified successfully",
        )
    except Exception as e:
        return APIResponse.error(
            f"Error verifying professional: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@admin_bp.route("/professionals/<int:profile_id>/block", methods=["POST"])
@token_required
@role_required("admin")
def block_professional(current_user, profile_id):
    """Block a professional's account"""
    try:
        data = block_user_schema.load(request.get_json())
        profile = ProfessionalProfile.query.get_or_404(profile_id)

        if not profile.user.is_active:
            return APIResponse.error(
                "Professional is already blocked", HTTPStatus.CONFLICT, "AlreadyBlocked"
            )

        profile.user.is_active = False

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.PROFESSIONAL_BLOCK,
            description=f"Blocked professional {profile.user.full_name}. Reason: {data['reason']}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(message="Professional blocked successfully")
    except ValidationError as err:
        return APIResponse.error(str(err.messages))
    except Exception as e:
        return APIResponse.error(
            f"Error blocking professional: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@admin_bp.route("/customers", methods=["GET"])
@token_required
@role_required("admin")
def list_customers(current_user):
    """List all customers with optional filters and pagination"""
    try:
        params = customers_list_query_schema.load(request.args)

        query = CustomerProfile.query

        if params.get("active") is not None:
            query = query.join(User).filter(User.is_active == params["active"])
        if params.get("pin_code"):
            query = query.join(User).filter(User.pin_code == params["pin_code"])

        paginated = query.paginate(
            page=params["page"], per_page=params["per_page"], error_out=False
        )

        return APIResponse.success(
            data=customer_profiles_schema.dump(paginated.items),
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


@admin_bp.route("/customers/<int:profile_id>/block", methods=["POST"])
@token_required
@role_required("admin")
def block_customer(current_user, profile_id):
    """Block a customer's account"""
    try:
        data = block_user_schema.load(request.get_json())
        profile = CustomerProfile.query.get_or_404(profile_id)

        if not profile.user.is_active:
            return APIResponse.error(
                "Customer is already blocked", HTTPStatus.CONFLICT, "AlreadyBlocked"
            )

        profile.user.is_active = False

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.CUSTOMER_BLOCK,
            description=f"Blocked customer {profile.user.full_name}. Reason: {data['reason']}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(message="Customer blocked successfully")
    except ValidationError as err:
        return APIResponse.error(str(err.messages))
    except Exception as e:
        return APIResponse.error(
            f"Error blocking customer: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@admin_bp.route("/reviews/reported", methods=["GET"])
@token_required
@role_required("admin")
def list_reported_reviews(current_user):
    """List all reported reviews with pagination"""
    try:
        params = customers_list_query_schema.load(request.args)

        paginated = Review.query.filter_by(is_reported=True).paginate(
            page=params["page"], per_page=params["per_page"], error_out=False
        )

        return APIResponse.success(
            data=reviews_schema.dump(paginated.items),
            message="Reported reviews retrieved successfully",
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
            f"Error retrieving reported reviews: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@admin_bp.route("/reviews/<int:review_id>/handle-report", methods=["POST"])
@token_required
@role_required("admin")
def handle_review_report(current_user, review_id):
    """Handle a reported review"""
    try:
        data = review_action_schema.load(request.get_json())
        review = Review.query.get_or_404(review_id)

        if not review.is_reported:
            return APIResponse.error(
                "Review is not reported", HTTPStatus.CONFLICT, "NotReported"
            )

        if data["action"] == "dismiss":
            review.is_reported = False
            action_type = ActivityLogActions.REVIEW_DISMISS
            message = "Review report dismissed"
        else:  # remove
            db.session.delete(review)
            action_type = ActivityLogActions.REVIEW_REMOVE
            message = "Review removed"

        log = ActivityLog(
            user_id=current_user.id,
            action=action_type,
            description=f"{message} for service request {review.service_request_id}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(message=message)
    except ValidationError as err:
        return APIResponse.error(str(err.messages))
    except Exception as e:
        return APIResponse.error(
            f"Error handling review report: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@admin_bp.route("/dashboard/stats", methods=["GET"])
@token_required
@role_required("admin")
def get_dashboard_stats(current_user):
    """Get statistics for admin dashboard"""
    try:
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
                "pending": ServiceRequest.query.filter_by(status="requested").count(),
                "in_progress": ServiceRequest.query.filter_by(
                    status="in_progress"
                ).count(),
                "completed": ServiceRequest.query.filter_by(status="completed").count(),
            },
        }

        validated_stats = dashboard_stats_schema.dump(stats)
        return APIResponse.success(
            data=validated_stats, message="Dashboard statistics retrieved successfully"
        )
    except ValidationError as err:
        return APIResponse.error(str(err.messages))
    except Exception as e:
        return APIResponse.error(
            f"Error retrieving dashboard statistics: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )
