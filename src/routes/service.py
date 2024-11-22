from flask import Blueprint, request, jsonify
from src.models import Service, ProfessionalProfile
from src.schemas import service_schema, services_schema, professional_profiles_schema
from src.utils.auth import token_required, role_required, APIError
from src import db

service_bp = Blueprint("service", __name__)


# Public endpoints
@service_bp.route("/", methods=["GET"])
def list_services():
    """List all active services"""
    services = Service.query.filter_by(is_active=True).all()
    return jsonify(services_schema.dump(services)), 200


@service_bp.route("/<int:service_id>", methods=["GET"])
def get_service(service_id):
    """Get service details with available professionals"""
    service = Service.query.get_or_404(service_id)
    if not service.is_active:
        raise APIError("Service is not available", 404)

    # Get verified professionals for this service
    professionals = ProfessionalProfile.query.filter_by(
        service_type_id=service_id, is_verified=True
    ).all()

    result = service_schema.dump(service)
    result["available_professionals"] = professional_profiles_schema.dump(professionals)

    return jsonify(result), 200


@service_bp.route("/search", methods=["GET"])
def search_services():
    """Search services by name or filter by various criteria"""
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
    return jsonify(services_schema.dump(services)), 200


# Admin endpoints
@service_bp.route("/", methods=["POST"])
@token_required
@role_required("admin")
def create_service(current_user):
    """Create a new service"""
    data = request.get_json()

    errors = service_schema.validate(data)
    if errors:
        raise APIError(f"Validation error: {errors}", 400)

    # Check if service name already exists
    if Service.query.filter_by(name=data["name"]).first():
        raise APIError("Service with this name already exists", 400)

    service = Service(**data)
    db.session.add(service)
    db.session.commit()

    return jsonify(
        {
            "message": "Service created successfully",
            "service": service_schema.dump(service),
        }
    ), 201


@service_bp.route("/<int:service_id>", methods=["PUT"])
@token_required
@role_required("admin")
def update_service(current_user, service_id):
    """Update an existing service"""
    service = Service.query.get_or_404(service_id)
    data = request.get_json()

    errors = service_schema.validate(data, partial=True)
    if errors:
        raise APIError(f"Validation error: {errors}", 400)

    # Check name uniqueness if name is being updated
    if "name" in data and data["name"] != service.name:
        if Service.query.filter_by(name=data["name"]).first():
            raise APIError("Service with this name already exists", 400)

    # Update fields
    for key, value in data.items():
        setattr(service, key, value)

    db.session.commit()

    return jsonify(
        {
            "message": "Service updated successfully",
            "service": service_schema.dump(service),
        }
    ), 200


@service_bp.route("/<int:service_id>", methods=["DELETE"])
@token_required
@role_required("admin")
def delete_service(current_user, service_id):
    """Soft delete a service by marking it as inactive"""
    service = Service.query.get_or_404(service_id)

    # Check if service has active professionals
    active_professionals = ProfessionalProfile.query.filter_by(
        service_type_id=service_id, is_verified=True
    ).count()

    if active_professionals > 0:
        raise APIError(
            "Cannot delete service with active professionals. Deactivate professionals first.",
            400,
        )

    service.is_active = False
    db.session.commit()

    return jsonify({"message": "Service deleted successfully"}), 200


@service_bp.route("/<int:service_id>/restore", methods=["POST"])
@token_required
@role_required("admin")
def restore_service(current_user, service_id):
    """Restore a soft-deleted service"""
    service = Service.query.get_or_404(service_id)
    service.is_active = True
    db.session.commit()

    return jsonify(
        {
            "message": "Service restored successfully",
            "service": service_schema.dump(service),
        }
    ), 200
