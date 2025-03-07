from datetime import datetime, timedelta, timezone

from marshmallow import Schema, ValidationError, fields, validate, validates

from src.models import Service
from src.schemas.base import BaseSchema
from src.schemas.service import ServiceOutputSchema


class ServiceRequestInputSchema(Schema):
    """Schema for creating service requests"""

    service_id = fields.Int(required=True)
    preferred_time = fields.DateTime(required=True)
    description = fields.Str(validate=validate.Length(max=1000))

    @validates("preferred_time")
    def validate_preferred_time(self, value):
        """Validate preferred_time constraints"""
        now = datetime.now(timezone.utc)

        # Check if time is in the past
        if value <= now:
            raise ValidationError("Preferred time must be in the future")

        # Check if time is more than 7 days in the future
        max_future_date = now + timedelta(days=7)
        if value > max_future_date:
            raise ValidationError(
                "Cannot schedule requests more than 7 days in advance"
            )

        # Check if time is within business hours (9 AM to 6 PM)
        if value.hour < 9 or value.hour >= 18:
            raise ValidationError("Service can only be scheduled between 9 AM and 6 PM")

        # Get service duration and check if service can be completed by 6 PM
        service = Service.query.get(self.context.get("service_id"))
        if service:
            service_end_time = value + timedelta(minutes=service.estimated_time)
            end_time_limit = datetime.combine(
                value.date(), datetime.strptime("18:00", "%H:%M").time()
            )
            if service_end_time > end_time_limit:
                raise ValidationError(
                    "Service cannot be completed by 6 PM with the selected start time"
                )


class SimplifiedCustomerSchema(Schema):
    """Simplified customer schema for nested relationships"""

    id = fields.Int(attribute="id")  # This will be the customer profile id
    user = fields.Nested(lambda: SimplifiedUserSchema())


class SimplifiedProfessionalSchema(Schema):
    """Simplified professional schema for nested relationships"""

    id = fields.Int(attribute="id")  # This will be the professional profile id
    user = fields.Nested(lambda: SimplifiedUserSchema())
    is_verified = fields.Bool(required=True)
    average_rating = fields.Float()


class SimplifiedUserSchema(Schema):
    """Simplified user schema for nested relationships"""

    id = fields.Int(required=True)
    username = fields.Str(required=True)
    full_name = fields.Str(required=True)
    phone = fields.Str(required=True)


class ServiceRequestOutputSchema(Schema):
    """Schema for service request output with proper nested relationships"""

    id = fields.Int(required=True)
    service = fields.Nested(ServiceOutputSchema)
    customer = fields.Nested(SimplifiedCustomerSchema)
    professional = fields.Nested(SimplifiedProfessionalSchema, allow_none=True)
    date_of_request = fields.DateTime(required=True)
    preferred_time = fields.DateTime(required=True)
    status = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    date_of_assignment = fields.DateTime(allow_none=True)
    date_of_completion = fields.DateTime(allow_none=True)
    remarks = fields.Str(allow_none=True)


class ReviewOutputSchema(Schema):
    """Schema for review output data"""

    id = fields.Int(required=True)
    rating = fields.Int(required=True)
    comment = fields.Str(allow_none=True)
    created_at = fields.DateTime(required=True)
    is_reported = fields.Bool(required=True)
    report_reason = fields.Str(allow_none=True)
    service_request = fields.Nested(ServiceRequestOutputSchema)


class ReviewInputSchema(BaseSchema):
    """Schema for submitting reviews"""

    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str(validate=validate.Length(max=1000))


class TimeSlotSchema(Schema):
    """Schema for time slot information"""

    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=True)
    status = fields.Str(required=True)  # 'available', 'booked', 'completed'
    service_request = fields.Nested("ServiceRequestOutputSchema", allow_none=True)


class DayScheduleSchema(Schema):
    """Schema for daily schedule"""

    date = fields.Date(required=True)
    time_slots = fields.List(fields.Nested(TimeSlotSchema), required=True)
    total_slots = fields.Int(required=True)
    available_slots = fields.Int(required=True)
    booked_slots = fields.Int(required=True)


class CalendarViewSchema(Schema):
    """Schema for calendar view response"""

    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    days = fields.List(fields.Nested(DayScheduleSchema), required=True)
    total_bookings = fields.Int(required=True)
    available_days = fields.Int(required=True)


# Schema instances
service_request_input_schema = ServiceRequestInputSchema()
service_request_output_schema = ServiceRequestOutputSchema()
service_requests_output_schema = ServiceRequestOutputSchema(many=True)
review_output_schema = ReviewOutputSchema()
reviews_output_schema = ReviewOutputSchema(many=True)

calendar_view_schema = CalendarViewSchema()
