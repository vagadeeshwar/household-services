import os
from http import HTTPStatus

from flask import Blueprint, current_app, request
from marshmallow import ValidationError

from src.schemas.contact import contact_form_schema
from src.utils.api import APIResponse
from src.utils.notification import EmailTemplate, NotificationService

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/contact", methods=["POST"])
def submit_contact_form():
    """Handle contact form submissions"""
    try:
        # Validate request data
        data = contact_form_schema.load(request.get_json())

        # Send email notification
        admin_email = os.getenv("ADMIN_EMAIL", current_app.config["MAIL_USERNAME"])
        success = NotificationService.send_email(
            to=admin_email,
            subject=f"Contact Form: {data['subject']}",
            template=EmailTemplate.CONTACT_FORM,
            data={
                "name": data["name"],
                "email": data["email"],
                "subject": data["subject"],
                "message": data["message"],
            },
        )

        if not success:
            return APIResponse.error(
                "Failed to send contact form",
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "EmailError",
            )

        return APIResponse.success(
            message="Contact form submitted successfully",
            status_code=HTTPStatus.CREATED,
        )

    except ValidationError as err:
        return APIResponse.error(str(err.messages))
    except Exception as e:
        return APIResponse.error(
            f"Error processing contact form: {str(e)}",
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "ContactFormError",
        )
