# src/routes/export.py
import os
from http import HTTPStatus

from flask import Blueprint, current_app, request, send_from_directory
from marshmallow import ValidationError

from src.schemas.export import export_request_schema
from src.tasks import generate_service_requests_csv
from src.utils.api import APIResponse
from src.utils.auth import role_required, token_required

export_bp = Blueprint("export", __name__)


@export_bp.route("/exports/service-requests", methods=["POST"])
@token_required
@role_required("admin")
def trigger_export(current_user):
    """Trigger service requests export for professionals"""
    try:
        # Validate request data
        data = export_request_schema.load(request.get_json() or {})

        # Get professional_id from request if provided
        professional_id = data.get("professional_id")

        # Trigger async task
        task = generate_service_requests_csv.delay(
            professional_id=professional_id,
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            user_email=current_user.email,
        )

        return APIResponse.success(
            data={"task_id": task.id},
            message="Export task started successfully",
            status_code=HTTPStatus.ACCEPTED,
        )

    except ValidationError as err:
        return APIResponse.error(str(err.messages))
    except Exception as e:
        return APIResponse.error(
            f"Error triggering export: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "ExportError",
        )


@export_bp.route("/exports/status/<task_id>", methods=["GET"])
@token_required
@role_required("admin")
def check_export_status(current_user, task_id):
    """Check export task status"""
    try:
        task = generate_service_requests_csv.AsyncResult(task_id)

        if task.state == "PENDING":
            response = {"state": task.state, "status": "Export task is pending"}
        elif task.state == "SUCCESS":
            response = {
                "state": task.state,
                "status": "Export completed successfully",
                "result": task.result,
            }
        elif task.state == "FAILURE":
            response = {
                "state": task.state,
                "status": "Export failed",
                "error": str(task.info.get("error", "Unknown error")),
            }
        else:
            response = {"state": task.state, "status": "Export is in progress"}

        return APIResponse.success(data=response)

    except Exception as e:
        return APIResponse.error(
            f"Error checking export status: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "StatusCheckError",
        )


@export_bp.route("/exports/download/<filename>", methods=["GET"])
@token_required
@role_required("admin")
def download_export(current_user, filename):
    """Download exported CSV file"""
    try:
        exports_dir = os.path.join(current_app.root_path, "static/exports")
        return send_from_directory(
            exports_dir, filename, as_attachment=True, mimetype="text/csv"
        )
    except Exception as e:
        return APIResponse.error(
            f"Error downloading file: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "DownloadError",
        )
