from flask import Blueprint
from marshmallow import ValidationError
from http import HTTPStatus

from src.models import (
    User,
    ProfessionalProfile,
    CustomerProfile,
    ServiceRequest,
    Review,
)

from src.constants import REQUEST_STATUS_CREATED, REQUEST_STATUS_COMPLETED

from src.schemas.admin import (
    dashboard_stats_schema,
)

from src.utils.auth import token_required, role_required
from src.utils.api import APIResponse

admin_bp = Blueprint("admin", __name__)


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
                "pending": ServiceRequest.query.filter_by(
                    status=REQUEST_STATUS_CREATED
                ).count(),
                "completed": ServiceRequest.query.filter_by(
                    status=REQUEST_STATUS_COMPLETED
                ).count(),
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
