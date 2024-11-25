from flask import Blueprint, request, current_app, func
from marshmallow import ValidationError
import base64
from http import HTTPStatus
import os

from src import db

from src.models import (
    User,
    ProfessionalProfile,
    ActivityLog,
    ServiceRequest,
    Service,
    Review,
)

from src.constants import ActivityLogActions, USER_ROLE_PROFESSIONAL

from src.schemas.professional import (
    professional_output_schema,
    professionals_list_query_schema,
    professional_register_schema,
)
from src.schemas.user import block_user_schema

from src.utils.auth import token_required, role_required
from src.utils.api import APIResponse
from src.utils.file import (
    save_verification_document,
    delete_verification_document,
    UPLOAD_FOLDER,
)
from src.utils.user import check_existing_user


professional_bp = Blueprint("professional", __name__)


@professional_bp.route("/register/professional", methods=["POST"])
def register_professional():
    """Register a new professional"""
    if "verification_document" not in request.files:
        return APIResponse.error(
            "Verification document is required",
            HTTPStatus.BAD_REQUEST,
            "MissingDocument",
        )

    try:
        form_data = {
            "username": request.form.get("username"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
            "full_name": request.form.get("full_name"),
            "phone": request.form.get("phone"),
            "address": request.form.get("address"),
            "pin_code": request.form.get("pin_code"),
            "service_type_id": int(request.form.get("service_type_id")),
            "experience_years": int(request.form.get("experience_years")),
            "description": request.form.get("description"),
        }
    except (TypeError, ValueError):
        return APIResponse.error(
            "Invalid service_type_id or experience_years",
            HTTPStatus.BAD_REQUEST,
            "ValidationError",
        )

    try:
        data = professional_register_schema.load(form_data)
    except ValidationError as err:
        return APIResponse.error(str(err.messages))

    exists, error_response = check_existing_user(data["username"], data["email"])
    if exists:
        return error_response

    filename, error = save_verification_document(request.files["verification_document"])
    if error:
        return APIResponse.error(error, HTTPStatus.BAD_REQUEST, "FileUploadError")

    try:
        user = User(
            username=data["username"],
            email=data["email"],
            full_name=data["full_name"],
            phone=data["phone"],
            address=data["address"],
            pin_code=data["pin_code"],
            role=USER_ROLE_PROFESSIONAL,
            is_active=False,
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.flush()  # Get user.id

        profile = ProfessionalProfile(
            user_id=user.id,
            service_type_id=data["service_type_id"],
            experience_years=data["experience_years"],
            description=data["description"],
            verification_documents=filename,
            is_verified=False,
        )
        db.session.add(profile)

        log = ActivityLog(
            user_id=user.id,
            action=ActivityLogActions.USER_REGISTER,
            description=f"New professional account created for {user.username}, pending verification",
        )
        db.session.add(log)
        db.session.commit()

        # Query the user again to get the relationship loaded
        user = User.query.get(user.id)
        return APIResponse.success(
            data=professional_output_schema.dump(user),
            message="Professional registered successfully. Account will be activated after verification.",
            status_code=HTTPStatus.CREATED,
        )
    except Exception as e:
        if filename:
            delete_verification_document(filename)
        return APIResponse.error(
            f"Error creating professional: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@professional_bp.route("/professionals", methods=["GET"])
@professional_bp.route("/professionals/<int:profile_id>", methods=["GET"])
@token_required
@role_required("admin", "customer")
def list_professionals(current_user, profile_id=None):
    try:
        if profile_id is not None:
            # Single professional retrieval - get the User object with joined profile
            user = (
                User.query.join(ProfessionalProfile)
                .filter(ProfessionalProfile.id == profile_id)
                .first_or_404()
            )

            # Check visibility based on role
            if current_user.role != "admin":
                if not user.professional_profile.is_verified or not user.is_active:
                    return APIResponse.error(
                        "Professional not found", HTTPStatus.NOT_FOUND, "NotFound"
                    )

            prof_data = professional_output_schema.dump(user)

            # For admin users, include verification document
            if (
                current_user.role == "admin"
                and user.professional_profile.verification_documents
            ):
                try:
                    with open(
                        os.path.join(
                            current_app.root_path,
                            UPLOAD_FOLDER,
                            user.professional_profile.verification_documents,
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
        query = User.query.join(ProfessionalProfile)

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
        for user in paginated.items:
            prof_data = professional_output_schema.dump(user)
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


@professional_bp.route("/professionals/<int:profile_id>/verify", methods=["POST"])
@token_required
@role_required("admin")
def verify_professional(current_user, profile_id):
    """Verify a professional's profile"""
    try:
        profile = ProfessionalProfile.query.get_or_404(profile_id)
        user = User.query.get(profile.user_id)

        if profile.is_verified:
            return APIResponse.error(
                "Professional is already verified",
                HTTPStatus.CONFLICT,
                "AlreadyVerified",
            )

        profile.is_verified = True
        user.is_active = True

        log = ActivityLog(
            user_id=current_user.id,
            entity_id=user.id,
            action=ActivityLogActions.PROFESSIONAL_VERIFY,
            description=f"Verified professional profile for {user.full_name}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(
            data=professional_output_schema.dump(user),
            message="Professional verified successfully",
        )
    except Exception as e:
        return APIResponse.error(
            f"Error verifying professional: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@professional_bp.route("/professionals/<int:profile_id>/block", methods=["POST"])
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


@professional_bp.route("/professionals/document", methods=["PUT"])
@token_required
@role_required("professional")
def update_verification_document(current_user):
    """Update professional's verification documents"""
    try:
        # Check for active service requests first
        has_active_requests = (
            ServiceRequest.query.filter(
                ServiceRequest.professional_id == current_user.professional_profile.id,
                ServiceRequest.status.in_(["assigned", "in_progress"]),
            ).first()
            is not None
        )

        if has_active_requests:
            return APIResponse.error(
                "Cannot update verification documents while having active service requests",
                HTTPStatus.CONFLICT,
                "ActiveRequestsExist",
            )

        if "verification_document" not in request.files:
            return APIResponse.error(
                "No document provided", HTTPStatus.BAD_REQUEST, "MissingDocument"
            )

        # Delete old document if it exists
        if current_user.professional_profile.verification_documents:
            delete_verification_document(
                current_user.professional_profile.verification_documents
            )

        # Save new document
        filename, error = save_verification_document(
            request.files["verification_document"]
        )
        if error:
            return APIResponse.error(error, HTTPStatus.BAD_REQUEST, "FileUploadError")

        # Update profile and set verification status
        current_user.professional_profile.verification_documents = filename
        current_user.professional_profile.is_verified = (
            False  # Reset verification status
        )

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.PROFESSIONAL_DOCUMENT_UPDATE,
            description=f"Updated verification documents for professional {current_user.username}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(
            data=professional_output_schema.dump(current_user),
            message="Verification document updated successfully. Awaiting verification.",
        )
    except Exception as e:
        # Clean up the newly uploaded file in case of error
        if "filename" in locals() and filename:
            delete_verification_document(filename)
        return APIResponse.error(
            f"Error updating document: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@professional_bp.route("/professionals/service", methods=["PUT"])
@token_required
@role_required("professional")
def update_service_type(current_user):
    """Update professional's service type"""
    try:
        data = request.get_json()
        if not data or "service_type_id" not in data:
            return APIResponse.error(
                "Service type ID is required", HTTPStatus.BAD_REQUEST, "MissingField"
            )

        # Check for active service requests
        has_active_requests = (
            ServiceRequest.query.filter(
                ServiceRequest.professional_id == current_user.professional_profile.id,
                ServiceRequest.status.in_(["assigned", "in_progress"]),
            ).first()
            is not None
        )

        if has_active_requests:
            return APIResponse.error(
                "Cannot change service type while having active requests",
                HTTPStatus.CONFLICT,
                "ActiveRequestsExist",
            )

        # Verify service exists and is active
        service = Service.query.get_or_404(data["service_type_id"])
        if not service.is_active:
            return APIResponse.error(
                "Selected service is not active",
                HTTPStatus.BAD_REQUEST,
                "InactiveService",
            )

        # Check if it's the same service type
        if current_user.professional_profile.service_type_id == service.id:
            return APIResponse.error(
                "Already assigned to this service type",
                HTTPStatus.BAD_REQUEST,
                "SameService",
            )

        current_user.professional_profile.service_type_id = service.id
        current_user.professional_profile.is_verified = (
            False  # Reset verification status
        )

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.PROFESSIONAL_PROFILE_UPDATE,
            entity_id=current_user.id,
            description=f"Updated service type for professional {current_user.username} from "
            f"{current_user.professional_profile.service_type.name} to {service.name}",
        )
        db.session.add(log)
        db.session.commit()

        return APIResponse.success(
            data=professional_output_schema.dump(current_user),
            message="Service type updated successfully. Awaiting verification.",
        )
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(
            f"Error updating service type: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@professional_bp.route("/professionals/dashboard", methods=["GET"])
@token_required
@role_required("professional")
def get_professional_dashboard(current_user):
    """Get professional's dashboard statistics"""
    try:
        professional_id = current_user.professional_profile.id

        stats = {
            "total_requests": ServiceRequest.query.filter_by(
                professional_id=professional_id
            ).count(),
            "completed_requests": ServiceRequest.query.filter_by(
                professional_id=professional_id, status="completed"
            ).count(),
            "active_requests": ServiceRequest.query.filter(
                ServiceRequest.professional_id == professional_id,
                ServiceRequest.status.in_(["assigned", "in_progress"]),
            ).count(),
            "average_rating": db.session.query(func.avg(Review.rating))
            .join(ServiceRequest)
            .filter(ServiceRequest.professional_id == professional_id)
            .scalar()
            or 0.0,
            "total_reviews": Review.query.join(ServiceRequest)
            .filter(ServiceRequest.professional_id == professional_id)
            .count(),
            "reported_reviews": Review.query.join(ServiceRequest)
            .filter(
                ServiceRequest.professional_id == professional_id,
                Review.is_reported == True,  # noqa: E712
            )
            .count(),
            # Additional useful statistics
            "service_type": current_user.professional_profile.service_type.name,
            "verification_status": "Verified"
            if current_user.professional_profile.is_verified
            else "Pending Verification",
        }

        return APIResponse.success(
            data=stats, message="Dashboard statistics retrieved successfully"
        )
    except Exception as e:
        return APIResponse.error(
            f"Error retrieving dashboard stats: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@professional_bp.route("/professionals/reviews", methods=["GET"])
@token_required
@role_required("professional")
def get_professional_reviews(current_user):
    """Get reviews for the logged-in professional"""
    try:
        # Apply pagination
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        professional_id = current_user.professional_profile.id

        # Base query
        query = (
            Review.query.join(ServiceRequest)
            .filter(ServiceRequest.professional_id == professional_id)
            .order_by(Review.created_at.desc())
        )

        is_reported = request.args.get("reported", type=bool)
        if is_reported is not None:
            query = query.filter(Review.is_reported == is_reported)

        # Execute paginated query
        try:
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        except Exception as e:
            return APIResponse.error(
                f"Pagination error: {str(e)}", HTTPStatus.BAD_REQUEST, "PaginationError"
            )

        # Format the reviews
        reviews = []
        for review in paginated.items:
            review_data = {
                "id": review.id,
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at,
                "is_reported": review.is_reported,
                "report_reason": review.report_reason,
                "service_request": {
                    "id": review.service_request.id,
                    "date_of_completion": review.service_request.date_of_completion,
                    "service_name": review.service_request.service.name,
                    "customer_name": review.service_request.customer.user.full_name,
                },
            }
            reviews.append(review_data)

        return APIResponse.success(
            data=reviews,
            message="Reviews retrieved successfully",
            pagination={
                "total": paginated.total,
                "pages": paginated.pages,
                "current_page": paginated.page,
                "per_page": paginated.per_page,
                "has_next": paginated.has_next,
                "has_prev": paginated.has_prev,
            },
        )
    except Exception as e:
        return APIResponse.error(
            f"Error retrieving reviews: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )
