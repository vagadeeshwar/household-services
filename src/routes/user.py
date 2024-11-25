from flask import Blueprint, request
from marshmallow import ValidationError
from http import HTTPStatus
from src.models import (
    User,
    ProfessionalProfile,
    CustomerProfile,
)
from src.schemas import (
    professionals_list_query_schema,
    customers_list_query_schema,
    combine_professional_data,
)
from src.utils.auth import token_required, role_required
from src.utils.api import APIResponse

user_bp = Blueprint("user", __name__)


@user_bp.route("/professionals", methods=["GET"])
@token_required
@role_required("admin")
def list_professionals(current_user):
    """List all professionals with optional filters and pagination"""
    try:
        params = professionals_list_query_schema.load(request.args)

        # Use joinedload for optimization
        query = ProfessionalProfile.query.join(User)

        if params.get("verified") is not None:
            query = query.filter(ProfessionalProfile.is_verified == params["verified"])
        if params.get("service_type"):
            query = query.filter(
                ProfessionalProfile.service_type_id == params["service_type"]
            )

        paginated = query.paginate(
            page=params["page"], per_page=params["per_page"], error_out=False
        )

        # Create flat professional objects with all necessary data
        professionals = [
            combine_professional_data(profile.user, profile)
            for profile in paginated.items
        ]

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


@user_bp.route("/customers", methods=["GET"])
@token_required
@role_required("admin")
def list_customers(current_user):
    """List all customers with optional filters and pagination"""
    try:
        params = customers_list_query_schema.load(request.args)

        # Optimize query with join
        query = CustomerProfile.query.join(User)

        if params.get("active") is not None:
            query = query.filter(User.is_active == params["active"])

        paginated = query.paginate(
            page=params["page"], per_page=params["per_page"], error_out=False
        )

        # Create flat customer objects
        customers = []
        for profile in paginated.items:
            customer_data = {
                # User data
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
                # Customer profile specific data
                "profile_id": profile.id,
                # Add any other customer-specific fields here
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
