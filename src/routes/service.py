from flask import Blueprint, request
from marshmallow import ValidationError
from http import HTTPStatus

from src import db

from src.models import Service, ProfessionalProfile, ActivityLog, User

from src.constants import ActivityLogActions

from src.schemas.service import (
    service_output_schema,
    service_input_schema,
    services_list_query_schema,
    service_update_schema,
)


from src.utils.auth import token_required, role_required
from src.utils.api import APIResponse

service_bp = Blueprint("service", __name__)


@service_bp.route("/services", methods=["POST"])
@token_required
@role_required("admin")
def create_service(current_user):
    """Create a new service"""
    try:
        data = service_input_schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(str(err.messages))

    # Check if service name already exists
    if Service.query.filter_by(name=data["name"]).first():
        return APIResponse.error(
            "Service with this name already exists",
            HTTPStatus.CONFLICT,
            "DuplicateService",
        )

    try:
        service = Service(
            name=data["name"],
            description=data["description"],
            base_price=data["base_price"],
            duration_minutes=data["duration_minutes"],
            is_active=True,
        )
        db.session.add(service)
        db.session.flush()

        log = ActivityLog(
            user_id=current_user.id,
            entity_id=service.id,
            action=ActivityLogActions.SERVICE_CREATE,
            description=f"Created new service: {service.name}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(
            data=service_output_schema.dump(service),
            message="Service created successfully",
            status_code=HTTPStatus.CREATED,
        )
    except Exception as e:
        return APIResponse.error(
            f"Error creating service: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@service_bp.route("/services", methods=["GET"])
@service_bp.route("/services/<int:service_id>", methods=["GET"])
@token_required
def list_services(current_user, service_id=None):
    """List all services or get a specific service"""
    try:
        if service_id is not None:
            # Single service retrieval
            service = Service.query.get_or_404(service_id)

            # If not admin, only return active services
            if current_user.role != "admin" and not service.is_active:
                return APIResponse.error(
                    "Service not found", HTTPStatus.NOT_FOUND, "NotFound"
                )

            return APIResponse.success(
                data=service_output_schema.dump(service),
                message="Service retrieved successfully",
            )

        # List services with filtering and pagination
        params = services_list_query_schema.load(request.args)
        query = Service.query

        # Non-admin users can only see active services
        if current_user.role != "admin":
            query = query.filter_by(is_active=True)
        elif params.get("is_active") is not None:
            query = query.filter_by(is_active=params["is_active"])

        # Apply pagination
        paginated = query.paginate(
            page=params["page"], per_page=params["per_page"], error_out=False
        )

        services = []

        for service in paginated.items:
            service_data = service_output_schema.dump(service)
            services.append(service_data)

        return APIResponse.success(
            data=services,
            message="Services retrieved successfully",
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
            f"Error retrieving services: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@service_bp.route("/services/<int:service_id>", methods=["PUT"])
@token_required
@role_required("admin")
def update_service(current_user, service_id):
    """Update an existing service"""
    try:
        service = Service.query.get_or_404(service_id)
        data = service_update_schema.load(request.get_json(), partial=True)

        # Check name uniqueness if name is being updated
        if "name" in data and data["name"] != service.name:
            if Service.query.filter_by(name=data["name"]).first():
                return APIResponse.error(
                    "Service with this name already exists",
                    HTTPStatus.CONFLICT,
                    "DuplicateService",
                )

        # Update fields
        for key, value in data.items():
            setattr(service, key, value)

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.SERVICE_UPDATE,
            entity_id=service_id,
            description=f"Updated service: {service.name}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(
            data=service_output_schema.dump(service),
            message="Service updated successfully",
        )
    except ValidationError as err:
        return APIResponse.error(str(err.messages))
    except Exception as e:
        return APIResponse.error(
            f"Error updating service: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@service_bp.route("/services/<int:service_id>/toggle", methods=["POST"])
@token_required
@role_required("admin")
def toggle_service(current_user, service_id):
    """Toggle service active status"""
    try:
        service = Service.query.get_or_404(service_id)

        # If deactivating, check for active professionals
        if service.is_active:
            active_professionals = (
                ProfessionalProfile.query.join(User)
                .filter(
                    ProfessionalProfile.service_type_id == service_id,
                    ProfessionalProfile.is_verified == True,  # noqa: E712
                    User.is_active == True,  # noqa: E712
                )
                .count()
            )

            if active_professionals > 0:
                return APIResponse.error(
                    "Cannot deactivate service with active professionals",
                    HTTPStatus.CONFLICT,
                    "ActiveProfessionalsExist",
                )

        # Toggle status
        service.is_active = not service.is_active
        action = (
            ActivityLogActions.SERVICE_DELETE
            if not service.is_active
            else ActivityLogActions.SERVICE_RESTORE
        )

        log = ActivityLog(
            user_id=current_user.id,
            action=action,
            entity_id=service_id,
            description=f"{'Deactivated' if not service.is_active else 'Activated'} service: {service.name}",
        )
        db.session.add(log)
        db.session.commit()

        message = (
            "Service deactivated successfully"
            if not service.is_active
            else "Service activated successfully"
        )
        return APIResponse.success(
            data=service_output_schema.dump(service), message=message
        )
    except Exception as e:
        return APIResponse.error(
            f"Error toggling service status: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@service_bp.route("/services/<int:service_id>", methods=["DELETE"])
@token_required
@role_required("admin")
def delete_service(current_user, service_id):
    """Permanently delete a service that has never been used"""
    try:
        service = Service.query.get_or_404(service_id)

        # Check if service has ever been assigned to any professional
        has_professionals = (
            ProfessionalProfile.query.filter_by(service_type_id=service_id).first()
            is not None
        )

        if has_professionals:
            return APIResponse.error(
                "Cannot delete service that has been assigned to professionals. Use deactivate instead.",
                HTTPStatus.CONFLICT,
                "ServiceInUse",
            )

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.SERVICE_DELETE,
            entity_id=service_id,
            description=f"Permanently deleted service: {service.name}",
        )
        db.session.add(log)

        db.session.delete(service)
        db.session.commit()

        return APIResponse.success(
            message="Service permanently deleted successfully",
            status_code=HTTPStatus.OK,
        )
    except Exception as e:
        return APIResponse.error(
            f"Error deleting service: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )
