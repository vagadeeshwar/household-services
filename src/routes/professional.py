import base64
import os
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from dateutil.relativedelta import relativedelta
from flask import Blueprint, current_app, request, send_from_directory
from marshmallow import ValidationError
from sqlalchemy import func

from src import db
from src.constants import (
    REQUEST_STATUS_ASSIGNED,
    REQUEST_STATUS_COMPLETED,
    USER_ROLE_PROFESSIONAL,
    ActivityLogActions,
)
from src.models import (
    ActivityLog,
    ProfessionalProfile,
    Review,
    Service,
    ServiceRequest,
    User,
)
from src.schemas.professional import (
    professional_output_schema,
    professional_query_schema,
    professional_register_schema,
    professionals_output_schema,
)
from src.schemas.request import reviews_output_schema
from src.schemas.user import block_user_schema
from src.tasks import send_account_status_notification
from src.utils.api import APIResponse
from src.utils.auth import role_required, token_required
from src.utils.cache import cache_, cache_invalidate
from src.utils.file import (
    UPLOAD_FOLDER,
    delete_verification_document,
    save_verification_document,
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
@cache_(timeout=300)
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
        params = professional_query_schema.load(request.args)
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

        # Get serialized data
        professionals_data = professionals_output_schema.dump(paginated.items)

        # Apply consistent field filtering for non-admin users
        if current_user.role != "admin":
            sensitive_fields = [
                "verification_documents",
                "created_at",
                "last_login",
            ]
            for prof in professionals_data:
                for field in sensitive_fields:
                    prof.pop(field, None)

        return APIResponse.success(
            data=professionals_data,
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
        profile = ProfessionalProfile.query.get(profile_id)
        if not profile:
            return APIResponse.error(
                "Professional not found", HTTPStatus.NOT_FOUND, "NotFound"
            )

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

        cache_invalidate()

        # Replace direct notification with Celery task
        send_account_status_notification.delay(
            profile.user.email,
            profile.user.full_name,
            "emails/verification_approved.html",
            "Professional Verification Approved",
            {"service": profile.service_type.name},
        )

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
        profile = ProfessionalProfile.query.get(profile_id)
        if not profile:
            return APIResponse.error(
                "Professional not found", HTTPStatus.NOT_FOUND, "NotFound"
            )
        if not profile.user.is_active:
            return APIResponse.error(
                "Professional is already blocked", HTTPStatus.CONFLICT, "AlreadyBlocked"
            )

        # Check for active service requests
        has_active_requests = (
            ServiceRequest.query.filter(
                ServiceRequest.professional_id == profile.id,
                ServiceRequest.status == REQUEST_STATUS_ASSIGNED,
            ).first()
            is not None
        )

        if has_active_requests:
            return APIResponse.error(
                "Cannot block professional with active service requests",
                HTTPStatus.CONFLICT,
                "ActiveRequestsExist",
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
        cache_invalidate()
        return APIResponse.success(message="Professional blocked successfully")
    except ValidationError as err:
        return APIResponse.error(str(err.messages))
    except Exception as e:
        return APIResponse.error(
            f"Error blocking professional: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@professional_bp.route("/professionals/<int:profile_id>/unblock", methods=["POST"])
@token_required
@role_required("admin")
def unblock_professional(current_user, profile_id):
    """Unblock a professional's account"""
    try:
        profile = ProfessionalProfile.query.get(profile_id)
        if not profile:
            return APIResponse.error(
                "Professional not found", HTTPStatus.NOT_FOUND, "NotFound"
            )

        if profile.user.is_active:
            return APIResponse.error(
                "Professional is already active", HTTPStatus.CONFLICT, "AlreadyActive"
            )

        # Only unblock if the professional is verified
        if not profile.is_verified:
            return APIResponse.error(
                "Cannot unblock unverified professional",
                HTTPStatus.BAD_REQUEST,
                "UnverifiedProfessional",
            )

        profile.user.is_active = True
        log = ActivityLog(
            user_id=current_user.id,
            entity_id=profile.user.id,
            action=ActivityLogActions.PROFESSIONAL_UNBLOCK,
            description=f"Unblocked professional {profile.user.full_name}",
        )
        db.session.add(log)
        db.session.commit()
        cache_invalidate()

        send_account_status_notification.delay(
            profile.user.email,
            profile.user.full_name,
            "emails/account_unblocked.html",
            "Account Unblocked",
        )

        return APIResponse.success(message="Professional unblocked successfully")
    except Exception as e:
        return APIResponse.error(
            f"Error unblocking professional: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DatabaseError",
        )


@professional_bp.route("/document", methods=["PUT"])
@token_required
@role_required("professional")
def update_verification_document(current_user):
    """Update professional's verification documents"""
    try:
        # Check for active service requests first
        has_active_requests = (
            ServiceRequest.query.filter(
                ServiceRequest.professional_id == current_user.professional_profile.id,
                ServiceRequest.status.in_([REQUEST_STATUS_ASSIGNED]),
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
        current_user.is_active = False

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.PROFESSIONAL_DOCUMENT_UPDATE,
            description=f"Updated verification documents for professional {current_user.username}",
        )
        db.session.add(log)
        db.session.commit()

        cache_invalidate()

        return APIResponse.success(
            data=professional_output_schema.dump(current_user),
            message="Verification document updated successfully. Awaiting verification.",
        )
    except Exception as e:
        # Clean up the newly uploaded file in case of error
        if "filename" in locals() and filename:
            delete_verification_document(filename)
        db.session.rollback()  # Added rollback in case of error
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
                ServiceRequest.status.in_([REQUEST_STATUS_ASSIGNED]),
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
        service = Service.query.get(data["service_type_id"])
        if not service:
            return APIResponse.error(
                "Service type not found", HTTPStatus.NOT_FOUND, "ServiceNotFound"
            )

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
        current_user.is_active = False

        log = ActivityLog(
            user_id=current_user.id,
            action=ActivityLogActions.PROFESSIONAL_SERVICE_UPDATE,
            entity_id=current_user.id,
            description=f"Updated service type for professional {current_user.username} from "
            f"{current_user.professional_profile.service_type.name} to {service.name}",
        )
        db.session.add(log)
        db.session.commit()

        cache_invalidate()

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


@professional_bp.route("/professionals/reviews", methods=["GET"])
@token_required
@role_required("professional")
@cache_(timeout=180)
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

        return APIResponse.success(
            data=reviews_output_schema.dump(paginated.items),
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


@professional_bp.route("/professionals/<int:profile_id>/document", methods=["GET"])
@token_required
@role_required("admin")
def download_verification_document(current_user, profile_id):
    """Download a professional's verification document securely.

    Only accessible by admins with proper authentication.
    Returns the document with appropriate headers for download.
    """
    try:
        # Get the professional profile
        profile = ProfessionalProfile.query.get(profile_id)

        if not profile:
            return APIResponse.error(
                "Professional not found", HTTPStatus.NOT_FOUND, "NotFound"
            )

        if not profile.verification_documents:
            return APIResponse.error(
                "No verification document found",
                HTTPStatus.NOT_FOUND,
                "DocumentNotFound",
            )

        # Check for document existence
        document_path = os.path.join(
            current_app.root_path, UPLOAD_FOLDER, profile.verification_documents
        )

        if not os.path.exists(document_path):
            return APIResponse.error(
                "Document file not found on server",
                HTTPStatus.NOT_FOUND,
                "FileNotFound",
            )

        # Get file extension to determine content type
        _, file_extension = os.path.splitext(profile.verification_documents)

        # Map common extensions to MIME types
        content_type = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
        }.get(file_extension.lower(), "application/octet-stream")

        # Get professional's name for the filename
        professional_user = User.query.get(profile.user_id)
        safe_name = "".join(
            c for c in professional_user.full_name if c.isalnum() or c in "._- "
        )

        # Log the download
        log = ActivityLog(
            user_id=current_user.id,
            entity_id=profile.id,
            action="document_download",
            description=f"Downloaded verification document for professional {professional_user.username}",
        )
        db.session.add(log)
        db.session.commit()

        # Return the file as an attachment with a proper filename
        download_name = f"verification_{safe_name}{file_extension}"

        return send_from_directory(
            os.path.dirname(document_path),
            os.path.basename(document_path),
            as_attachment=True,
            download_name=download_name,
            mimetype=content_type,
        )

    except Exception as e:
        current_app.logger.error(f"Error downloading document: {str(e)}")
        return APIResponse.error(
            f"Error downloading document: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DownloadError",
        )


@professional_bp.route("/my-document", methods=["GET"])
@token_required
@role_required("professional")
def download_own_verification_document(current_user):
    """Download your own verification document.

    Allows professionals to download their own verification document.
    Returns the document with appropriate headers for download.
    """
    try:
        # Ensure user has a professional profile
        if not current_user.professional_profile:
            return APIResponse.error(
                "Professional profile not found",
                HTTPStatus.NOT_FOUND,
                "ProfileNotFound",
            )

        # Check if document exists
        if not current_user.professional_profile.verification_documents:
            return APIResponse.error(
                "No verification document found",
                HTTPStatus.NOT_FOUND,
                "DocumentNotFound",
            )

        # Check for document existence on filesystem
        document_path = os.path.join(
            current_app.root_path,
            UPLOAD_FOLDER,
            current_user.professional_profile.verification_documents,
        )

        if not os.path.exists(document_path):
            return APIResponse.error(
                "Document file not found on server",
                HTTPStatus.NOT_FOUND,
                "FileNotFound",
            )

        # Get file extension to determine content type
        _, file_extension = os.path.splitext(
            current_user.professional_profile.verification_documents
        )

        # Map common extensions to MIME types
        content_type = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
        }.get(file_extension.lower(), "application/octet-stream")

        # Generate a safe filename
        safe_name = "".join(
            c for c in current_user.full_name if c.isalnum() or c in "._- "
        )

        # Log the download
        log = ActivityLog(
            user_id=current_user.id,
            entity_id=current_user.professional_profile.id,
            action="document_download",
            description=f"Professional {current_user.username} downloaded their own verification document",
        )
        db.session.add(log)
        db.session.commit()

        # Return the file as an attachment with a proper filename
        download_name = f"verification_{safe_name}{file_extension}"

        return send_from_directory(
            os.path.dirname(document_path),
            os.path.basename(document_path),
            as_attachment=True,
            download_name=download_name,
            mimetype=content_type,
        )

    except Exception as e:
        current_app.logger.error(f"Error downloading document: {str(e)}")
        return APIResponse.error(
            f"Error downloading document: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DownloadError",
        )


@professional_bp.route("/professionals/dashboard", methods=["GET"])
@token_required
@role_required("professional")
@cache_(timeout=120)
def get_professional_dashboard(current_user):
    """Get professional's dashboard statistics with trend data"""
    try:
        professional_id = current_user.professional_profile.id
        # Get time period from query params (default: last 30 days)
        period = request.args.get("period", "30d")  # Options: 7d, 30d, 90d, all
        # Calculate date range based on period
        today = datetime.now(timezone.utc)
        if period == "7d":
            start_date = today - timedelta(days=7)
        elif period == "30d":
            start_date = today - timedelta(days=30)
        elif period == "90d":
            start_date = today - timedelta(days=90)
        else:  # "all" - find earliest date
            earliest_request = (
                ServiceRequest.query.filter(
                    ServiceRequest.professional_id == professional_id,
                    ServiceRequest.status == REQUEST_STATUS_COMPLETED,
                )
                .order_by(ServiceRequest.date_of_completion.asc())
                .first()
            )

            if earliest_request and earliest_request.date_of_completion:
                start_date = earliest_request.date_of_completion
            else:
                # Fallback if no completed requests
                start_date = today - timedelta(days=365)  # Default to 1 year

        # Base query with optional date filtering
        completed_requests_query = ServiceRequest.query.filter(
            ServiceRequest.professional_id == professional_id,
            ServiceRequest.status == REQUEST_STATUS_COMPLETED,
        )
        if start_date:
            completed_requests_query = completed_requests_query.filter(
                ServiceRequest.date_of_completion >= start_date
            )
        # Core statistics
        stats = {
            "total_requests": ServiceRequest.query.filter_by(
                professional_id=professional_id
            ).count(),
            "completed_requests": completed_requests_query.count(),
            "active_requests": ServiceRequest.query.filter(
                ServiceRequest.professional_id == professional_id,
                ServiceRequest.status == REQUEST_STATUS_ASSIGNED,
            ).count(),
            "average_rating": db.session.query(func.avg(Review.rating))
            .select_from(Review)  # Explicitly define the starting point
            .join(
                ServiceRequest, ServiceRequest.id == Review.service_request_id
            )  # Explicit ON clause
            .filter(ServiceRequest.professional_id == professional_id)
            .scalar()
            or 0.0,
            "total_reviews": Review.query.join(
                ServiceRequest, ServiceRequest.id == Review.service_request_id
            )  # Explicit ON clause
            .filter(ServiceRequest.professional_id == professional_id)
            .count(),
            "reported_reviews": Review.query.join(
                ServiceRequest, ServiceRequest.id == Review.service_request_id
            )  # Explicit ON clause
            .filter(
                ServiceRequest.professional_id == professional_id,
                Review.is_reported == True,  # noqa: E712
            )
            .count(),
            # Profile information
            "service_type": current_user.professional_profile.service_type.name,
            "verification_status": "Verified"
            if current_user.professional_profile.is_verified
            else "Pending Verification",
        }

        # Add weekly trend data - requests completed per week
        weekly_trend = []
        if period == "all" or period == "90d":
            # For longer periods, show weekly data for past 12 weeks
            num_weeks = 12
        else:
            # For shorter periods, show daily data
            num_weeks = int(period[:-1]) // 7 or 1
        for i in range(num_weeks):
            end_date = today - timedelta(days=i * 7)
            start_date_week = end_date - timedelta(days=7)
            completed_count = ServiceRequest.query.filter(
                ServiceRequest.professional_id == professional_id,
                ServiceRequest.status == REQUEST_STATUS_COMPLETED,
                ServiceRequest.date_of_completion >= start_date_week,
                ServiceRequest.date_of_completion < end_date,
            ).count()
            weekly_trend.insert(
                0,
                {
                    "period": start_date_week.strftime("%Y-%m-%d"),
                    "completed": completed_count,
                },
            )
        stats["weekly_trend"] = weekly_trend

        # Add monthly rating trend
        monthly_ratings = []
        for i in range(3):  # Last 3 months
            end_date = today.replace(day=1) - relativedelta(months=i - 1)
            start_date_month = end_date - relativedelta(months=1)

            avg_rating = (
                db.session.query(func.avg(Review.rating))
                .select_from(Review)  # Explicitly define the starting point
                .join(
                    ServiceRequest, ServiceRequest.id == Review.service_request_id
                )  # Explicit ON clause
                .filter(
                    ServiceRequest.professional_id == professional_id,
                    Review.created_at >= start_date_month,
                    Review.created_at < end_date,
                )
                .scalar()
                or 0
            )

            month_label = start_date_month.strftime("%B %Y")  # e.g., "February 2025"

            monthly_ratings.insert(
                0,
                {
                    "month": month_label,
                    "rating": round(float(avg_rating), 1),
                },
            )
        stats["monthly_ratings"] = monthly_ratings

        # Add month-over-month comparison
        current_month_start = today.replace(day=1)
        prev_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        current_month_requests = ServiceRequest.query.filter(
            ServiceRequest.professional_id == professional_id,
            ServiceRequest.status == REQUEST_STATUS_COMPLETED,
            ServiceRequest.date_of_completion >= current_month_start,
        ).count()
        prev_month_requests = ServiceRequest.query.filter(
            ServiceRequest.professional_id == professional_id,
            ServiceRequest.status == REQUEST_STATUS_COMPLETED,
            ServiceRequest.date_of_completion >= prev_month_start,
            ServiceRequest.date_of_completion < current_month_start,
        ).count()
        # Calculate month-over-month changes
        if prev_month_requests > 0:
            requests_change_percent = round(
                ((current_month_requests - prev_month_requests) / prev_month_requests)
                * 100,
                1,
            )
        else:
            requests_change_percent = 100 if current_month_requests > 0 else 0
        stats["monthly_comparison"] = {
            "current_month": current_month_start.strftime("%B %Y"),
            "current_month_requests": current_month_requests,
            "prev_month_requests": prev_month_requests,
            "change_percent": requests_change_percent,
        }
        # Get top 5 services by count
        if start_date:
            top_services_query = (
                db.session.query(
                    ServiceRequest.service_id,
                    Service.name.label("service_name"),
                    func.count().label("count"),
                )
                .select_from(ServiceRequest)  # Explicitly define starting point
                .join(
                    Service, ServiceRequest.service_id == Service.id
                )  # Explicit ON clause
                .filter(
                    ServiceRequest.professional_id == professional_id,
                    ServiceRequest.status == REQUEST_STATUS_COMPLETED,
                    ServiceRequest.date_of_completion >= start_date,
                )
                .group_by(ServiceRequest.service_id, Service.name)
                .order_by(func.count().desc())
                .limit(5)
            )
            stats["top_services"] = [
                {"service_name": row.service_name, "count": row.count}
                for row in top_services_query.all()
            ]
        # Add busiest days analysis
        if start_date:
            # Analyze busiest days of the week
            busiest_days_query = (
                db.session.query(
                    func.extract("dow", ServiceRequest.date_of_completion).label(
                        "day_of_week"
                    ),
                    func.count().label("count"),
                )
                .select_from(ServiceRequest)  # Explicitly define starting point
                .filter(
                    ServiceRequest.professional_id == professional_id,
                    ServiceRequest.status == REQUEST_STATUS_COMPLETED,
                    ServiceRequest.date_of_completion >= start_date,
                )
                .group_by("day_of_week")
                .order_by(func.count().desc())
            )
            day_names = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            busiest_days = []
            for row in busiest_days_query.all():
                # Adjust based on database's day numbering (some start at 0, some at 1)
                day_index = int(row.day_of_week)
                # Adjust for PostgreSQL's Sunday=0 or MySQL's Sunday=1
                day_name = (
                    day_names[6] if day_index == 0 else day_names[day_index - 1]
                )  # If Sunday is 0
                busiest_days.append(
                    {
                        "day": day_name,
                        "count": row.count,
                        "percentage": round(
                            (row.count / stats["completed_requests"]) * 100
                            if stats["completed_requests"] > 0
                            else 0,
                            1,
                        ),
                    }
                )
            # Analyze busiest hours
            busiest_hours_query = (
                db.session.query(
                    func.extract("hour", ServiceRequest.date_of_completion).label(
                        "hour"
                    ),
                    func.count().label("count"),
                )
                .select_from(ServiceRequest)  # Explicitly define starting point
                .filter(
                    ServiceRequest.professional_id == professional_id,
                    ServiceRequest.status == REQUEST_STATUS_COMPLETED,
                    ServiceRequest.date_of_completion >= start_date,
                )
                .group_by("hour")
                .order_by(func.count().desc())
            )
            busiest_hours = [
                {
                    "hour": f"{int(row.hour)}:00 - {int(row.hour)}:59",
                    "count": row.count,
                    "percentage": round(
                        (row.count / stats["completed_requests"]) * 100
                        if stats["completed_requests"] > 0
                        else 0,
                        1,
                    ),
                }
                for row in busiest_hours_query.all()
            ]
            stats["activity_patterns"] = {
                "busiest_days": busiest_days,
                "busiest_hours": busiest_hours,
            }
        # Add customer satisfaction trends
        if start_date:
            # Get rating trends over time (grouped by week)
            rating_trends_query = (
                db.session.query(
                    func.strftime("%Y-%W", Review.created_at).label("week_str"),
                    func.avg(Review.rating).label("avg_rating"),
                    func.count().label("review_count"),
                )
                .select_from(Review)  # Explicitly define the starting point
                .join(
                    ServiceRequest, ServiceRequest.id == Review.service_request_id
                )  # Explicit ON clause
                .filter(
                    ServiceRequest.professional_id == professional_id,
                    Review.created_at >= start_date,
                )
                .group_by("week_str")
                .order_by("week_str")
            )
            rating_trends = []
            for row in rating_trends_query.all():
                # Parse year and week from the string
                try:
                    year, week = map(int, row.week_str.split("-"))
                    # Create a date object for the first day of the week
                    # This is a simple approximation - Jan 1 + week_number*7
                    date_obj = datetime.strptime(f"{year}-01-01", "%Y-%m-%d")
                    delta_days = (week) * 7
                    week_date = date_obj + timedelta(days=delta_days)
                    period = week_date.strftime("%Y-%m-%d")
                except (ValueError, AttributeError):
                    # Fallback if parsing fails
                    period = f"{row.week_str}"
                rating_trends.append(
                    {
                        "period": period,
                        "average_rating": round(float(row.avg_rating or 0), 1),
                        "review_count": row.review_count,
                    }
                )
            # Get rating distribution (1-5 stars)
            rating_distribution_query = (
                db.session.query(Review.rating, func.count().label("count"))
                .select_from(Review)  # Explicitly define the starting point
                .join(
                    ServiceRequest, ServiceRequest.id == Review.service_request_id
                )  # Explicit ON clause
                .filter(
                    ServiceRequest.professional_id == professional_id,
                    Review.created_at >= start_date,
                )
                .group_by(Review.rating)
                .order_by(Review.rating)
            )
            rating_distribution = [
                {
                    "rating": row.rating,
                    "count": row.count,
                    "percentage": round(
                        (row.count / stats["total_reviews"]) * 100
                        if stats["total_reviews"] > 0
                        else 0,
                        1,
                    ),
                }
                for row in rating_distribution_query.all()
            ]
            # Ensure all ratings 1-5 are represented
            existing_ratings = {item["rating"] for item in rating_distribution}
            for rating in range(1, 6):
                if rating not in existing_ratings:
                    rating_distribution.append(
                        {"rating": rating, "count": 0, "percentage": 0}
                    )
            # Sort by rating
            rating_distribution.sort(key=lambda x: x["rating"])
            # Count positive vs negative reviews
            positive_reviews_count = (
                db.session.query(func.count())
                .select_from(Review)  # Explicitly define the starting point
                .join(
                    ServiceRequest, ServiceRequest.id == Review.service_request_id
                )  # Explicit ON clause
                .filter(
                    ServiceRequest.professional_id == professional_id,
                    Review.created_at >= start_date,
                    Review.rating >= 4,
                )
                .scalar()
                or 0
            )
            negative_reviews_count = (
                db.session.query(func.count())
                .select_from(Review)  # Explicitly define the starting point
                .join(
                    ServiceRequest, ServiceRequest.id == Review.service_request_id
                )  # Explicit ON clause
                .filter(
                    ServiceRequest.professional_id == professional_id,
                    Review.created_at >= start_date,
                    Review.rating <= 2,
                )
                .scalar()
                or 0
            )
            stats["satisfaction_analysis"] = {
                "rating_trends": rating_trends,
                "rating_distribution": rating_distribution,
                "positive_reviews_count": positive_reviews_count,
                "negative_reviews_count": negative_reviews_count,
                "positive_percentage": round(
                    (positive_reviews_count / stats["total_reviews"]) * 100
                    if stats["total_reviews"] > 0
                    else 0,
                    1,
                ),
                "negative_percentage": round(
                    (negative_reviews_count / stats["total_reviews"]) * 100
                    if stats["total_reviews"] > 0
                    else 0,
                    1,
                ),
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
