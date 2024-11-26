from marshmallow import fields, validate, Schema

from src.schemas.base import BaseSchema
from src.schemas.service import ServiceOutputSchema
from src.schemas.customer import CustomerOutputSchema
from src.schemas.professional import ProfessionalOutputSchema


class ServiceRequestInputSchema(BaseSchema):
    service_id = fields.Int(required=True)
    preferred_time = fields.Str()
    description = fields.Str(validate=validate.Length(max=1000))


class ServiceRequestOutputSchema(Schema):
    id = fields.Int(required=True)
    service = fields.Nested(ServiceOutputSchema, dump_only=True)
    customer = fields.Nested(CustomerOutputSchema, dump_only=True)
    professional = fields.Nested(
        ProfessionalOutputSchema, dump_only=True, allow_none=True
    )
    date_of_request = fields.DateTime(required=True)
    preferred_time = fields.Str(allow_none=True)
    status = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    date_of_assignment = fields.DateTime(allow_none=True)
    date_of_completion = fields.DateTime(allow_none=True)
    remarks = fields.Str(allow_none=True)


class ReviewInputSchema(BaseSchema):
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str(validate=validate.Length(max=1000))


class ReviewOutputSchema(Schema):
    """Schema for review output data"""

    id = fields.Int(required=True)
    rating = fields.Int(required=True)
    comment = fields.Str(allow_none=True)
    created_at = fields.DateTime(required=True)
    is_reported = fields.Bool(required=True)
    report_reason = fields.Str(allow_none=True)
    service_request = fields.Nested(ServiceOutputSchema)


service_request_input_schema = ServiceRequestInputSchema()
service_request_output_schema = ServiceRequestOutputSchema()
service_requests_output_schema = ServiceRequestOutputSchema(many=True)
review_output_schema = ReviewOutputSchema()
reviews_output_schema = ReviewOutputSchema(many=True)
