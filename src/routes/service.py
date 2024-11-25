from flask import Blueprint, request
from marshmallow import ValidationError
from http import HTTPStatus
from src.models import Service, ProfessionalProfile, ActivityLog
from src.schemas import (
    service_schema,
    services_schema,
    professional_profiles_schema,
    service_input_schema,
)
from src.utils.auth import token_required, role_required
from src.utils.api import APIResponse
from src.constants import ActivityLogActions
from src import db

service_bp = Blueprint("service", __name__)


@service_bp.route("/", methods=["GET"])
@token_required
def list_services():
    """List all active services"""
    try:
        services = Service.query.filter_by(is_active=True).all()
        return APIResponse.success(
            data=services_schema.dump(services),
            message="Services retrieved successfully",
        )
    except Exception as e:
        return APIResponse.error(
            f"Error retrieving services: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@service_bp.route("/<int:service_id>", methods=["GET"])
def get_service(service_id):
    """Get service details with available professionals"""
    try:
        service = Service.query.get_or_404(service_id)
        if not service.is_active:
            return APIResponse.error(
                "Service is not available",
                HTTPStatus.NOT_FOUND,
                "ServiceNotAvailable",
            )

        # Get verified professionals for this service
        professionals = ProfessionalProfile.query.filter_by(
            service_type_id=service_id,
            is_verified=True,
        ).all()

        result = service_schema.dump(service)
        result["available_professionals"] = professional_profiles_schema.dump(
            professionals
        )

        return APIResponse.success(
            data=result,
            message="Service details retrieved successfully",
        )
    except Exception as e:
        return APIResponse.error(
            f"Error retrieving service details: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@service_bp.route("/search", methods=["GET"])
def search_services():
    """Search services by name or filter by various criteria"""
    try:
        name = request.args.get("name", "").lower()
        min_price = request.args.get("min_price", type=float)
        max_price = request.args.get("max_price", type=float)

        query = Service.query.filter_by(is_active=True)

        if name:
            query = query.filter(Service.name.ilike(f"%{name}%"))
        if min_price is not None:
            query = query.filter(Service.base_price >= min_price)
        if max_price is not None:
            query = query.filter(Service.base_price <= max_price)

        services = query.all()
        return APIResponse.success(
            data=services_schema.dump(services),
            message="Services search completed successfully",
        )
    except Exception as e:
        return APIResponse.error(
            f"Error searching services: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@service_bp.route("/", methods=["POST"])
@token_required
@role_required("admin")
def create_service(current_user):
    """Create a new service"""
    try:
        data = service_input_schema.load(request.get_json())

        # Check if service name already exists
        if Service.query.filter_by(name=data["name"]).first():
            return APIResponse.error(
                "Service with this name already exists",
                HTTPStatus.CONFLICT,
                "DuplicateService",
            )

        service = Service(**data)
        db.session.add(service)

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.SERVICE_CREATE,
            description=f"Created new service: {service.name}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(
            data=service_schema.dump(service),
            message="Service created successfully",
            status_code=HTTPStatus.CREATED,
        )
    except ValidationError as err:
        return APIResponse.error(str(err.messages))
    except Exception as e:
        return APIResponse.error(
            f"Error creating service: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@service_bp.route("/<int:service_id>", methods=["PUT"])
@token_required
@role_required("admin")
def update_service(current_user, service_id):
    """Update an existing service"""
    try:
        service = Service.query.get_or_404(service_id)
        data = service_input_schema.load(request.get_json(), partial=True)

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
            data=service_schema.dump(service),
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


@service_bp.route("/<int:service_id>", methods=["DELETE"])
@token_required
@role_required("admin")
def delete_service(current_user, service_id):
    """Soft delete a service by marking it as inactive"""
    try:
        service = Service.query.get_or_404(service_id)

        # Check if service has active professionals
        active_professionals = ProfessionalProfile.query.filter_by(
            service_type_id=service_id,
            is_verified=True,
        ).count()

        if active_professionals > 0:
            return APIResponse.error(
                "Cannot delete service with active professionals. Deactivate professionals first.",
                HTTPStatus.CONFLICT,
                "ActiveProfessionalsExist",
            )

        service.is_active = False

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.SERVICE_DELETE,
            entity_id=service_id,
            description=f"Deleted service: {service.name}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(message="Service deleted successfully")
    except Exception as e:
        return APIResponse.error(
            f"Error deleting service: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@service_bp.route("/<int:service_id>/restore", methods=["POST"])
@token_required
@role_required("admin")
def restore_service(current_user, service_id):
    """Restore a soft-deleted service"""
    try:
        service = Service.query.get_or_404(service_id)
        service.is_active = True

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.SERVICE_RESTORE,
            entity_id=service_id,
            description=f"Restored service: {service.name}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(
            data=service_schema.dump(service),
            message="Service restored successfully",
        )
    except Exception as e:
        return APIResponse.error(
            f"Error restoring service: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )
