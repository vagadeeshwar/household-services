from flask import Blueprint, request, current_app
from marshmallow import ValidationError
import base64
from http import HTTPStatus
from src.models import (
    User,
    ProfessionalProfile,
    CustomerProfile,
    ServiceRequest,
    Review,
    ActivityLog,
)
import os
from src.schemas import (
    customers_list_query_schema,
    block_user_schema,
    dashboard_stats_schema,
    combine_professional_data,
    professionals_list_query_schema,
)
from src.utils.auth import token_required, role_required
from src.utils.api import APIResponse
from src.utils.file import UPLOAD_FOLDER
from src.constants import ActivityLogActions
from src import db

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/professionals", methods=["GET"])
@admin_bp.route("/professionals/<int:profile_id>", methods=["GET"])
@token_required
@role_required("admin", "customer")
def list_professionals(current_user, profile_id=None):
    """
    List all professionals or get a specific professional by ID
    Accessible by both admins and customers with role-specific behavior
    """
    try:
        if profile_id is not None:
            # Single professional retrieval
            profile = (
                ProfessionalProfile.query.join(User)
                .filter(ProfessionalProfile.id == profile_id)
                .first_or_404()
            )

            # Check visibility based on role
            if current_user.role != "admin":
                if not profile.is_verified or not profile.user.is_active:
                    return APIResponse.error(
                        "Professional not found", HTTPStatus.NOT_FOUND, "NotFound"
                    )

            prof_data = combine_professional_data(profile.user, profile)

            # For admin users requesting specific profile, include the verification document content
            if current_user.role == "admin" and profile.verification_documents:
                try:
                    with open(
                        os.path.join(
                            current_app.root_path,
                            UPLOAD_FOLDER,
                            profile.verification_documents,
                        ),
                        "rb",
                    ) as f:
                        verification_doc = base64.b64encode(f.read()).decode("utf-8")
                        prof_data["verification_document_content"] = verification_doc
                except Exception as e:
                    current_app.logger.error(
                        f"Error reading verification document: {str(e)}"
                    )
                    prof_data["verification_document_content"] = None

            # Remove sensitive information for non-admin users
            elif current_user.role != "admin":
                sensitive_fields = [
                    "verification_documents",
                    "created_at",
                    "last_login",
                ]
                for field in sensitive_fields:
                    prof_data.pop(field, None)

            return APIResponse.success(
                data=prof_data,
                message="Professional retrieved successfully",
            )

        # List all professionals
        params = professionals_list_query_schema.load(request.args)
        query = ProfessionalProfile.query.join(User)

        # Apply role-specific filters
        if current_user.role != "admin":
            query = query.filter(
                ProfessionalProfile.is_verified == True,  # noqa: E712
                User.is_active == True,  # noqa: E712
            )
        else:
            if params.get("verified") is not None:
                query = query.filter(
                    ProfessionalProfile.is_verified == params["verified"]
                )

        # Common filters
        if params.get("service_type"):
            query = query.filter(
                ProfessionalProfile.service_type_id == params["service_type"]
            )

        # Pagination
        paginated = query.paginate(
            page=params["page"], per_page=params["per_page"], error_out=False
        )

        professionals = []
        for profile in paginated.items:
            prof_data = combine_professional_data(profile.user, profile)
            if current_user.role != "admin":
                sensitive_fields = [
                    "verification_documents",
                    "created_at",
                    "last_login",
                ]
                for field in sensitive_fields:
                    prof_data.pop(field, None)
            professionals.append(prof_data)

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


@admin_bp.route("/customers", methods=["GET"])
@admin_bp.route("/customers/<int:profile_id>", methods=["GET"])
@token_required
@role_required("admin")
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

            customer_data = {
                "id": profile.user.id,
                "username": profile.user.username,
                "email": profile.user.email,
                "full_name": profile.user.full_name,
                "phone": profile.user.phone,
                "address": profile.user.address,
                "pin_code": profile.user.pin_code,
                "is_active": profile.user.is_active,
                "created_at": profile.user.created_at,
                "last_login": profile.user.last_login,
                "profile_id": profile.id,
            }

            return APIResponse.success(
                data=customer_data,
                message="Customer retrieved successfully",
            )

        # List all customers
        params = customers_list_query_schema.load(request.args)
        query = CustomerProfile.query.join(User)

        if params.get("active") is not None:
            query = query.filter(User.is_active == params["active"])
        if params.get("pin_code"):
            query = query.filter(User.pin_code == params["pin_code"])

        paginated = query.paginate(
            page=params["page"], per_page=params["per_page"], error_out=False
        )

        customers = []
        for profile in paginated.items:
            customer_data = {
                "id": profile.user.id,
                "username": profile.user.username,
                "email": profile.user.email,
                "full_name": profile.user.full_name,
                "phone": profile.user.phone,
                "address": profile.user.address,
                "pin_code": profile.user.pin_code,
                "is_active": profile.user.is_active,
                "created_at": profile.user.created_at,
                "last_login": profile.user.last_login,
                "profile_id": profile.id,
            }
            customers.append(customer_data)

        return APIResponse.success(
            data=customers,
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
            entity_id=profile.user.id,
            action=ActivityLogActions.PROFESSIONAL_VERIFY,
            description=f"Verified professional profile for {profile.user.full_name}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(
            data=combine_professional_data(profile.user, profile),
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
            entity_id=profile.user.id,
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
            entity_id=profile.user.id,
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
