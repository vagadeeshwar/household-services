import csv
import os
import traceback
from datetime import datetime, timedelta, timezone

from celery.schedules import crontab

from src.celery_app import celery
from src.constants import REQUEST_STATUS_ASSIGNED, REQUEST_STATUS_COMPLETED
from src.models import ActivityLog, ProfessionalProfile, ServiceRequest, User
from src.utils.notification import NotificationService


def get_app():
    from src.app import create_app

    app = create_app()
    return app


@celery.task
def send_daily_reminders():
    """Send daily reminders to professionals with pending requests"""
    with get_app().app_context():
        try:
            # Get all active professionals
            professionals = (
                ProfessionalProfile.query.join(User)
                .filter(
                    User.is_active == True,  # noqa: E712
                    ProfessionalProfile.is_verified == True,  # noqa: E712
                )
                .all()
            )

            for professional in professionals:
                # Get pending and assigned requests
                pending_requests = ServiceRequest.query.filter(
                    ServiceRequest.professional_id == professional.id,
                    ServiceRequest.status == REQUEST_STATUS_ASSIGNED,
                    ServiceRequest.preferred_time >= datetime.now(timezone.utc),
                    ServiceRequest.preferred_time
                    <= datetime.now(timezone.utc) + timedelta(days=1),
                ).all()

                if pending_requests:
                    NotificationService.send_daily_reminder(
                        professional, pending_requests
                    )

            return {
                "status": "success",
                "message": f"Sent reminders to {len(professionals)} professionals",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


@celery.task
def generate_monthly_reports():
    """Generate and send monthly activity reports for all users"""
    with get_app().app_context():
        try:
            # Get all active users
            users = User.query.filter_by(is_active=True).all()
            month = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%B %Y")
            start_date = datetime.now(timezone.utc).replace(day=1) - timedelta(days=1)

            for user in users:
                report_data = {
                    "name": user.full_name,
                    "month": month,
                    "total_requests": 0,
                    "completed_requests": 0,
                    "average_rating": 0.0,
                    "recent_activities": [],
                }

                if user.role == "professional" and user.professional_profile:
                    # Get professional's statistics
                    requests = ServiceRequest.query.filter(
                        ServiceRequest.professional_id == user.professional_profile.id,
                        ServiceRequest.date_of_request >= start_date,
                    ).all()

                    report_data.update(
                        {
                            "total_requests": len(requests),
                            "completed_requests": sum(
                                1
                                for r in requests
                                if r.status == REQUEST_STATUS_COMPLETED
                            ),
                            "average_rating": user.professional_profile.average_rating
                            or 0.0,
                        }
                    )

                elif user.role == "customer" and user.customer_profile:
                    # Get customer's statistics
                    requests = ServiceRequest.query.filter(
                        ServiceRequest.customer_id == user.customer_profile.id,
                        ServiceRequest.date_of_request >= start_date,
                    ).all()

                    report_data.update(
                        {
                            "total_requests": len(requests),
                            "completed_requests": sum(
                                1
                                for r in requests
                                if r.status == REQUEST_STATUS_COMPLETED
                            ),
                        }
                    )

                # Get recent activities
                activities = (
                    ActivityLog.query.filter(
                        ActivityLog.user_id == user.id,
                        ActivityLog.created_at >= start_date,
                    )
                    .order_by(ActivityLog.created_at.desc())
                    .limit(5)
                    .all()
                )

                report_data["recent_activities"] = [
                    {
                        "description": activity.description,
                        "date": activity.created_at.strftime("%Y-%m-%d %H:%M"),
                    }
                    for activity in activities
                ]

                # Send report email
                NotificationService.send_monthly_report(user, report_data)

            return {
                "status": "success",
                "message": f"Generated reports for {len(users)} users",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


@celery.task(bind=True)
def generate_service_requests_csv(
    self, professional_id=None, start_date=None, end_date=None, user_email=None
):
    """Generate CSV export of service requests"""
    app = get_app()

    with app.app_context():
        try:
            self.update_state(state="STARTED", meta={"info": "Task starting"})

            # Build query
            query = ServiceRequest.query.filter_by(status=REQUEST_STATUS_COMPLETED)

            if professional_id:
                query = query.filter_by(professional_id=professional_id)
                # Verify professional exists
                professional = ProfessionalProfile.query.get(professional_id)
                if not professional:
                    raise ValueError(
                        f"Professional with ID {professional_id} not found"
                    )

            if start_date:
                query = query.filter(
                    ServiceRequest.date_of_request
                    >= datetime.strptime(start_date, "%Y-%m-%d")
                )
            if end_date:
                query = query.filter(
                    ServiceRequest.date_of_request
                    <= datetime.strptime(end_date, "%Y-%m-%d")
                )

            requests = query.all()

            if not requests:
                return {
                    "status": "success",
                    "message": "No completed service requests found for the given criteria",
                    "total_records": 0,
                }

            # Generate filename - now using timestamp only since it's admin export
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"service_requests_{timestamp}.csv"
            if professional_id:
                filename = f"service_requests_{professional_id}_{timestamp}.csv"

            filepath = os.path.join(app.root_path, "static/exports", filename)

            # Create directory if doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # Write CSV
            with open(filepath, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    [
                        "Request ID",
                        "Service",
                        "Customer Name",
                        "Professional Name",
                        "Date Requested",
                        "Date Completed",
                        "Status",
                        "Remarks",
                        "Rating",
                        "Review Comment",
                    ]
                )

                for request in requests:
                    review = request.review
                    writer.writerow(
                        [
                            request.id,
                            request.service.name,
                            request.customer.user.full_name,
                            request.professional.user.full_name
                            if request.professional
                            else "N/A",
                            request.date_of_request.strftime("%Y-%m-%d %H:%M"),
                            request.date_of_completion.strftime("%Y-%m-%d %H:%M")
                            if request.date_of_completion
                            else "N/A",
                            request.status,
                            request.remarks or "N/A",
                            review.rating if review else "N/A",
                            review.comment if review and review.comment else "N/A",
                        ]
                    )

            # Send notification
            if user_email:
                # Get the admin user's name from the email
                admin_user = User.query.filter_by(email=user_email).first()
                NotificationService.send_email(
                    to=user_email,
                    subject="Service Requests Export Complete",
                    template="emails/export_complete.html",
                    data={
                        "name": admin_user.full_name if admin_user else "Admin",
                        "filename": filename,
                        "total_records": len(requests),
                    },
                )

            return {
                "status": "success",
                "filename": filename,
                "total_records": len(requests),
                "professional_id": professional_id,  # Include in response if specific professional
                "message": f"Successfully exported {len(requests)} service requests",
            }

        except Exception as e:
            self.update_state(
                state="FAILURE",
                meta={
                    "exc_type": type(e).__name__,
                    "exc_message": str(e),
                    "traceback": traceback.format_exc(),
                },
            )
            raise


@celery.task
def send_account_status_notification(
    email, name, template, subject, additional_data=None
):
    """Send account status notification emails."""
    try:
        with get_app().app_context():
            # Create the data dictionary with name and any additional data
            data = {"name": name}
            if additional_data:
                data.update(additional_data)

            # Send the email
            result = NotificationService.send_email(
                to=email, subject=subject, template=template, data=data
            )
            print(f"Email sent to {email} using template {template}: {result}")
            return {"success": result, "email": email}
    except Exception as e:
        import traceback

        print(f"Error sending notification: {str(e)}")
        print(traceback.format_exc())
        return {"success": False, "error": str(e)}


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Send daily reminders at 6 PM every day
    sender.add_periodic_task(
        crontab(hour=18, minute=0), send_daily_reminders.s(), name="daily-reminders"
    )

    # Generate monthly reports on the 1st of every month at 1 AM
    sender.add_periodic_task(
        crontab(day_of_month=1, hour=1, minute=0),
        generate_monthly_reports.s(),
        name="monthly-reports",
    )
