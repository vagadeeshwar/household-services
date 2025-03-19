from http import HTTPStatus

from flask import Blueprint, request
from marshmallow import ValidationError

from src import db
from src.constants import USER_ROLE_CUSTOMER, ActivityLogActions
from src.models import (
    ActivityLog,
    CustomerProfile,
    User,
)
from src.schemas.customer import (
    customer_output_schema,
    customer_query_schema,
    customer_register_schema,
    customers_output_schema,
)
from src.schemas.user import block_user_schema
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
