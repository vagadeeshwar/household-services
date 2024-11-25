from flask import Blueprint, request, current_app
from marshmallow import ValidationError
import base64
from http import HTTPStatus
import os

from src import db

from src.models import (
    User,
    ProfessionalProfile,
    ActivityLog,
)

from src.constants import ActivityLogActions, USER_ROLE_PROFESSIONAL

from src.schemas.professional import (
    combine_professional_data,
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
        db.session.flush()

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

        response_data = combine_professional_data(user, profile)

        return APIResponse.success(
            data=response_data,
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


@professional_bp.route("/professionals/<int:profile_id>/verify", methods=["POST"])
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
