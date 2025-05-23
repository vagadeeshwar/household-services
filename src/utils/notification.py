from flask import current_app, render_template
from flask_mail import Mail, Message
from typing import List, Optional, Dict, Any

mail = Mail()


class EmailTemplate:
    """Email template constants"""

    VERIFICATION_APPROVED = "emails/verification_approved.html"
    SERVICE_REQUEST_ASSIGNED = "emails/service_request_assigned.html"
    SERVICE_REQUEST_COMPLETED = "emails/service_request_completed.html"
    MONTHLY_REPORT = "emails/monthly_report.html"
    DAILY_REMINDER = "emails/daily_reminder.html"
    CONTACT_FORM = "emails/contact_form.html"


class NotificationService:
    @staticmethod
    def send_email(
        to: str,
        subject: str,
        template: str,
        data: Dict[str, Any],
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> bool:
        """Send an email using a template"""
        try:
            current_app.logger.info(f"Attempting to send email to {to}")
            current_app.logger.info(f"Template: {template}")
            current_app.logger.info(f"Template data: {data}")

            msg = Message(
                subject,
                sender=current_app.config["MAIL_DEFAULT_SENDER"],
                recipients=[to],
                cc=cc,
                bcc=bcc,
            )

            msg.html = render_template(template, **data)
            current_app.logger.info("Template rendered successfully")

            mail.send(msg)
            current_app.logger.info(f"Email sent successfully to {to}")
            return True

        except Exception as e:
            current_app.logger.error(f"Failed to send email: {str(e)}")
            current_app.logger.error("Exception details:", exc_info=True)
            return False

    @classmethod
    def send_verification_approved(cls, professional):
        """Send verification approval email"""
        return cls.send_email(
            to=professional.user.email,
            subject="Professional Verification Approved",
            template=EmailTemplate.VERIFICATION_APPROVED,
            data={
                "name": professional.user.full_name,
                "service": professional.service_type.name,
            },
        )

    @classmethod
    def send_service_request_notification(
        cls, service_request, template: str, subject: str
    ):
        """Send service request related notifications"""
        return cls.send_email(
            to=service_request.customer.user.email,
            subject=subject,
            template=template,
            data={
                "customer_name": service_request.customer.user.full_name,
                "service_name": service_request.service.name,
                "date": service_request.preferred_time.strftime("%Y-%m-%d %H:%M"),
                "professional_name": service_request.professional.user.full_name
                if service_request.professional
                else None,
                "request_id": service_request.id,
            },
        )

    @classmethod
    def send_daily_reminder(cls, professional, pending_requests):
        """Send daily reminder to professional"""
        return cls.send_email(
            to=professional.user.email,
            subject="Daily Service Requests Update",
            template=EmailTemplate.DAILY_REMINDER,
            data={
                "name": professional.user.full_name,
                "pending_requests": pending_requests,
            },
        )

    @classmethod
    def send_monthly_report(cls, user, report_data):
        """Send monthly activity report"""
        return cls.send_email(
            to=user.email,
            subject=f"Monthly Activity Report - {report_data['month']}",
            template=EmailTemplate.MONTHLY_REPORT,
            data=report_data,
        )
